import os
import requests
import json

class APIRequestException(Exception):
    """Exception raised for errors in the API request.

    Attributes:
        message -- explanation of the error
    """
    def __init__(self, message):
        self.message = message
        super().__init__(message)

class APIDataException(Exception):
    """Exception raised for errors in handling API data.

    Attributes:
        message -- explanation of the error
    """
    def __init__(self, message):
        self.message = message
        super().__init__(message)

def fetch_json_from_github(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # This will raise an HTTPError if the HTTP request returned an unsuccessful status code.
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None

def get_from_api(url):
    # API details
    app_id = os.getenv('PARSE_APPLICATION_ID')
    api_key = os.getenv('PARSE_REST_API_KEY')

    # Check if environment variables are set
    if not app_id or not api_key:
        raise ValueError("ERROR: Missing required environment variables (PARSE_APPLICATION_ID, PARSE_REST_API_KEY)")

    headers = {
        'X-Parse-Application-Id': app_id,
        'X-Parse-REST-API-Key': api_key
    }

    try:
        # Fetch data
        response = requests.get(url, headers=headers)
        
        # Check if the request was successful
        if response.status_code != 200:
            raise APIRequestException(f"ERROR: Request failed with status code {response.status_code}: {response.text}")

        # Parse JSON data
        data = response.json()
        return data

    except requests.RequestException as e:
        # Raise requests-related exceptions
        raise APIRequestException(f"ERROR: Could not retrieve data from the API - {e}")
    except json.JSONDecodeError:
        # Raise JSON parsing error
        raise APIDataException("ERROR: Failed to parse JSON response")