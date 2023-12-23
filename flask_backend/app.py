import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from confluent_kafka import Producer
from flask_socketio import SocketIO
import hmac
import datetime

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
socketio = SocketIO(app, cors_allowed_origins="*")

# Replace with your actual secret
secret = b"GoofyKey"

# Kafka configuration
kafka_config = {
    'bootstrap.servers': 'localhost:9092',
    'client.id': 'flask-kafka-producer'
}

# Create Kafka producer
producer = Producer(kafka_config)

def validate_signature(request):
    try:
        # Get the signature from the headers
        signature_header = request.headers.get('Petzi-Signature')

        # Split the signature into parts
        signature_parts = dict(part.split("=") for part in signature_header.split(","))

        # Prepare the signed body string
        body_to_sign = f'{signature_parts["t"]}.{request.data.decode("utf-8")}'

        # Compute the expected signature
        expected_signature = hmac.new(secret, body_to_sign.encode(), "sha256").hexdigest()

        # Compare the signatures
        if not hmac.compare_digest(expected_signature, signature_parts["v1"]):
            raise ValueError("Invalid signature")

        # Reject old messages
        time_delta = datetime.datetime.utcnow() - datetime.datetime.fromtimestamp(int(signature_parts["t"]))
        print(f'Time Delta: {time_delta}')
        if time_delta.total_seconds() > 30:
            raise ValueError("Expired signature")
        
    except Exception as e:
        raise ValueError(f"Signature validation failed: {str(e)}")

@app.route('/webhook', methods=['POST'])
def webhook_handler():
    try:
        # Validate the signature
        validate_signature(request)

        # Get the JSON data from the request
        json_data = request.get_json()

        event_id = json_data.get('details', {}).get('ticket', {}).get('eventId')

        # Send relevant data, including eventId, to Kafka
        producer.produce('webhook_events', json.dumps({'eventId': event_id, 'data': json_data}))

        # Emit the event to Socket.IO clients
        socketio.emit('webhook_events', json.dumps({'eventId': event_id, 'data': json_data}))

        return jsonify({'message': 'Webhook data saved and sent to Kafka successfully'}), 200

    except ValueError as e:
        return jsonify({'error': str(e)}), 401  # Unauthorized

if __name__ == '__main__':
    # Use Socket.IO's run method instead of app.run
    socketio.run(app, debug=True)
