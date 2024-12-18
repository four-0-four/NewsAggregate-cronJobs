import requests
from dotenv import load_dotenv
import os
from app.models.common import Category, NewsCorporations
from app.models.news import NewsInput

# Load environment variables
load_dotenv()

BASE_URL = os.getenv("BASE_URL")
ADD_NEWS_ENDPOINT = os.getenv("ADD_NEWS_ENDPOINT")

def add_news(news_data: NewsInput, token):
    headers = {'Authorization': f'Bearer {token}'}

    try:
        # Convert the news_data object to a dictionary
        news_data_dict = news_data.dict()

        # Convert datetime objects to string in ISO format
        if news_data_dict.get('publishedDate'):
            news_data_dict['publishedDate'] = news_data_dict['publishedDate'].isoformat()

        response = requests.post(BASE_URL + ADD_NEWS_ENDPOINT, json=news_data_dict, headers=headers)

        # Check if the response was successful
        if response.status_code != 200:
            print(f"        WARNING: Failed to add news {news_data.title}. Status code: {response.status_code}")
            return None
        return response.json()
    except requests.RequestException as e:
        print(f"Error during request: {e}")
        return None


def get_news_for_category_past_12hr(category_id, token):
    headers = {'Authorization': f'Bearer {token}'}

    try:

        response = requests.get(BASE_URL + "/news/getByCategory/past12hr", params={'category_id':category_id}, headers=headers)

        # Check if the response was successful
        if response.status_code != 200:
            print(f"WARNING: Failed to fetch news for category {category_id}. Status code: {response.status_code}")
            return None
        return response.json()
    except requests.RequestException as e:
        print(f"Error during request: {e}")
        return None

def fetch_categories(db):
    # Fetch all categories from the database
    return db.query(Category).all()


def fetch_news_corporations(db):
    # Fetch all news corporations from the database
    return db.query(NewsCorporations).all()


