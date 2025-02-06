import google.generativeai as genai
from langchain.schema import HumanMessage, SystemMessage, AIMessage
import streamlit as st
import re

# Set up Streamlit page
st.title("🚀 Google Gemini Chat")
st.write("❤️ Built by [Build Fast with AI](https://buildfastwithai.com/genai-course)")

# Sidebar for API key input and model selection
with st.sidebar:
    st.header("⚙️ Configuration")

    # Take Google API Key input
    st.session_state.google_api_key = st.text_input("Google API Key", type="password")

    # Dropdown for model selection with correct models
    model_options = [
        "gemini-2.0-pro-exp",
        "gemini-2.0-flash-lite-preview",
        "gemini-2.0-flash"
    ]
    st.session_state.selected_model = st.selectbox("Select AI Model", model_options)

    st.divider()
    st.markdown(f"**Selected Model:** `{st.session_state.selected_model}`")

    st.divider()
    if st.button("🔄 Start New Chat", use_container_width=True):
        st.session_state.messages = [
            SystemMessage(content="You are a helpful AI assistant. Respond directly to queries without using '<think>' tags or extra reasoning steps.")
        ]
        st.rerun()

# Display initial assistant message
with st.chat_message("assistant"):
    st.write("Ask me anything!")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        SystemMessage(content="You are a helpful AI assistant. Respond directly to queries without using '<think>' tags or extra reasoning steps.")
    ]

# Display chat history
for message in st.session_state.messages[1:]:
    with st.chat_message("user" if isinstance(message, HumanMessage) else "assistant"):
        st.write(message.content)

# Chat input
if prompt := st.chat_input("What's on your mind?"):
    if not st.session_state.google_api_key:
        st.error("Please enter your Google API key in the sidebar")
        st.stop()

    # Initialize Gemini API client
    genai.configure(api_key=st.session_state.google_api_key)
    client = genai.GenerativeModel(st.session_state.selected_model)

    # Prepare chat history for Gemini model
    conversation_history = []
    for msg in st.session_state.messages:
        role = "user" if isinstance(msg, HumanMessage) else "model" 
        conversation_history.append({"role": role, "parts": [msg.content]})

    # Append the current user message
    conversation_history.append({"role": "user", "parts": [prompt]})

    # Add user message to chat history
    st.session_state.messages.append(HumanMessage(content=prompt))

    with st.chat_message("user"):
        st.write(prompt)

    # Get AI response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        try:
            response = client.generate_content(conversation_history)
            if response and hasattr(response, "text"):
                full_response = response.text

        except Exception as e:
            full_response = f"⚠️ Error: {str(e)}"

        # Remove <think> tags if present
        cleaned_response = re.sub(r"<think>.*?</think>", "", full_response, flags=re.DOTALL).strip()

        # Now display the cleaned response
        message_placeholder.write(cleaned_response)

    # Save AI response to chat history
    st.session_state.messages.append(AIMessage(content=cleaned_response))
