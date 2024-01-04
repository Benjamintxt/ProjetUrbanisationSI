from flask_sqlalchemy import SQLAlchemy
import json
from flask import Flask, request, jsonify, current_app
from flask_cors import CORS
from confluent_kafka import Producer
from flask_socketio import SocketIO
from kafka_consumer import get_kafka_events
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

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///events.db'
db = SQLAlchemy(app)

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    eventId = db.Column(db.String(255), unique=True, nullable=False)
    eventName = db.Column(db.String(255), nullable=False)
    tickets = db.relationship('Ticket', backref='event', lazy=True)

class Ticket(db.Model):
    id = db.Column(db.String(255), primary_key=True)
    eventId = db.Column(db.String(255), db.ForeignKey('event.eventId'), nullable=False)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(datetime.timezone.utc))  # Updated timestamp field
    data = db.Column(db.JSON, nullable=False)


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
        event_name = json_data.get('details', {}).get('ticket', {}).get('event')

        # Save event to the database
        existing_event = Event.query.filter_by(eventId=event_id).first()

        if not existing_event:
            new_event = Event(eventId=event_id, eventName=event_name)
            db.session.add(new_event)
            db.session.commit()
        
        existing_ticket = Ticket.query.get(json_data['details']['ticket']['number'])

        # If the ticket doesn't exist, create a new one and associate it with the existing or newly created event
        if not existing_ticket:
            new_ticket = Ticket(
                id=json_data['details']['ticket']['number'],
                eventId=event_id,
                timestamp=datetime.datetime.utcnow()
                         + datetime.timedelta(hours=1),
                data=json_data
            )
            db.session.add(new_ticket)
            db.session.commit()

        # Send relevant data, including eventId, to Kafka
        producer.produce('webhook_events', json.dumps({'eventId': event_id, 'event': event_name, 'data': json_data}))

        # Emit the event to Socket.IO clients
        socketio.emit('webhook_events', {'eventId': event_id, 'event': event_name, 'data': json_data})

        return jsonify({'message': 'Webhook data saved and sent to Kafka successfully'}), 200

    except ValueError as e:
        return jsonify({'error': str(e)}), 401

@app.route('/events', methods=['GET'])
def get_events():
    try:
        # Fetch events from the database
        events = Event.query.all()

        # Serialize the events
        serialized_events = [{'eventId': event.eventId, 'eventName': event.eventName} for event in events]

        return jsonify({'events': serialized_events}), 200

    except Exception as e:
        print(f"Error fetching events: {str(e)}")
        return jsonify({'error': 'Internal Server Error'}), 500

@app.route('/event-sales-count/<event_id>', methods=['GET'])
def get_event_sales_count(event_id):
    try:
        # Fetch the count of tickets for the specified event from SQLite
        sales_count = Ticket.query.filter_by(eventId=event_id).count()

        return jsonify({'event_sales_count': sales_count}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/event-ticket-sales/<event_id>', methods=['GET'])
def get_event_ticket_sales(event_id):
    try:
        # Fetch timestamp and eventId from tickets for the specified event
        ticket_data = Ticket.query.filter_by(eventId=event_id).with_entities(Ticket.timestamp).all()

        # Serialize the timestamp data
        serialized_data = [str(timestamp[0].isoformat()) for timestamp in ticket_data]

        return jsonify({'event_ticket_sales': serialized_data}), 200

    except Exception as e:
        print(f"Error fetching event ticket sales: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':

    with app.app_context():
        # Create tables if they do not exist
        db.create_all()
    
    # Use Socket.IO's run method instead of app.run
    socketio.run(app, debug=True)