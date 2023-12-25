import requests
import json
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.common import Category
from app.models.news import News, NewsKeywords, NewsAffiliates, NewsMedia, NewsInput
from ..config.database import SessionLocal
from dotenv import load_dotenv
import os
from app.services.authService import authenticate_user
from app.services.newsService import add_news, fetch_categories, fetch_news_corporations, acquire_keywords

# Load environment variables
load_dotenv()

# API credentials and endpoints
newsdata_io_api_key = os.getenv('NEWS_DATA_TO_API_KEY')


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def make_news_api_call(category, domain, language="en"):
    url = "https://newsdata.io/api/1/news"
    params = {
        "apikey": newsdata_io_api_key,
        "language": language,
        "domain": domain,
        "category": category
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json().get('results', [])
    except requests.RequestException as e:
        raise Exception(f"Error in make_news_api_call: {e}")


def write_to_json_file(filename,data):
    print("LOG: Writing news to json file...")
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)


def authenticate():
    print("LOG: Authenticating user...")
    token = authenticate_user('sina', 'sinasina12')
    if not token:
        print("LOG: Authentication failed")
        return None
    return token


def fetch_news_for_category_and_corporation(category, corporation, token):
    print(f"LOG: Fetching news for {corporation.shortName} in category {category.name}...")
    # Assuming make_news_api_call takes category name and corporation shortName
    news_list = make_news_api_call(category.name, corporation.shortName)
    if not news_list:
        print(f"LOG: No news found for {corporation.shortName} in category {category.name}")
        return None
    return news_list


def get_category_id(db, category_name):
    category = db.query(Category).filter(Category.name == category_name).first()
    if category:
        return category.id
    else:
        return None


def process_news_item(db, news_item, token, category):
    print(f"LOG: Processing news {news_item.get('title', '')}...")

    # Convert pubDate to MySQL datetime format
    pub_date_str = news_item.get('pubDate', '')
    pub_date = datetime.strptime(pub_date_str, '%Y-%m-%d %H:%M:%S') if pub_date_str else datetime.now()

    # Placeholder for keywords logic - implement as needed
    keywords = acquire_keywords(news_item.get('description', ''), token) if news_item.get('description', '') else []

    # Assuming default values for language_id, isInternal, isPublished, writer_id, and category_id
    news_data = NewsInput(
        title=news_item.get('title', ''),
        description=news_item.get('description', None),
        content=news_item.get('content', ''),
        publishedDate=pub_date,
        language_id=16,
        isInternal=False,
        isPublished=False,
        keywords=keywords,
        category_id=get_category_id(category)
    )

    return news_data


def run_news_cron_job():
    db: Session = next(get_db())
    token = authenticate()
    if not token:
        return

    categories = fetch_categories(db)
    news_corporations = fetch_news_corporations(db)

    for category in categories:
        for corporation in news_corporations:
            news_list = fetch_news_for_category_and_corporation(category, corporation, token)
            if not news_list:
                continue

            write_to_json_file(f"{corporation.shortName}_{category.name}.json", news_list)
            '''
            for news_item in news_list:
                news_data = process_news_item(db, news_item, token, category.name)
                if news_data:
                    add_news(news_data, db)
            '''




if __name__ == "__main__":
    run_news_cron_job()
