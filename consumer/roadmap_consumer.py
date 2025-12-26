import os
import json
import joblib
from confluent_kafka import Consumer, Producer

# 🔹 Load ML artifacts (safe paths)
model = joblib.load("ml/roadmap_model.pkl")
skill_encoder = joblib.load("ml/skill_encoder.pkl")
label_encoder = joblib.load("ml/label_encoder.pkl")

# 🔐 Secure Confluent Cloud Configuration
conf = {
    'bootstrap.servers': os.getenv("KAFKA_BOOTSTRAP"),
    'security.protocol': 'SASL_SSL',
    'sasl.mechanisms': 'PLAIN',
    'sasl.username': os.getenv("KAFKA_API_KEY"),
    'sasl.password': os.getenv("KAFKA_API_SECRET"),
    'group.id': 'roadmap-consumer-group',
    'auto.offset.reset': 'earliest',
    'enable.auto.commit': True
}

consumer = Consumer(conf)
producer = Producer(conf)

consumer.subscribe(['student_progress'])

print("📡 Roadmap Consumer Started...")

def generate_roadmap_decision(event):
    # Validate input
    if not isinstance(event, dict):
        print("⚠️ Invalid event format, expected dict")
        return "Revise Basics"

    skill = event.get("skill")
    progress = event.get("progress")

    if skill is None or progress is None:
        print(f"⚠️ Missing keys in event: {event}")
        return "Revise Basics"

    # Ensure progress is numeric
    try:
        progress = float(progress)
    except Exception:
        print(f"⚠️ Invalid progress value: {progress}")
        return "Revise Basics"

    # Handle unseen skills (case-insensitive match first)
    classes = list(skill_encoder.classes_)
    matched_skill = None
    for c in classes:
        if c.lower() == str(skill).lower():
            matched_skill = c
            break

    if matched_skill is None:
        print(f"⚠️ Unknown skill received: {skill}")
        return "Revise Basics"

    skill_encoded = skill_encoder.transform([matched_skill])[0]

    try:
        prediction = model.predict([[skill_encoded, progress]])
        decision = label_encoder.inverse_transform(prediction)[0]
        return decision
    except Exception as e:
        print(f"⚠️ Prediction failed: {e}")
        return "Revise Basics"

try:
    while True:
        msg = consumer.poll(1.0)

        if msg is None:
            continue
        if msg.error():
            print("Consumer error:", msg.error())
            continue

        event = json.loads(msg.value().decode())
        decision = generate_roadmap_decision(event)

        roadmap_update = {
            "student_id": event["student_id"],
            "skill": event["skill"],
            "progress": event["progress"],
            "next_step": decision
        }

        producer.produce(
            topic='roadmap_updates',
            value=json.dumps(roadmap_update)
        )
        producer.flush()

        print("🧠 Roadmap Update:", roadmap_update)

except KeyboardInterrupt:
    print("🛑 Shutting down consumer...")

finally:
    consumer.close()
