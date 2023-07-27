from flask import Flask
from flask import render_template, request, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from os import getenv
from sqlalchemy.sql import text  # for making queries
from livereload import Server

import json
import plotly
import plotly.graph_objs as go

from functions import move_to_end, is_valid_animal_id, is_valid_country_id
from error_handlers import (
    bad_request,
    unauthorized,
    forbidden,
    page_not_found,
    conflict,
    precondition_failed,
    too_many_requests,
    internal_server_error,
    bad_gateway,
    service_unavailable,
    gateway_timeout,
)

app = Flask(__name__)
app.debug = True
app.config.update(TEMPLATES_AUTO_RELOAD=True)

app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")
db = SQLAlchemy(app)

app.register_error_handler(400, bad_request)
app.register_error_handler(401, unauthorized)
app.register_error_handler(403, forbidden)
app.register_error_handler(404, page_not_found)
app.register_error_handler(409, conflict)
app.register_error_handler(412, precondition_failed)
app.register_error_handler(429, too_many_requests)
app.register_error_handler(500, internal_server_error)
app.register_error_handler(502, bad_gateway)
app.register_error_handler(503, service_unavailable)
app.register_error_handler(504, gateway_timeout)


@app.route("/check_email_availability", methods=["POST"])
def check_email_availability():
    email = request.json.get("email")
    sql = text("SELECT email FROM person WHERE email = :email")
    result = db.session.execute(sql, {"email": email}).fetchone()

    # true if email not found, false if email found
    is_email_available = not bool(result)

    return jsonify({"available": is_email_available})


@app.route("/")
def index():
    sql = text("SELECT person_id FROM favorite_animals")
    result = db.session.execute(sql).fetchall()
    return render_template("index.html", count=len(result))


@app.route("/add")
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


@app.route("/send", methods=["POST"])
def send():
    # values to the person table
    email = request.form["email"]
    first_name = request.form["first_name"]
    last_name = request.form["last_name"]
    own_country_id = request.form["own_country_id"]
    if not is_valid_country_id(text, db, own_country_id):
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

    # Get the person_id of the newly inserted person
    last_id = result.fetchone()[0]

    # values to the favorite_animals table
    favorite_animal_id = request.form["favorite_animal_id"]
    if not is_valid_animal_id(text, db, favorite_animal_id):
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
    if not is_valid_country_id(text, db, favorite_country_id):
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


@app.route("/result")
def result():
    # TOP 5 favorite animals
    sql = text(
        "SELECT animal AS favorite_animal, COUNT(*) AS total "
        "FROM favorite_animals "
        "INNER JOIN animals "
        "ON favorite_animals.favorite_animal_id = animals.animal_id "
        "GROUP BY favorite_animal "
        "ORDER BY total DESC "
        "LIMIT 5"
    )

    result = db.session.execute(sql).fetchall()

    # processing the data
    favorite_animal = [row[0] for row in result]
    total = [row[1] for row in result]

    # creating the graph using Plotly
    graph_data = [
        go.Bar(x=favorite_animal, y=total, marker=dict(color="rgb(69, 147, 165)"))
    ]

    graph_layout = go.Layout(
        title="Favorite animals TOP 5",
        xaxis=dict(title="Animal"),
        yaxis=dict(title="Total"),
        plot_bgcolor="rgba(220, 201, 155, 0.17)",
    )
    graph_figure_animal = go.Figure(data=graph_data, layout=graph_layout)

    graph_json_animal = json.dumps(
        graph_figure_animal, cls=plotly.utils.PlotlyJSONEncoder
    )

    # TOP 5 favorite countries
    sql = text(
        "SELECT country AS favorite_country, COUNT(*) AS total "
        "FROM favorite_countries "
        "INNER JOIN countries "
        "ON favorite_countries.favorite_country_id = countries.country_id "
        "GROUP BY favorite_country "
        "ORDER BY total DESC "
        "LIMIT 5"
    )
    result = db.session.execute(sql).fetchall()

    # processing the data
    favorite_country = [row[0] for row in result]
    total = [row[1] for row in result]

    # creating the graph using Plotly
    graph_data = [
        go.Bar(x=favorite_country, y=total, marker=dict(color="rgb(69, 147, 165)"))
    ]

    graph_layout = go.Layout(
        title="Favorite countries TOP 5",
        xaxis=dict(title="Country"),
        yaxis=dict(title="Total"),
        plot_bgcolor="rgba(220, 201, 155, 0.17)",
    )
    graph_figure_country = go.Figure(data=graph_data, layout=graph_layout)

    graph_json_country = json.dumps(
        graph_figure_country, cls=plotly.utils.PlotlyJSONEncoder
    )

    # creating the Choropleth Map
    sql = text(
        "SELECT country, COUNT(*) AS total FROM person "
        "INNER JOIN countries "
        "ON person.own_country_id = countries.country_id "
        "GROUP BY country"
    )
    result = db.session.execute(sql).fetchall()

    custom_colorscale = [
        [0.0, "rgb(220, 201, 155)"],
        [0.5, "rgb(179, 199, 184)"],
        [1.0, "rgb(43, 136, 162)"],
    ]

    data = go.Choropleth(
        locations=[row[0] for row in result],
        z=[row[1] for row in result],
        locationmode="country names",
        colorscale=custom_colorscale,
        # best colour:YlGnBu,YlOrRd, Earth
        colorbar=dict(title="Number of People"),
    )
    layout = go.Layout(
        title="Geographic Distribution of Favorite Entries",
        geo=dict(projection_type="natural earth"),
    )
    map_figure = go.Figure(data=data, layout=layout)
    map_json = json.dumps(map_figure, cls=plotly.utils.PlotlyJSONEncoder)

    # total favorite entries - same value also in the person table and the favorite_animals table
    sql = text("SELECT COUNT(*) FROM favorite_animals")
    total_entries = db.session.execute(sql).fetchone()[0]

    # using render_template to pass graphJSONs to html
    return render_template(
        "result.html",
        graph_json_animal=graph_json_animal,
        graph_json_country=graph_json_country,
        map_json=map_json,
        total_entries=total_entries,
    )


@app.route("/updated_bar_charts", methods=["GET"])
def updated_bar_charts():
    clicked_country = request.args.get("clicked_country")
    print(clicked_country)

    # if a specific country is clicked, filtering by that country
    sql = text(
        "SELECT animal, COUNT(*) FROM person "
        "INNER JOIN countries "
        "ON person.own_country_id = countries.country_id "
        "INNER JOIN favorite_animals "
        "ON person.person_id = favorite_animals.person_id "
        "INNER JOIN animals "
        "ON favorite_animals.favorite_animal_id = animals.animal_id "
        "WHERE country = :clicked_country "
        "GROUP BY animal "
        "ORDER BY count(*) DESC "
        "LIMIT 5"
    )
    result = db.session.execute(sql, {"clicked_country": clicked_country}).fetchall()

    # processing the data
    favorite_animal = [row[0] for row in result]
    total = [row[1] for row in result]

    # creating the graph using Plotly
    graph_data = [
        go.Bar(x=favorite_animal, y=total, marker=dict(color="rgb(69, 147, 165)"))
    ]

    graph_layout = go.Layout(
        title="Favorite animals TOP 5",
        xaxis=dict(title="Animal"),
        yaxis=dict(title="Total"),
        plot_bgcolor="rgba(220, 201, 155, 0.17)",
    )
    graph_figure_animal = go.Figure(data=graph_data, layout=graph_layout)

    graph_json_animal = json.dumps(
        graph_figure_animal, cls=plotly.utils.PlotlyJSONEncoder
    )

    # returning the updated data as JSON using jsonify()
    return jsonify(graph_json_animal)


if __name__ == "__main__":
    server = Server(app.wsgi_app)
    server.serve(port=5000)
