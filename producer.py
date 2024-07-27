from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from confluent_kafka import Producer
import uvicorn

app = FastAPI()

# Kafka producer configuration
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
