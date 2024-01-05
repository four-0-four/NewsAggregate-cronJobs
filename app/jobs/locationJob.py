from ..config.database import SessionLocal
from dotenv import load_dotenv
from app.util.apiHandler import get_from_api, fetch_json_from_github
from app.models.location import Continent, Country, Province, City
import json
from app.util.apiHandler import APIDataException

# Load environment variables
load_dotenv()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_continent_id_given_name(db, continent_name):
    continent_name = continent_name.lower()
    continent = db.query(Continent).filter(Continent.name == continent_name).first()
    return continent.id if continent else None

def add_continent(db, continent_data):
    new_continent = Continent(
        name=continent_data["name"]
    )
    db.add(new_continent)
    db.commit()
    return new_continent
    
def add_country(db, country_data, continent_id):
    new_country = Country(
        name=country_data["name"],
        code=country_data["iso3"],
        capital=country_data.get("capital"),
        phone=country_data.get("phone_code"),
        native=country_data.get("native"),
        currency=country_data.get("currency"),
        continent_id=continent_id,
    )
    db.add(new_country)
    db.commit()
    return new_country

def add_province(db, province_data, country_id):
    new_province = Province(
        name=province_data["name"],
        code=province_data["state_code"],
        country_id=country_id,
    )
    db.add(new_province)
    db.commit()
    return new_province

def add_city(db, city_data, province_id, country_id):
    new_city = City(
        name=city_data["name"],
        province_id=province_id,
        country_id=country_id,
    )
    db.add(new_city)
    db.commit()
    return new_city

def get_coutries_provinces_cities():
    print("LOG: connecting to database...")
    db_gen = get_db()
    db = next(db_gen)

    try:
        print("LOG: fetching geographical data from API...")
        url = "https://raw.githubusercontent.com/dr5hn/countries-states-cities-database/master/countries%2Bstates%2Bcities.json"
        data = fetch_json_from_github(url)

        for country_data in data:
            print(f"LOG: Processing country {country_data['name']}...")
            continent_id = get_continent_id_given_name(db, country_data["region"])
            if not continent_id:
                raise Exception(f"ERROR: Continent {country_data['region']} not found in database.")
            
            db_country = db.query(Country).filter(
                Country.code == country_data["iso3"], 
                Country.name == country_data["name"]
            ).first()

            if db_country is None:
                print(f"LOG: Adding country {country_data['name']} to database...")
                db_country = add_country(db, country_data, continent_id)
                
            for province_data in country_data.get("states", []):
                print(f"LOG: Processing province {province_data['name']}...")
                db_province = db.query(Province).filter(
                    Province.code == province_data["state_code"], 
                    Province.name == province_data["name"]
                ).first()

                if db_province is None:
                    print(f"LOG: Adding province {province_data['name']} to database...")
                    db_province = add_province(db, province_data, db_country.id)

                for city_data in province_data.get("cities", []):
                    print(f"LOG: Processing city {city_data['name']}...")
                    db_city = db.query(City).filter(
                        City.name == city_data["name"],
                        City.country_id == db_country.id
                    ).first()

                    if db_city is None:
                        print(f"LOG: Adding city {city_data['name']} to database...")
                        add_city(db, city_data, db_province.id, db_country.id)

        print("LOG: Data processing completed.")

    except Exception as e:
        print(f"ERROR: An error occurred: {e}")
        db.rollback()

    finally:
        next(db_gen, None)
        print("LOG: Database session closed.")

def get_continents():
    print("LOG: connecting to database...")
    db_gen = get_db()
    db = next(db_gen)

    try:
        print("LOG: fetching geographical data from API...")
        url = "https://raw.githubusercontent.com/dr5hn/countries-states-cities-database/master/regions.json"
        data = fetch_json_from_github(url)
        
        for continent_data in data:
            print(f"LOG: Processing continent {continent_data['name']}...")
            db_continent = db.query(Continent).filter(
                Continent.name == continent_data["name"]
            ).first()

            if db_continent is None:
                print(f"LOG: Adding continent {continent_data['name']} to database...")
                db_continent = add_continent(db, continent_data)
                
        
        print("LOG: Data processing completed.")

    except Exception as e:
        print(f"ERROR: An error occurred: {e}")
        db.rollback()

    finally:
        next(db_gen, None)
        print("LOG: Database session closed.")


def get_countries():
    print("LOG: connecting to database...")
    db_gen = get_db()
    db = next(db_gen)

    print("LOG: fetching geographical data from API for countries...")
    url = "https://raw.githubusercontent.com/dr5hn/countries-states-cities-database/master/countries.json"
    data = fetch_json_from_github(url)


    for country_data in data:
        print(f"LOG: Processing country {country_data['name']}...")
        continent_id = get_continent_id_given_name(db, country_data["region"])
        if not continent_id:
            print(f"ERROR: Continent {country_data['region']} not found in database.")
            continue

        db_country = db.query(Country).filter(
            Country.code == country_data["iso3"],
            Country.name == country_data["name"]
        ).first()

        if db_country is None:
            print(f"LOG: Adding country {country_data['name']} to database...")
            db_country = add_country(db, country_data, continent_id)

    print("LOG: Data processing completed.")


def get_provinces():
    print("LOG: connecting to database...")
    db_gen = get_db()
    db = next(db_gen)

    print("LOG: fetching geographical data from API for provinces...")
    url = "https://raw.githubusercontent.com/dr5hn/countries-states-cities-database/master/states.json"
    data = fetch_json_from_github(url)

    for province_data in data:
        print(f"LOG: Processing province {province_data['name']}...")
        db_province = db.query(Province).filter(
            Province.code == province_data["state_code"],
            Province.name == province_data["name"]
        ).first()

        db_country = db.query(Country).filter(
            Country.name == province_data["country_name"]
        ).first()

        if not db_country:
            print(f"ERROR: Country {province_data["country_name"]} not found in database when attempting to add province.")
            continue

        if db_province is None:
            print(f"LOG: Adding province {province_data['name']} to database...")
            db_province = add_province(db, province_data, db_country.id)

    print("LOG: Data processing completed.")


def get_cities():
    print("LOG: connecting to database...")
    db_gen = get_db()
    db = next(db_gen)

    print("LOG: fetching geographical data from API for cities...")
    url = "https://raw.githubusercontent.com/dr5hn/countries-states-cities-database/master/cities.json"
    data = fetch_json_from_github(url)

    for city_data in data:
        print(f"LOG: Processing city {city_data['name']}...")
        db_country = db.query(Country).filter(
            Country.name == city_data["country_name"]
        ).first()

        if not db_country:
            print(f"ERROR: Country {city_data["country_name"]} not found in database when attempting to add city.")
            continue

        db_province = db.query(Province).filter(
            Country.name == city_data["state_name"]
        ).first()

        if not db_country:
            print(f"ERROR: province {city_data["state_name"]} not found in database when attempting to add city.")
            continue

        db_city = db.query(City).filter(
            City.name == city_data["name"],
            City.country_id == db_country.id
        ).first()

        if db_city is None:
            print(f"LOG: Adding city {city_data['name']} to database...")
            add_city(db, city_data, db_province.id, db_country.id)

    print("LOG: Data processing completed.")


def run_location_cron_job():
    get_continents()
    get_countries()
    get_provinces()
    get_cities()

if __name__ == "__main__":
    run_location_cron_job()
