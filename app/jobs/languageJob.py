from ..config.database import SessionLocal
from dotenv import load_dotenv
from app.util.apiHandler import get_from_api
from app.models.language import Language
from app.util.apiHandler import get_from_api

# Load environment variables
load_dotenv()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def run_language_cron_job():
    # Get a database session
    print("LOG: connecting to database...")
    db_gen = get_db()
    db = next(db_gen)

    try:
        print("LOG: fetching languages from API...")
        url = 'https://parseapi.back4app.com/classes/Continentscountriescities_Language'
        languages_data = get_from_api(url)['results']

        for language in languages_data:
            # Check if the language already exists in the database
            print("LOG: checking if language exists...")
            existing_language = db.query(Language).filter_by(code=language['code']).first()
            if not existing_language:
                # If not, create a new Language instance and add it to the session
                new_language = Language(
                    code=language['code'],
                    name=language['name'],
                    native=language.get('native')  # Use .get in case 'native' is not present in the response
                )
                print("LOG: adding language ${new_language.name} to database...")
                db.add(new_language)
        
        db.commit()  # Commit the session if new languages were added

    except Exception as e:
        print(f"ERROR: An error occurred: {e}")
        db.rollback()  # Rollback the session in case of error

    finally:
        # Make sure to close the database session
        next(db_gen, None)

if __name__ == "__main__":
    run_language_cron_job()
