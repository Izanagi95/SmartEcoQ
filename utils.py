import requests
import os
from dotenv import load_dotenv

# Carica il file .env
load_dotenv()

API_TOKEN = ""

def setup():
    global API_TOKEN  # Dichiara che stai modificando la variabile globale
    API_KEY = os.getenv('API_KEY')

    # Define the URL and headers
    url = 'https://iam.cloud.ibm.com/identity/token'
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    # Define the data payload
    data = {
        'grant_type': 'urn:ibm:params:oauth:grant-type:apikey',
        'apikey': API_KEY
    }

    # Send the POST request
    response = requests.post(url, headers=headers, data=data)

    # Check the response status
    if response.status_code == 200:
        print("Token response:")
        print(response.json())
        API_TOKEN = response.json()['access_token']
    else:
        print(f"Failed to retrieve token. Status code: {response.status_code}")
        print(response.text)