from flask import Blueprint, request, render_template, redirect
from app import text
from models import db
from functions.other_functions import is_valid_animal_id, is_valid_country_id

send_bp = Blueprint("send", __name__)


@send_bp.route("/send", methods=["POST"])
def send():
    # values to the person table
    email = request.form["email"]
    first_name = request.form["first_name"]
    last_name = request.form["last_name"]
    own_country_id = request.form["own_country_id"]
    if not is_valid_country_id(text, own_country_id):
        return (
            render_template("error.html", error_message="Invalid own country ID."),
            400,
        )
    sql = text(
        "INSERT INTO person (first_name, last_name, email, own_country_id, created_on)"
        "VALUES (:first_name, :last_name, :email, :own_country_id, CURRENT_TIMESTAMP)"
        "RETURNING person_id"
    )
    result = db.session.execute(
        sql,
        {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "own_country_id": own_country_id,
        },
    )

    # get the person_id of the newly inserted person
    last_id = result.fetchone()[0]

    # values to the favorite_animals table
    favorite_animal_id = request.form["favorite_animal_id"]
    if not is_valid_animal_id(text, favorite_animal_id):
        return (
            render_template("error.html", error_message="Invalid favorite animal ID."),
            400,
        )
    other_id_animals = db.session.execute(
        text("SELECT animal_id FROM animals WHERE animal = 'Other'")
    ).fetchone()[0]
    other_animal = (
        request.form["other_animal"]
        if favorite_animal_id == str(other_id_animals)
        else None
    )
    sql = text(
        "INSERT INTO favorite_animals(person_id, favorite_animal_id, other_animal, created_on)"
        "VALUES (:last_id, :favorite_animal_id, :other_animal , CURRENT_TIMESTAMP)"
    )
    db.session.execute(
        sql,
        {
            "last_id": last_id,
            "favorite_animal_id": favorite_animal_id,
            "other_animal": other_animal,
        },
    )
    db.session.commit()

    # values to the favorite_countries table
    favorite_country_id = request.form["favorite_country_id"]
    if not is_valid_country_id(text, favorite_country_id):
        return (
            render_template("error.html", error_message="Invalid favorite country ID."),
            400,
        )
    sql = text(
        "INSERT INTO favorite_countries(person_id, favorite_country_id, created_on)"
        "VALUES (:last_id, :favorite_country_id, CURRENT_TIMESTAMP)"
    )
    db.session.execute(
        sql, {"last_id": last_id, "favorite_country_id": favorite_country_id}
    )
    db.session.commit()

    return redirect("/")
