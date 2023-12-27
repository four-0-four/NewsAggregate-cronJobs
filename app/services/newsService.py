import requests
from app.models.common import Category, NewsCorporations
from app.models.news import NewsInput

BASE_URL = "http://138.197.63.3"
KEYWORDS_ENDPOINT = "/news/acquireKeywords"
ADD_NEWS_ENDPOINT = "/news/add"


def acquire_keywords(description, token):
    headers = {'Authorization': f'Bearer {token}'}
    data = {"description": description}

    try:
        response = requests.get(BASE_URL + KEYWORDS_ENDPOINT, json=data, headers=headers)
        response.raise_for_status()
        return response.json().get('keywords')
    except requests.RequestException as e:
        raise Exception(f"        Error acquiring keywords - get: {e}")


def add_news(news_data: NewsInput, token):
    headers = {'Authorization': f'Bearer {token}'}

    try:
        # Convert the news_data object to a dictionary
        news_data_dict = news_data.dict()

        # Convert datetime objects to string in ISO format
        if news_data_dict.get('publishedDate'):
            news_data_dict['publishedDate'] = news_data_dict['publishedDate'].isoformat()

        response = requests.post(BASE_URL + ADD_NEWS_ENDPOINT, json=news_data_dict, headers=headers)
        response.raise_for_status()
        print("        News successfully added")
    except requests.RequestException as e:
        raise Exception(f"        Error adding news: {e}")


def fetch_categories(db):
    # Fetch all categories from the database
    return db.query(Category).all()


def fetch_news_corporations(db):
    # Fetch all news corporations from the database
    return db.query(NewsCorporations).all()

