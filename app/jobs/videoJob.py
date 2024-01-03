from sqlalchemy.orm import Session

from app.config.database import SessionLocal
from app.jobs.newsJob import authenticate
from app.services.NewsMediaProcessor import NewsMediaProcessor, create_video_with_music
from app.services.newsService import get_news_for_category_past_12hr
import random


categories = [5,6,7,8,9]
category_name = {
    6: 'politics',
    5: 'health',
    7: 'science',
    8: 'sports',
    9: 'technology'
}

news_list = [
  {
      "title": "Young Gazans hope for peace in new year as war with Israel goes on",
      "url": "https://ichef.bbci.co.uk/news/1024/branded_news/2325/production/_132179980_p0h2bpd0.jpg"
  },
  {
      "title": "New Year celebrations",
      "url": "https://ichef.bbci.co.uk/news/1024/branded_news/157BD/production/_132179978_p0h2bmsz.jpg"
  },
  {
      "title": "Missouri extends SEC Coach of Year Drinkwitz",
      "url": "https://a.espncdn.com/combiner/i?img=%2Fphoto%2F2023%2F1231%2Fr1272252_1296x729_16%2D9.jpg"
  },
  {
      "title": "Xi Jinping says Chinese business having 'tough time' in new year message",
      "url": "https://i.guim.co.uk/img/media/44da1bb1ef378819c33a1c9d041bd9eeda55505c/288_529_2741_1645/master/2741.jpg?width=1200&height=630&quality=85&auto=format&fit=crop&overlay-align=bottom%2Cleft&overlay-width=100p&overlay-base64=L2ltZy9zdGF0aWMvb3ZlcmxheXMvdGctZGVmYXVsdC5wbmc&s=6174b0863abadb437b6973809cc6516c"
  },
  {
      "title": "Three's £2bn dividend payout sparks row over Vodafone merger",
      "url": "https://i.guim.co.uk/img/media/449c1969405243c63af1eef489a665365289d71f/0_269_5088_3052/master/5088.jpg?width=1200&height=630&quality=85&auto=format&fit=crop&overlay-align=bottom%2Cleft&overlay-width=100p&overlay-base64=L2ltZy9zdGF0aWMvb3ZlcmxheXMvdGctZGVmYXVsdC5wbmc&s=a41b3b6eebf0aba3759eade16c2ac17a"
  },
  {
      "title": "Venice to limit tourist group size to 25 to protect historic city",
      "url": "https://i.guim.co.uk/img/media/ed0d6e4bd960d764fc1a6b6df0556c556d7f4bd8/0_200_3000_1800/master/3000.jpg?width=1200&height=630&quality=85&auto=format&fit=crop&overlay-align=bottom%2Cleft&overlay-width=100p&overlay-base64=L2ltZy9zdGF0aWMvb3ZlcmxheXMvdGctZGVmYXVsdC5wbmc&s=ab1172a7d00f1bf5594473927ed83cfc"
  },
  {
      "title": "Cyber-hackers target UK nuclear waste company RWM",
      "url": "https://i.guim.co.uk/img/media/df73b79363a5a5f2b0f129e594572436120ff6be/0_94_4157_2494/master/4157.jpg?width=1200&height=630&quality=85&auto=format&fit=crop&overlay-align=bottom%2Cleft&overlay-width=100p&overlay-base64=L2ltZy9zdGF0aWMvb3ZlcmxheXMvdGctZGVmYXVsdC5wbmc&s=cf45c75e903086bbda3dd68961bbcb57"
  }
]

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def run_video_cron_job():
    db: Session = next(get_db())
    token = authenticate()
    if not token:
        return

    image_paths = []
    
    for i in range(len(news_list)):
        news = news_list[i]
        print(f"        LOG: Processing news {news['title']}...")
        processor = NewsMediaProcessor(news["url"], news["title"], f"media/image/news{i}.jpg")
        processed_image_path = processor.process_image()
        image_paths.append(processed_image_path)
        print(f"        LOG: Processed image saved to {processed_image_path}")

    print(f"LOG: Creating video with music...")
    random_number = random.randint(1, 15)
    create_video_with_music(image_paths, 'media/output_video.mp4', f"media/music/music{random_number}.mp3")
    



if __name__ == "__main__":
    run_video_cron_job()