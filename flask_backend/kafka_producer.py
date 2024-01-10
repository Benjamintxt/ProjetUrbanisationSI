# kafka_producer.py
import json
from confluent_kafka import Producer

# Kafka configuration
kafka_config = {
    'bootstrap.servers': 'localhost:9092',
    'client.id': 'flask-kafka-producer'
}

# Create Kafka producer
producer = Producer(kafka_config)

# Kafka topic for events
kafka_topic = 'webhook_event'

# Kafka producer function
def produce_to_kafka(event_id, event_name, json_data):
    kafka_events = {'eventId': event_id, 'event': event_name, 'data': json_data}
    producer.produce(kafka_topic, json.dumps(kafka_events))
    producer.flush()
