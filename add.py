from flask import Blueprint, render_template
from app import text
from functions import move_to_end
from models import db

add_bp = Blueprint("add", __name__)


@add_bp.route("/add")
def add():
    # next making the drop-down menu values for own_country_id and favorite_country_id
    sql = text("SELECT country_id, country FROM countries")
    original_countries = db.session.execute(sql).fetchall()
    # sorts countries by alphabetically
    sorted_countries = sorted(original_countries, key=lambda x: x[1])

    # next making the drop-down menu values for favorite_animals_id
    sql = text("SELECT animal_id, animal FROM animals")
    original_animals = db.session.execute(sql).fetchall()
    alph_animals = sorted(original_animals, key=lambda x: x[1])
    # fetches the row of the query result and returns a row as a list of tuples
    sql = text("SELECT animal_id, animal FROM animals WHERE animal = 'Other'")
    other_elem = db.session.execute(sql).fetchall()[0]
    # moves other_elem to the end of the list
    sorted_animals = move_to_end(alph_animals, other_elem)

    # finds the 'Other' value's id from the animals table
    sql = text("SELECT animal_id FROM animals WHERE animal = 'Other'")
    other_id_animals = db.session.execute(sql).fetchone()[0]

    return render_template(
        "add.html",
        sorted_countries=sorted_countries,
        sorted_animals=sorted_animals,
        other_id_animals=other_id_animals,
    )
