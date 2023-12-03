from ..config.database import SessionLocal
from dotenv import load_dotenv
from app.util.apiHandler import get_from_api
from app.models.language import Language

# Load environment variables
load_dotenv()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_languages_from_api():
    # API details
    url = 'https://parseapi.back4app.com/classes/Continentscountriescities_Language'
    data = get_from_api(url)

def run_language_cron_job():
    # Get a database session
    db_gen = get_db()
    db = next(db_gen)

    try:
        languages_data = get_languages_from_api()

        for language in languages_data:
            # Check if the language already exists in the database
            existing_language = db.query(Language).filter_by(code=language['code']).first()
            if not existing_language:
                # If not, create a new Language instance and add it to the session
                new_language = Language(
                    code=language['code'],
                    name=language['name'],
                    native=language.get('native')  # Use .get in case 'native' is not present in the response
                )
                db.add(new_language)
        
        db.commit()  # Commit the session if new languages were added

    except Exception as e:
        print(f"An error occurred: {e}")
        db.rollback()  # Rollback the session in case of error

    finally:
        # Make sure to close the database session
        next(db_gen, None)

if __name__ == "__main__":
    run_language_cron_job()
