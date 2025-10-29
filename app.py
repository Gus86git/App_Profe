import streamlit as st
import os
from groq import Groq

# Initialize the Groq client
try:
    # Get the API key from Streamlit's secrets
    client = Groq(api_key=st.secrets["groq_api_key"])
except Exception as e:
    st.error(f"Failed to initialize Groq client: {e}")
    st.stop()

st.title("🤖 My Groq AI Assistant")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("What is up?"):
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Get AI response
    try:
        stream = client.chat.completions.create(
            messages=st.session_state.messages,
            model="llama-3.3-70b-versatile",
            stream=True
        )
        
        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            response = st.write_stream(stream)
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})
    
    except Exception as e:
        st.error(f"An error occurred during the API call: {e}")
