from flask import Blueprint, render_template
from models import db
from app import text

from functions.graph_functions import (
    create_bar_graph,
    create_line_chart,
    create_choropleth_map,
)

result_bp = Blueprint("result", __name__)


@result_bp.route("/result")
def result():
    # fetch and create bar graph for TOP 5 favorite animals
    sql_animals = text(
        "SELECT animal AS favorite_animal, COUNT(*) AS total "
        "FROM favorite_animals "
        "INNER JOIN animals "
        "ON favorite_animals.favorite_animal_id = animals.animal_id "
        "GROUP BY favorite_animal "
        "ORDER BY total DESC "
        "LIMIT 5"
    )

    graph_json_animal = create_bar_graph(
        sql_animals,
        x_label="Animal",
        y_label="Total",
        graph_title="Favorite animals TOP 5",
    )

    # fetch and create bar graph for TOP 5 favorite countries
    sql_countries = text(
        "SELECT country AS favorite_country, COUNT(*) AS total "
        "FROM favorite_countries "
        "INNER JOIN countries "
        "ON favorite_countries.favorite_country_id = countries.country_id "
        "GROUP BY favorite_country "
        "ORDER BY total DESC "
        "LIMIT 5"
    )

    graph_json_country = create_bar_graph(
        sql_countries,
        x_label="Country",
        y_label="Total",
        graph_title="Favorite countries TOP 5",
    )

    # fetch and create graph for the Choropleth Map
    sql_map = text(
        "SELECT country, COUNT(*) AS total FROM person "
        "INNER JOIN countries "
        "ON person.own_country_id = countries.country_id "
        "GROUP BY country"
    )

    map_json = create_choropleth_map(
        sql_map,
        colorbar_title="Number of Entries",
        graph_title="Geographic Distribution of Favorite Entries",
    )

    # fetch and create line chart for number of entries per day
    sql_line = text(
        "SELECT DATE(created_on), COUNT(*) FROM favorite_animals "
        "GROUP BY DATE(created_on) "
        "ORDER BY DATE(created_on)"
    )

    graph_json_line = create_line_chart(
        sql_line,
        x_label="Date",
        y_label="Total",
        graph_title="Number of Entries per day",
    )

    # fetch total favorite entries
    sql_entries = text("SELECT COUNT(*) FROM favorite_animals")
    total_entries = db.session.execute(sql_entries).fetchone()[0]

    # using render_template to pass graphJSONs to html
    return render_template(
        "result.html",
        graph_json_animal=graph_json_animal,
        graph_json_country=graph_json_country,
        graph_json_line=graph_json_line,
        map_json=map_json,
        total_entries=total_entries,
    )
