import json
from confluent_kafka import Consumer, KafkaError
import datetime

from app import insert_into_database, app


# Kafka configuration for consuming messages
kafka_config = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'flask-kafka-consumer',
    'auto.offset.reset': 'smallest'
}

app.app_context().push()

consumer = Consumer(kafka_config)

# Kafka consumer
consumer.subscribe(['webhook_event'])

try:
    

    # Consume all available messages from the 'webhook_event' topic
    while True:
        msg = consumer.poll(1000.0)

        if msg is None:
            break

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
            event_name = json_data.get('event')

            with app.app_context():
                insert_into_database(event_id, event_name, json_data)

        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")

finally:
    # Close down consumer to commit final offsets.
    consumer.close()