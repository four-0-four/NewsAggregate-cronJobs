import requests
import json
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.models.common import NewsCorporations
from app.models.news import NewsInput
from app.services.newsService import add_news
from ..config.database import SessionLocal
from dotenv import load_dotenv
import os
from app.services.authService import authenticate_user
from eventregistry import EventRegistry, QueryArticlesIter, ReturnInfo, ArticleInfoFlags, SourceInfoFlags

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


def fetch_news_for_corporation(corporation, token):
    print(f"        LOG: Fetching news for {corporation}...")
    # Assuming make_news_api_call takes category name and corporation shortName
    er = EventRegistry(apiKey='2084a034-acf9-46be-8c5f-26851ff83d3f')
    sourceUri = er.getSourceUri(corporation)
    news_list = []

    # Get today's date and yesterday's date
    today = datetime.now()
    yesterday = today - timedelta(days=1)

    q = QueryArticlesIter(
        sourceUri=sourceUri,
        lang="eng",
        dateStart=yesterday,
        dateEnd=today
    )

    for article in q.execQuery(er, sortBy="date", returnInfo=ReturnInfo(
            articleInfo=ArticleInfoFlags(concepts=True, categories=True, location=True),
            sourceInfo=SourceInfoFlags(location=True, image=True)
    )):
        news_list.append(article)

    if not news_list:
        print(f"WARNING:        No news found for {corporation}")
        return None

    return news_list


def get_categories(news_item):
    categories = news_item.get('categories', [])
    extracted_categories = [cat['uri'].split('/')[1] for cat in categories if '/' in cat['uri']]
    return extracted_categories

def get_keywords(news_item):
    concepts = news_item.get('concepts', [])
    keywords = [concept['label']['eng'] for concept in concepts if 'label' in concept and 'eng' in concept['label']]
    return keywords


def process_news_item(db, news_item, token):
    print(f"        LOG: Processing news {news_item.get('title', '')}...")

    # Convert dateTimePub to MySQL datetime format
    pub_date_str = news_item.get('dateTimePub', '')
    pub_date = datetime.strptime(pub_date_str, '%Y-%m-%dT%H:%M:%SZ') if pub_date_str else datetime.now()

    # get keywords
    keywords = get_keywords(news_item)

    # get categories
    categories = get_categories(news_item)

    # Get the body of the news item
    body = news_item.get('body', '')

    # Summarize the body for description
    description = body[:50] + '...' if body else ''
    print(news_item.get('image', ''))
    # Assuming default values for language_id, isInternal, isPublished, writer_id, and category_id
    news_data = NewsInput(
        title=news_item.get('title', ''),
        description=description,
        content=body,
        publishedDate=pub_date,
        language_id=16,
        isInternal=False,
        isPublished=False,
        keywords=keywords,
        media_urls=[news_item.get('image', '')],
        categories=categories,
        writer_id=None
    )

    return news_data


def run_news_cron_job():
    db: Session = next(get_db())
    token = authenticate()
    if not token:
        return

    # Retrieve all news corporations from the database
    all_corporations = db.query(NewsCorporations).all()

    for corporation in all_corporations:
        print(f"LOG: Processing news for {corporation.name}...")
        news_corporation = corporation.name
        news_list = fetch_news_for_corporation(news_corporation, token)
        if not news_list:
            continue

        for news_item in news_list:
            news_data = process_news_item(db, news_item, token)
            if news_data:
                add_news(news_data, db)



if __name__ == "__main__":
    run_news_cron_job()
