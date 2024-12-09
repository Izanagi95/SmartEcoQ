import streamlit as st
import requests

TOKEN = "xxx"

def main():
    st.title("🤖 Chat with Recycling Assistant")

    # Initialize session state for chat history and input
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "user_input" not in st.session_state:
        st.session_state.user_input = ""

    # Display chat history
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.write(f"**You:** {message['content']}")
        else:
            st.write(f"**Assistant:** {message['content']}")

    # Text input for user
    user_input = st.text_input("Type your question about recycling:", value=st.session_state.user_input, key="chat_input")

    # If user submits input
    if st.button("Send") and user_input:
        # Append user message to session
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Generate chatbot response
        with st.spinner("The assistant is thinking..."):
            try:
                # Example API call (replace with your preferred chatbot API logic)
                response = requests.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {TOKEN}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "gpt-4",
                        "messages": [{"role": "user", "content": user_input}],
                        "max_tokens": 200
                    }
                )
                assistant_reply = response.json()["choices"][0]["message"]["content"]
            except Exception as e:
                assistant_reply = f"Error: {str(e)}"
        
        # Append assistant message to session
        st.session_state.messages.append({"role": "assistant", "content": assistant_reply})
        
        # Clear the input field
        st.session_state.user_input = ""