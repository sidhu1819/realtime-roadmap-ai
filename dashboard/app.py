import os
import json
import pandas as pd
import streamlit as st
from confluent_kafka import Producer, Consumer

# ---------- Page Setup ----------
st.set_page_config(page_title="AI Learning Roadmap", layout="wide")
st.title("🎓 AI-Powered Learning Roadmap Platform")
st.caption("Real-time personalized learning guidance using AI & streaming data")

# ---------- Kafka Config ----------
conf = {
    'bootstrap.servers': os.getenv("KAFKA_BOOTSTRAP"),
    'security.protocol': 'SASL_SSL',
    'sasl.mechanisms': 'PLAIN',
    'sasl.username': os.getenv("KAFKA_API_KEY"),
    'sasl.password': os.getenv("KAFKA_API_SECRET"),
}

# ---------- Kafka Producer ----------
producer = Producer(conf)

# ---------- Kafka Consumer ----------
@st.cache_resource
def init_consumer():
    c = Consumer({
        **conf,
        'group.id': 'dashboard-consumer-group',
        'auto.offset.reset': 'latest'
    })
    c.subscribe(['roadmap_updates'])
    return c

consumer = init_consumer()

# ---------- Session State ----------
if "history" not in st.session_state:
    st.session_state.history = []

# ===============================
# STUDENT INPUT SECTION
# ===============================
st.subheader("📥 Student Learning Progress")

with st.form("student_form"):
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

    producer.produce("student_progress", json.dumps(event))
    producer.flush()

    st.success("✅ Progress submitted! AI is analyzing...")

# ===============================
# AI OUTPUT SECTION
# ===============================
st.divider()
st.subheader("🧠 AI Recommendation")

msg = consumer.poll(0.5)

if msg and not msg.error():
    data = json.loads(msg.value().decode())
    st.session_state.history.append(data)

if st.session_state.history:
    latest = st.session_state.history[-1]

    st.success(
        f"📌 Skill: {latest['skill']} | "
        f"Progress: {latest['progress']}% | "
        f"Next Step: **{latest['next_step']}**"
    )

    df = pd.DataFrame(st.session_state.history)
    st.subheader("📊 Recommendation History")
    st.dataframe(df, use_container_width=True)
else:
    st.info("Waiting for AI recommendations...")
