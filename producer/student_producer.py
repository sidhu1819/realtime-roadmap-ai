import os
from confluent_kafka import Producer
import json
import time
import random

conf = {
    'bootstrap.servers': os.getenv("KAFKA_BOOTSTRAP"),
    'security.protocol': 'SASL_SSL',
    'sasl.mechanisms': 'PLAIN',
    'sasl.username': os.getenv("KAFKA_API_KEY"),
    'sasl.password': os.getenv("KAFKA_API_SECRET")
}

producer = Producer(conf)

topic = "student_progress"
skills = ["Python", "Pandas", "SQL", "Machine Learning"]

print("🚀 Kafka Producer Started...")

while True:
    event = {
        "student_id": 101,
        "skill": random.choice(skills),
        "progress": random.randint(10, 100)
    }

    producer.produce(topic=topic, value=json.dumps(event))
    producer.flush()
    time.sleep(2)
