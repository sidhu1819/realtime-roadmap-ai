import os
import json
import pandas as pd
import streamlit as st
from confluent_kafka import Consumer

# ---------- Streamlit Page ----------
st.set_page_config(page_title="Real-Time Learning Roadmap", layout="wide")
st.title("📊 Real-Time Engineering Roadmap Simulator")

# ---------- Kafka Config ----------
conf = {
    'bootstrap.servers': os.getenv("KAFKA_BOOTSTRAP"),
    'security.protocol': 'SASL_SSL',
    'sasl.mechanisms': 'PLAIN',
    'sasl.username': os.getenv("KAFKA_API_KEY"),
    'sasl.password': os.getenv("KAFKA_API_SECRET"),
    'group.id': 'dashboard-consumer-group',
    'auto.offset.reset': 'latest'
}

# ---------- Init Consumer ONCE ----------
@st.cache_resource
def init_consumer():
    c = Consumer(conf)
    c.subscribe(['roadmap_updates'])
    return c

consumer = init_consumer()

# ---------- Session State ----------
if "data" not in st.session_state:
    st.session_state.data = []

# ---------- Poll Kafka (NON-BLOCKING) ----------
msg = consumer.poll(0.3)

if msg is not None and not msg.error():
    event = json.loads(msg.value().decode())
    st.session_state.data.append(event)

# ---------- Display ----------
if st.session_state.data:
    df = pd.DataFrame(st.session_state.data)

    st.subheader("📌 Live Roadmap Updates")
    st.dataframe(df, use_container_width=True)
    st.metric("Total Updates", len(df))
else:
    st.info("Waiting for roadmap updates from Kafka...")

# ---------- Manual refresh hint ----------
st.caption("⏱️ Page refreshes automatically when new Kafka messages arrive")
