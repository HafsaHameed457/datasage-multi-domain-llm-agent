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
if "summary" not in st.session_state:
    st.session_state.summary = ""

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
                body = {
                    "question": prompt,
                    "summary": st.session_state.summary,
                    "history": [
                        [m["role"], m["content"]]
                        for m in st.session_state.messages[:-1]
                    ],
                }
                resp = httpx.post(API_URL, json=body, timeout=60)
                resp.raise_for_status()
                data = resp.json()
                answer = data["answer"]
                st.session_state.summary = data.get("summary", "")
            except Exception as e:
                answer = f"Error: {e}"
        st.markdown(answer)
    st.session_state.messages.append({"role": "assistant", "content": answer})
