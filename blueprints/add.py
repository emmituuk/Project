from flask import Blueprint, render_template
from app import text
from functions.other_functions import move_to_end
from models import db

add_bp = Blueprint("add", __name__)


# fetch and prepare data for drop-down menus
@add_bp.route("/add")
def add():
    # fetch all countries from the database and sort alphabetically
    sql = text("SELECT country_id, country FROM countries")
    original_countries = db.session.execute(sql).fetchall()
    sorted_countries = sorted(original_countries, key=lambda x: x[1])

    # fetch all animals from the database and sort alphabetically
    sql = text("SELECT animal_id, animal FROM animals")
    original_animals = db.session.execute(sql).fetchall()
    alph_animals = sorted(original_animals, key=lambda x: x[1])

    # fetch the 'Other' animal from the database and move it to the end of the list
    sql = text("SELECT animal_id, animal FROM animals WHERE animal = 'Other'")
    other_elem = db.session.execute(sql).fetchall()[0]
    sorted_animals = move_to_end(alph_animals, other_elem)

    # fetch the 'Other' animal_id from the animals table
    sql = text("SELECT animal_id FROM animals WHERE animal = 'Other'")
    other_id_animals = db.session.execute(sql).fetchone()[0]

    return render_template(
        "add.html",
        sorted_countries=sorted_countries,
        sorted_animals=sorted_animals,
        other_id_animals=other_id_animals,
    )
