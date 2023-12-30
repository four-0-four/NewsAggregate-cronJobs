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
        print(f"        WARNING: No news found for {corporation}...")
        return None
    else:
        print(f"        LOG: Fetched {len(news_list)} news for {corporation}...")
    return news_list


def get_categories(news_item):
    categories = news_item.get('categories', [])
    extracted_categories = []

    for cat in categories:
        # Check if the URI contains '/'
        if '/' in cat['uri']:
            # Split the URI into parts
            parts = cat['uri'].split('/')
            # Remove the first part and reassemble the rest
            cleaned_uri = '/'.join(parts[1:])
            # Add to the extracted categories
            extracted_categories.append(cleaned_uri)

    return extracted_categories

def get_keywords(news_item):
    concepts = news_item.get('concepts', [])
    keywords = [concept['label']['eng'] for concept in concepts if 'label' in concept and 'eng' in concept['label']]
    return keywords


def process_news_item(db, news_item, token):
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

    news_image = news_item.get('image', '')
    if not news_image:
        return False

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
        media_urls=[news_image],
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

        number_of_news_added = 0
        number_of_news_to_authenticate = 0
        for news_item in news_list:
            if number_of_news_to_authenticate >= 100:
                token = authenticate()
                if not token:
                    return
                number_of_news_to_authenticate = 0

            news_data = process_news_item(db, news_item, token)
            if news_data:
                response = add_news(news_data, token)
                number_of_news_added += response == 200

            number_of_news_to_authenticate += 1
        print(f"        LOG: {number_of_news_added} news for {corporation} to the database...")



if __name__ == "__main__":
    run_news_cron_job()
