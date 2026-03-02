import os
import requests
import streamlit as st

# Configure this to point to your n8n instance
# Example: "https://your-n8n-domain.com/webhook"
N8N_BASE_URL = os.getenv("N8N_BASE_URL", "http://localhost:5678/webhook")

UI_PATH = "chat"           # from Serve UI (GET) node
API_PATH = "chat-response" # from Receive Msg (POST)1 node

st.set_page_config(page_title="n8n Agent UI", page_icon="🤖", layout="centered")

st.title("n8n Agent")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I am your n8n assistant. How can I help?"}
    ]

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

user_input = st.chat_input("Type a message...")

def call_n8n_api(message: str) -> str:
    """Call the n8n /chat-response webhook and return the agent's reply."""
    url = f"{N8N_BASE_URL}/{API_PATH}"
    try:
        resp = requests.post(
            url,
            json={"message": message},
            timeout=60,
        )
        resp.raise_for_status()
        data = resp.json()
        # Your Respond to UI nodes return { "output": "<text>" }
        return data.get("output", "No response defined in n8n.")
    except Exception as e:
        return f"Error calling n8n: {e}"

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Agent is thinking..."):
            reply = call_n8n_api(user_input)
            st.markdown(reply)
    st.session_state.messages.append({"role": "assistant", "content": reply})
