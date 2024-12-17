import streamlit as st
import requests
import utils

USER_AVATAR = "👤"
BOT_AVATAR = "🤖"
SYSTEM_PROMPT = """
Assume the role of an Italian Virtual Assistant for Lucca Comics, a renowned annual event.
Your task is to provide informative yet entertaining responses to user queries about the event's programs.
Your answers should be in Italian and reflect the lively and unique atmosphere of Lucca Comics.
The first question is, "What are the main programs happening at Lucca Comics this year?"
Respond with concise, witty sentences that capture the essence of the event.
Remember, your goal is to inform and entertain simultaneously. Add a relevant emoji to your answer.
"""
def main():
    st.title("🤖 Chat with Event Assistant")

    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "Ciao! Sono il tuo assistente per questo evento di Lucca Comics. Come posso aiutarti? 😊"}]

    # Display chat messages
    for msg in st.session_state.messages[0:]:
        if msg['role'] == "user":
            with st.chat_message("user", avatar=USER_AVATAR):
                if msg['content'][0]['type'] == "text":
                    st.write(msg['content'][0]['text'])
        else:
            st.chat_message("assistant", avatar=BOT_AVATAR).write(msg["content"])

    user_input = st.chat_input("How can I help you?")
    if user_input:
        message = {"role": "user", "content": [{"type": "text", "text": user_input}]}
        st.session_state.messages.append(message)
        avatar = USER_AVATAR if message["role"] == "user" else BOT_AVATAR
        st.chat_message(message['role'], avatar=avatar).write(user_input)

        url = "https://eu-de.ml.cloud.ibm.com/ml/v1/text/chat?version=2023-05-29"
        model_messages = []
        latest_image_url = None
        for msg in st.session_state.messages:
            if msg["role"] == "user" and isinstance(msg["content"], list):
                content = []
                for item in msg["content"]:
                    if item["type"] == "text":
                        content.append(item)
                    elif item["type"] == "image_url":
                        latest_image_url = item
                if latest_image_url:
                    content.append(latest_image_url)
                model_messages.append({"role": msg["role"], "content": content})
            else:
                model_messages.append({"role": msg["role"], "content": [{"type": "text", "text": msg["content"]}] if isinstance(msg["content"], str) else msg["content"]})
        # st.write(st.session_state.messages)
        # st.write("model msg")
        # st.write(model_messages[-1])


        response = requests.post(
            url,
            headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {utils.API_TOKEN}"
        },
            json={
                "messages": [
                    {
                    "role":
                    "system",
                    "content": SYSTEM_PROMPT
                    }, model_messages[-1]
                ],
                "project_id": "5fcc55d2-43bf-4bae-a2f9-5b4ce2885c77",
                "model_id": "meta-llama/llama-3-1-70b-instruct",
                "decoding_method": "greedy",
                "repetition_penalty": 1,
                "max_tokens": 900
            }
        )

        if response.status_code != 200:
            raise Exception("Non-200 response: " + str(response.text))

        data = response.json()
        res_content = data['choices'][0]['message']['content']
        print(res_content)

        st.session_state.messages.append({"role": "assistant", "content": res_content})
        with st.chat_message("assistant", avatar=BOT_AVATAR):
            st.write(res_content)