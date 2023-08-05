from flask import Blueprint, render_template
from app import text
from models import db

add_bp = Blueprint("add", __name__)


# fetch and prepare data for drop-down menus
@add_bp.route("/add")
def add():
    # fetch all countries from the database
    sql = text("SELECT country_id, country FROM countries")
    original_countries = db.session.execute(sql).fetchall()
    # Sort the countries alphabetically based on their names.
    # The key=lambda x: x[1] specifies that the sorting should be based on
    # the second element of each tuple, which is the country name.
    sorted_countries = sorted(original_countries, key=lambda x: x[1])

    # fetch all animals from the database and sort alphabetically
    sql = text("SELECT animal_id, animal FROM animals")
    original_animals = db.session.execute(sql).fetchall()
    alph_animals = sorted(original_animals, key=lambda x: x[1])

    # find the tuple (animal_id, 'Other') in the sorted animals list.
    target_animal = "Other"
    other_elem = None

    for animal_id, animal in alph_animals:
        if animal == target_animal:
            other_elem = (animal_id, animal)
            break

    # move the 'Other' element (animal_id, 'Other') to the end of the list
    alph_animals.remove(other_elem)
    alph_animals.append(other_elem)

    # the list 'sorted_animals' now contains animals sorted alphabetically, with 'Other' moved to the end
    sorted_animals = alph_animals

    # get the animal_id associated with 'Other'
    other_id_animals = other_elem[0]

    return render_template(
        "add.html",
        sorted_countries=sorted_countries,
        sorted_animals=sorted_animals,
        other_id_animals=other_id_animals,
    )
