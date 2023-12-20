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

    # Process the message (store it, print it, etc.)
    print('Received message: {}'.format(msg.value().decode('utf-8')))
