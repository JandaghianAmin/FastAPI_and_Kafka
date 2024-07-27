

Prerequisites
Python 3.8+
Kafka Broker (e.g., local installation or Docker)
Kafka Python Client Libraries (confluent-kafka for producer and consumer)

# Step 1: Setting Up Kafka
First, you need a running Kafka broker. You can use Docker to quickly set up a Kafka broker.

Docker Compose File (docker-compose.yml):
```
version: '3.1'
services:
  zookeeper:
    image: 'confluentinc/cp-zookeeper:latest'
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
      ZOOKEEPER_TICK_TIME: 2000

  kafka:
    image: 'confluentinc/cp-kafka:latest'
    depends_on:
      - zookeeper
    ports:
      - 9092:9092
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://localhost:9092
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1

```

Run Kafka using Docker Compose:

```
docker-compose up -d

```

# Step 2: Installing Required Libraries
Install FastAPI, Uvicorn (ASGI server), and Confluent Kafka Python library.
```
pip install fastapi uvicorn confluent-kafka
```

# Step 3: Creating the FastAPI Application
We'll create a FastAPI application with an endpoint to produce messages to Kafka and a background task to consume messages from Kafka.

1. Producer Endpoint

```   
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from confluent_kafka import Producer
import uvicorn

app = FastAPI()


producer_conf = {
    'bootstrap.servers': 'localhost:9092'
}

producer = Producer(producer_conf)

class Message(BaseModel):
    key: str
    value: str

@app.post("/produce/")
async def produce_message(message: Message):
    try:
        producer.produce('my_topic', key=message.key.encode('utf-8'), value=message.value.encode('utf-8'))
        producer.flush()
        return {"status": "Message produced successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
  ```


2. Consumer Background Task
Add a background task to consume messages.


```
import asyncio
from confluent_kafka import Consumer, KafkaException


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
```

# Step 4: Running the Application
To run the application, use:


```
python consumer.py
python producer.py
```


