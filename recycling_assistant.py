import streamlit as st
import json
import base64
import requests
import os
import utils
from streamlit_card import card

# Function to load the recycling data
def load_recycling_data():
    current_dir = os.getcwd()
    file_path = os.path.join(current_dir, 'data.json')
    try:
        with open(file_path, ) as file:
            return json.load(file)
    except FileNotFoundError:
        st.error("Could not find data.json file")
        return None

# Function to analyze the picture taken from the camera
def analyze_image(image_data):
    try:
        # Encode image to base64
        base64_image = base64.b64encode(image_data.getvalue()).decode('utf-8')
        # print(base64_image)
        prompt = """
        You are a waste sorting assistant that identifies items based on established recycling categories. Identify items precisely to help users determine the correct disposal method.
        Analyze this image and identify items.
        Guidelines for identification:
        - List only physical objects you can clearly see
        - Use simple, generic terms
        - Specify quantities if multiple similar items exist
        - Ignore background elements or non-disposable items
        Format your response as a comma-separated list. Example:
        "glass wine bottle, plastic yogurt container, banana peel, cardboard box"
        """
        response = requests.post(
            url = "https://eu-de.ml.cloud.ibm.com/ml/v1/text/chat?version=2023-05-29",
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Authorization": f"Bearer {utils.API_TOKEN}"
            },
            json={
                "messages": [
                    {
                        "role": "system",
                        "content": prompt
                    },
                    {
                        "role": "user",
                        "content": [{
                            "type": "text",
                            "text": ""
                        }, {
                            "type": "image_url",
                            "image_url": {
                                "url":
                                f"data:image/jpeg;base64, {base64_image}"
                            }
                        }]
                    }
                ],
                "project_id": "5fcc55d2-43bf-4bae-a2f9-5b4ce2885c77",
                "model_id": "mistralai/pixtral-12b",
                "max_tokens": 900,
                "temperature": 0,
                "top_p": 1
            })

        data = response.json()
        return data['choices'][0]['message']['content']

    except Exception as e:
        return f"Error analyzing image: {str(e)}"


def get_recycling_advice(context, items):
    prompt = f"""
    You are a specialized recycling assistant with deep knowledge of waste sorting.
    Your goal is to provide accurate, practical advice that helps users correctly dispose of items.
    Always prioritize environmental safety and proper waste separation.

    You are a recycling expert assistant. Using the provided recycling guidelines, analyze these items: {items} Context (recycling guidelines):
    {context}

    For each item, provide a structured analysis:
    - Item Name: [name1]
    - Correct Bin: [Specify the exact bin color/type]
    - Preparation Required: [List any cleaning/preparation steps]
    - Reason: [Explain why this bin is correct]
    - Special Notes: [Any warnings, alternatives, or important details]
    ---------
    - Item Name: [name2]
    - Correct Bin: [Specify the exact bin color/type]
    - Preparation Required: [List any cleaning/preparation steps]
    - Reason: [Explain why this bin is correct]
    - Special Notes: [Any warnings, alternatives, or important details]
    ---------
    - Item Name: [name3]
    - Correct Bin: [Specify the exact bin color/type]
    - Preparation Required: [List any cleaning/preparation steps]
    - Reason: [Explain why this bin is correct]
    - Special Notes: [Any warnings, alternatives, or important details]

    Guidelines for your response:
    - Separate each item with the separator ---------
    - Remove empty lines
    - Be specific about bin colors and types
    - If an item isn't in the guidelines, recommend the safest disposal method
    - Mention if items need to be clean, disassembled, or specially prepared
    - Include any relevant warnings about contamination or hazardous materials
    - If an item has multiple components, explain how to separate them
    - Answer only with the structure described
    - Please format your response clearly and concisely for each item and do not use <|eom_id|>.
    """

    url = "https://eu-de.ml.cloud.ibm.com/ml/v1/text/generation?version=2023-05-29"

    body = {
        "input": prompt,
        "parameters": {
            "decoding_method": "greedy",
            "max_new_tokens": 500,
            "min_new_tokens": 0,
            "repetition_penalty": 1
        },
        "model_id": "meta-llama/llama-3-1-70b-instruct",
        "project_id": "2edf768f-9827-4456-8f8f-9322f75f2314",
        "moderations": {
            "hap": {
                "input": {
                    "enabled": True,
                    "threshold": 0.5,
                    "mask": {
                        "remove_entity_value": True
                    }
                },
                "output": {
                    "enabled": True,
                    "threshold": 0.5,
                    "mask": {
                        "remove_entity_value": True
                    }
                }
            },
            "pii": {
                "input": {
                    "enabled": True,
                    "threshold": 0.5,
                    "mask": {
                        "remove_entity_value": True
                    }
                },
                "output": {
                    "enabled": True,
                    "threshold": 0.5,
                    "mask": {
                        "remove_entity_value": True
                    }
                }
            }
        }
    }

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer " + utils.API_TOKEN
    }

    response = requests.post(url, headers=headers, json=body)

    if response.status_code != 200:
        raise Exception("Non-200 response: " + str(response.text))

    data = response.json()
    return data['results'][0]['generated_text']


def get_bin_image(waste_type):
    """Return the image path for a given waste type"""
    bin_images = {
        "battery_symbol": "images/battery_symbol.png",
        "blue": "images/blu.png",
        "brown": "images/brown.png",
        "green": "images/green.png",
        "yellow": "images/yellow.png",
        "grey": "images/grey.png",
        "oil_symbol": "images/oil_symbol.png",
        "red": "images/red.png",
        "farmacie": "images/farmacie.jpg",
        "yellow_street": "images/yellow_street.png",
    }
    return bin_images.get(waste_type.lower(), None)


def main():
    st.title("♻️ Recycling Assistant")

    # # Load recycling data
    recycling_data = load_recycling_data()

    if not recycling_data:
        st.stop()

    img_file = st.camera_input("Take a picture of the item")
    if img_file is not None:
        with st.spinner("Analyzing image..."):
            identified_items = analyze_image(img_file)

            if not isinstance(identified_items,str) or identified_items.startswith("Error"):
                st.error(identified_items)
            else:
                st.write("Detected Items:", identified_items)

                items = identified_items
                context = json.dumps(recycling_data)
                recycling_advice = get_recycling_advice(context, items)

                print(recycling_advice)
                # generate a lore for the object

                # animate the object

                st.write("### Recycling Instructions:")
                recycling_advice_items = recycling_advice.split('---------')

                for recycling_advice_item in recycling_advice_items:
                    recycling_advice = {}
                    print("recycling_advice_item", recycling_advice_item)
                    for line in recycling_advice_item.splitlines():
                        line = line.strip()  # Rimuovi spazi iniziali e finali
                        if line:  # Salta le righe vuote
                            if ": " in line:  # Assicurati che ci sia un delimitatore valido
                                key, value = line.split(": ", 1)  # Dividi al primo ": "
                                recycling_advice[key.lstrip("- ")] = value.strip()
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        card(
                        title=recycling_advice['Item Name'],
                        text=[recycling_advice['Reason'], recycling_advice['Special Notes']],
                        styles={
                        "card": {
                            "width": "100%",
                            "height": "300px",
                            "border": "1px solid black",
                            "padding": "10px",
                            "margin": "0px",
                        },
                        "filter": {
                            "background-color": "gray"
                        },
                        "text": {
                            "color": "white",
                            "font-weight": "lighter",
                        }
                        }
                        )

                    with col2:
                        # Map waste types to their corresponding images
                        if "unsorted waste" in recycling_advice_item.lower() or "grey" in recycling_advice_item.lower():
                            st.image(get_bin_image("grey"), width=200)
                        elif "organic" in recycling_advice_item.lower() or "food waste" in recycling_advice_item.lower() or "brown" in recycling_advice_item.lower():
                            st.image(get_bin_image("brown"), width=200)
                        elif "plastic" in recycling_advice_item.lower() or "metal" in recycling_advice_item.lower() or "yellow" in recycling_advice_item.lower():
                            st.image(get_bin_image("yellow"), width=200)
                        elif "paper" in recycling_advice_item.lower() or "blue" in recycling_advice_item.lower():
                            st.image(get_bin_image("blue"), width=200)
                        elif "collection centers" in recycling_advice_item.lower() or "electronic" in recycling_advice_item.lower() or "red" in recycling_advice_item.lower():
                            st.image(get_bin_image("red"), width=200)
                        elif "oil" in recycling_advice_item.lower():
                            st.image(get_bin_image("oil_symbol"),width=200)
                        elif "battery" in recycling_advice_item.lower():
                            st.image(get_bin_image("battery_symbol"),width=200),
                        elif "farmacy" in recycling_advice_item.lower():
                            st.image(get_bin_image("farmacie"), width=200)
                        st.write("<p style='text-align: center;'>" + recycling_advice["Correct Bin"] + " bin</p>", unsafe_allow_html=True)

