import streamlit as st
import requests
import json

# Configure the page
st.set_page_config(page_title="Multi-Model AI Chat", page_icon="🤖")

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("Multi-Model AI Chatbot")

# Sidebar for model selection
model = st.sidebar.radio(
    "Choose AI Model",
    ["claude", "gpt", "deepseek"],
    captions=["Anthropic Claude", "OpenAI GPT", "DeepSeek"]
)

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Chat input
if prompt := st.chat_input():
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # Send request to backend
    try:
        response = requests.post(
            "http://localhost:8000/chat",
            json={"message": prompt, "model": model}
        )
        response.raise_for_status()
        assistant_response = response.json()["response"]

        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": assistant_response})
        with st.chat_message("assistant"):
            st.write(assistant_response)

    except requests.exceptions.RequestException as e:
        st.error(f"Error communicating with the backend: {str(e)}")

# Clear chat button
if st.sidebar.button("Clear Chat"):
    st.session_state.messages = []
    st.rerun()
