import json
from confluent_kafka import Consumer, KafkaError

# Kafka configuration for consuming messages
kafka_consumer_config = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'flask-kafka-consumer',
    'auto.offset.reset': 'earliest'
}

# Kafka consumer
consumer = Consumer(kafka_consumer_config)

# Subscribe to Kafka topic
consumer.subscribe(['webhook_events'])

while True:
    msg = consumer.poll(1.0)  # Poll for messages, timeout 1 second

    if msg is None:
        continue
    if msg.error():
        if msg.error().code() == KafkaError._PARTITION_EOF:
            continue
        else:
            print(msg.error())
            break

    try:
        # Decode JSON data
        json_data = json.loads(msg.value().decode('utf-8'))

        # Extract eventId
        event_id = json_data.get('eventId')

        # Process the message (store it, print it, etc.)
        print(f'Received message: eventId={event_id}, data={json_data}')

        # Store or process the JSON data and eventId as needed
        # Example: store_data_in_database(event_id, json_data)

    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")