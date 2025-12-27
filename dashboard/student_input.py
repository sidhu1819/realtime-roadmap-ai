import os
import json
import streamlit as st
from confluent_kafka import Producer

st.set_page_config(page_title="Student Learning Portal", layout="centered")
st.title("🎓 Student Learning Portal")

# Kafka Producer Config
conf = {
    'bootstrap.servers': os.getenv("KAFKA_BOOTSTRAP"),
    'security.protocol': 'SASL_SSL',
    'sasl.mechanisms': 'PLAIN',
    'sasl.username': os.getenv("KAFKA_API_KEY"),
    'sasl.password': os.getenv("KAFKA_API_SECRET")
}

producer = Producer(conf)

# ---- Student Input Form ----
with st.form("learning_form"):
    student_id = st.number_input("Student ID", min_value=1, value=101)
    skill = st.selectbox("Select Skill", ["Python", "SQL", "Pandas", "Machine Learning"])
    progress = st.slider("Completion Progress (%)", 0, 100, 30)
    submit = st.form_submit_button("Submit Progress")

if submit:
    event = {
        "student_id": student_id,
        "skill": skill,
        "progress": progress
    }

    producer.produce(
        topic="student_progress",
        value=json.dumps(event)
    )
    producer.flush()

    st.success("✅ Progress submitted successfully!")
