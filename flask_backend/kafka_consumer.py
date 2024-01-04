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

def get_kafka_events():
    try:
        kafka_events = []

        # Consume all available messages from the 'webhook_events' topic
        while True:
            msg = consumer.poll(1.0)

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

                # Append the event to the list
                kafka_events.append({'eventId': event_id, 'event': event_name, 'data': json_data})

            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}")

        return kafka_events

    except Exception as e:
        print(f'Error fetching Kafka events: {str(e)}')
        return []

if __name__ == '__main__':
    
    kafka_events = get_kafka_events()
    print("Kafka events:", kafka_events)