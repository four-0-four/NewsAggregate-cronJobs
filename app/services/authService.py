import requests


BASE_URL = "https://api.farabix.com/mainframe2"
#BASE_URL = "http://127.0.0.1:8080"
AUTH_ENDPOINT = "/auth/user/login"


def authenticate_user(username, password):
    auth_url = BASE_URL + AUTH_ENDPOINT
    data = {'username': username, 'password': password}

    try:
        response = requests.post(auth_url, data=data)
        response.raise_for_status()

        return response.json().get('access_token')
    except requests.RequestException as e:
        raise Exception(f"Authentication failed: {e}")