import requests
import json
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.news import News, NewsKeywords, NewsAffiliates, NewsMedia, NewsInput
from ..config.database import SessionLocal
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# API credentials and endpoints
newsdata_io_api_key = os.getenv('NEWS_DATA_TO_API_KEY')
BASE_URL = "http://138.197.63.3"
AUTH_ENDPOINT = "/auth/user/login"
KEYWORDS_ENDPOINT = "/news/acquireKeywords"
ADD_NEWS_ENDPOINT = "/news/add"


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def make_news_api_call(language, domain):
    url = "https://newsdata.io/api/1/news"
    params = {"apikey": newsdata_io_api_key, "language": language, "domain": domain}

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json().get('results', [])
    except requests.RequestException as e:
        raise Exception(f"Error in make_news_api_call: {e}")


def authenticate_user(username, password):
    auth_url = BASE_URL + AUTH_ENDPOINT
    data = {'username': username, 'password': password}

    try:
        response = requests.post(auth_url, data=data)
        response.raise_for_status()
        return response.json().get('token')
    except requests.RequestException as e:
        raise Exception(f"Authentication failed: {e}")


def acquire_keywords(description, token):
    headers = {'Authorization': f'Bearer {token}'}
    data = {"description": description}

    try:
        response = requests.post(BASE_URL + KEYWORDS_ENDPOINT, json=data, headers=headers)
        response.raise_for_status()
        return response.json().get('keywords')
    except requests.RequestException as e:
        raise Exception(f"Error acquiring keywords: {e}")


def add_news(news_data, token):
    headers = {'Authorization': f'Bearer {token}'}

    try:
        response = requests.post(BASE_URL + ADD_NEWS_ENDPOINT, json=news_data, headers=headers)
        response.raise_for_status()
        print("News successfully added")
    except requests.RequestException as e:
        raise Exception(f"Error adding news: {e}")


def run_news_cron_job():
    try:
        db: Session = next(get_db())

        # Authenticate and get token
        print("LOG: Authenticating user...")
        token = authenticate_user('sina', 'sinasina12')
        if not token:
            return

        print("LOG: Fetching news from API...")
        news_list = make_news_api_call('en', 'bbc')
        if not news_list:
            return

        print("LOG: Processing news...")
        for news_item in news_list:
            print(f"LOG: Processing news {news_item.get('title', '')}...")
            print(f"LOG: Acquiring keywords for news {news_item.get('title', '')}...")
            keywords = acquire_keywords(news_item.get('description', ''), token)
            if keywords:
                news_data = {
                    "title": news_item.get('title', ''),
                    "description": news_item.get('description', ''),
                    "content": news_item.get('content', ''),
                    "publishedDate": datetime.now().isoformat(),
                    "language_id": 16,
                    "isInternal": False,
                    "isPublished": True,
                    "keywords": keywords
                }
                print(f"LOG: Adding news {news_item.get('title', '')} to database...")
                add_news(news_data, token)

    except Exception as e:
        print(f"Error in run_news_cron_job: {e}")


if __name__ == "__main__":
    run_news_cron_job()
