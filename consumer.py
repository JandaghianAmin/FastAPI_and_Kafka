import asyncio
from confluent_kafka import Consumer, KafkaException

# Kafka consumer configuration
consumer_conf = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'my_group',
    'auto.offset.reset': 'earliest'
}

consumer = Consumer(consumer_conf)

async def consume_messages():
    consumer.subscribe(['my_topic'])
    try:
        while True:
            msg = consumer.poll(1.0)  # Poll every second
            if msg is None:
                await asyncio.sleep(1)
                continue
            if msg.error():
                print(f"Consumer error: {msg.error()}")
                continue
            print(f"Consumed message: {msg.key().decode('utf-8')}: {msg.value().decode('utf-8')}")
            await asyncio.sleep(0.1)  # Yield control to the event loop
    except KafkaException as e:
        print(f"Kafka exception: {e}")
    finally:
        consumer.close()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(consume_messages())
