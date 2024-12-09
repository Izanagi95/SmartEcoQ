import streamlit as st
import json
import base64
import requests
import os
import utils

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
    
def analyze_image(image_data):
    try:
        # Encode image to base64
        base64_image = base64.b64encode(image_data.getvalue()).decode('utf-8')

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

        url = "https://eu-de.ml.cloud.ibm.com/ml/v1/text/generation?version=2023-05-29"

        # JSON body with Base64 image data
        body = {
            "input": prompt,
            "parameters": {
                "decoding_method": "greedy",
                "max_new_tokens": 200,
                "min_new_tokens": 0,
                "repetition_penalty": 1
            },
            "model_id": "mistralai/pixtral-12b",
            "project_id": "2edf768f-9827-4456-8f8f-9322f75f2314",
            "image_data": base64_image  # Adding the Base64-encoded image data
        }

        # Headers
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": "Bearer " + utils.API_TOKEN
        }

        # Send POST request
        response = requests.post(
            url,
            headers=headers,
            json=body
        )

        if response.status_code != 200:
            raise Exception("Non-200 response: " + str(response.text))

        data = response.json()
        return data['results'][0]['generated_text']
        
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
    1. Item Name:
    - Correct Bin: [Specify the exact bin color/type]
    - Preparation Required: [List any cleaning/preparation steps]
    - Reason: [Explain why this bin is correct]
    - Special Notes: [Any warnings, alternatives, or important details]
    Guidelines for your response:
    - Separate each item with a blank line
    - Be specific about bin colors and types
    - If an item isn't in the guidelines, recommend the safest disposal method
    - Mention if items need to be clean, disassembled, or specially prepared
    - Include any relevant warnings about contamination or hazardous materials
    - If an item has multiple components, explain how to separate them
    Please format your response clearly and concisely for each item."""


    url = "https://eu-de.ml.cloud.ibm.com/ml/v1/text/generation?version=2023-05-29"

    body = {
        "input": prompt,
        "parameters": {
            "decoding_method": "greedy",
            "max_new_tokens": 200,
            "min_new_tokens": 0,
            "repetition_penalty": 1
        },
        "model_id": "meta-llama/llama-3-3-70b-instruct",
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

    response = requests.post(
        url,
        headers=headers,
        json=body
    )

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
       "famacie": "images/farmacie.jpg",
       "yellow_street": "images/yellow_street.png",

    }
    return bin_images.get(waste_type.lower(), None)


def main():
    st.title("🌍 Recycling Assistant")

    # # Load recycling data
    recycling_data = load_recycling_data()

    if not recycling_data:
        st.stop()

    img_file = st.camera_input("Take a picture of the item")
    if img_file is not None:
        with st.spinner("Analyzing image..."):
            identified_items = analyze_image(img_file)
            
            if not isinstance(identified_items, str) or identified_items.startswith("Error"):
                st.error(identified_items)
            else:
                st.write("Detected Items:", identified_items)

                items = identified_items
                context = json.dumps(recycling_data)
                recycling_advice = get_recycling_advice(context, items)
                
                st.write("### Recycling Instructions:")
                items = recycling_advice.split('\n\n')
                
                for item in items:
                
                    if item.strip():
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.write(item)
                        with col2:
                            # Map waste types to their corresponding images
                            if "unsorted waste" in item.lower() or "grey" in item.lower():
                                st.image(get_bin_image("grey"), width=200)
                            elif "organic" in item.lower() or "food waste" in item.lower() or "brown" in item.lower():
                                st.image(get_bin_image("brown"), width=200)
                            elif "plastic" in item.lower() or "metal" in item.lower() or "yellow" in item.lower():
                                st.image(get_bin_image("yellow"), width=200)
                            elif "paper" in item.lower() or "blue" in item.lower():
                                st.image(get_bin_image("blue"), width=200)
                            elif "collection centers" in item.lower() or "electronic" in item.lower() or "red" in item.lower():
                                st.image(get_bin_image("red"), width=200)
                            elif "oil" in item.lower():
                                st.image(get_bin_image("oil_symbol"), width=200)
                            elif "battery" in item.lower():
                                st.image(get_bin_image("battery_symbol"), width=200),
                            elif "farmacy" in item.lower():
                                st.image(get_bin_image("farmacie"), width=200)

    # Add the new button and ecological sites finder
    if st.button("🔍 Find Nearby Ecological Sites"):
        st.write("### Nearby Ecological Sites:")