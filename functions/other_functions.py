from models import db


# function for validating animal ID - used send.py
def is_valid_animal_id(text, animal_id):
    sql = text("SELECT COUNT(*) FROM animals WHERE animal_id = :animal_id")
    result = db.session.execute(sql, {"animal_id": animal_id}).scalar()
    return result == 1


# function for validating country ID - used send.py
def is_valid_country_id(text, country_id):
    sql = text("SELECT COUNT(*) FROM countries WHERE country_id = :country_id")
    result = db.session.execute(sql, {"country_id": country_id}).scalar()
    return result == 1
