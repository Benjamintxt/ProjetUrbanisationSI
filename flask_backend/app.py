import json
from flask import Flask, request, jsonify
from confluent_kafka import Producer

app = Flask(__name__)

# Kafka configuration
kafka_config = {
    'bootstrap.servers': 'localhost:9092',
    'client.id': 'flask-kafka-producer'
}

# Create Kafka producer
producer = Producer(kafka_config)

@app.route('/webhook', methods=['POST'])
def webhook_handler():
    try:
        # Get the JSON data from the request
        json_data = request.get_json()

        # Send the JSON data to Kafka topic
        producer.produce('webhook_events', json.dumps(json_data))

        """ Save the JSON data to a file (you can customize the filename and path)
        with open('webhook_data.json', 'w') as file:
            file.write(json.dumps(json_data, indent=2))  # Convert to JSON string with indentation"""

        return jsonify({'message': 'Webhook data saved and sent to Kafka successfully'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
