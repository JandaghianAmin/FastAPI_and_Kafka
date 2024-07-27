from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from confluent_kafka import Producer
import uvicorn
from datetime import datetime

app = FastAPI()

@app.middleware("http")
async def log_request_details(request: Request, call_next):
    method_name = request.method
    path = request.url.path
    with open("request_log.txt", mode="a") as reqfile:
        content = f"Method: {method_name}, Path: {path}, Received at: {datetime.now()}\n"
        reqfile.write(content)
    
    response = await call_next(request)
    return response




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
