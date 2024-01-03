import requests
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

BASE_URL = os.getenv("BASE_URL")
AUTH_ENDPOINT = os.getenv("AUTH_ENDPOINT")


def authenticate_user(username, password):
    auth_url = BASE_URL + AUTH_ENDPOINT
    data = {'username': username, 'password': password}

    try:
        response = requests.post(auth_url, data=data)
        response.raise_for_status()

        return response.json().get('access_token')
    except requests.RequestException as e:
        raise Exception(f"Authentication failed: {e}")