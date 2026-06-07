import httpx
import streamlit as st

API_URL = "http://localhost:8000/query"

st.set_page_config(
    page_title="DataSage",
    page_icon="🧠",
    layout="centered",
)

st.title("🧠 DataSage")
st.markdown("Ask about movies, music, or books in natural language.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ask a question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                resp = httpx.post(API_URL, json={"question": prompt}, timeout=60)
                resp.raise_for_status()
                answer = resp.json()["answer"]
            except Exception as e:
                answer = f"Error: {e}"
        st.markdown(answer)
    st.session_state.messages.append({"role": "assistant", "content": answer})
