from flask import Blueprint, request, jsonify
from models import db
from app import text

from functions.graph_functions import create_bar_graph, create_line_chart


updated_graphs_bp = Blueprint("updated_graphs", __name__)


@updated_graphs_bp.route("/updated_graphs", methods=["GET"])
def updated_graphs():
    clicked_country = request.args.get("clicked_country")

    # if a specific country is clicked, filtering by that country - favorite animals
    sql_animal = text(
        "SELECT animal, COUNT(*) FROM person "
        "INNER JOIN countries "
        "ON person.own_country_id = countries.country_id "
        "INNER JOIN favorite_animals "
        "ON person.person_id = favorite_animals.person_id "
        "INNER JOIN animals "
        "ON favorite_animals.favorite_animal_id = animals.animal_id "
        "WHERE country = :clicked_country "
        "GROUP BY animal "
        "ORDER BY COUNT(*) DESC "
        "LIMIT 5"
    )

    graph_json_animal = create_bar_graph(
        sql_animal,
        x_label="Animal",
        y_label="Total",
        graph_title="Favorite animals TOP 5",
        filter_data={"clicked_country": clicked_country},
    )

    # if a specific country is clicked, filtering by that country - favorite countries
    sql_country = text(
        "SELECT fc.country, COUNT(*) "
        "FROM favorite_countries "
        "INNER JOIN countries AS fc ON favorite_countries.favorite_country_id = fc.country_id "
        "INNER JOIN person ON favorite_countries.person_id = person.person_id "
        "INNER JOIN countries AS oc ON person.own_country_id = oc.country_id "
        "WHERE oc.country = :clicked_country "
        "GROUP BY fc.country "
        "ORDER BY COUNT(*) DESC "
        "LIMIT 5"
    )

    graph_json_country = create_bar_graph(
        sql_country,
        x_label="Country",
        y_label="Total",
        graph_title="Favorite countries TOP 5",
        filter_data={"clicked_country": clicked_country},
    )

    # if a specific country is clicked, filtering by that country - line chart
    sql_line = text(
        "SELECT DATE(favorite_animals.created_on) AS dates, COUNT(*) "
        "FROM favorite_animals "
        "INNER JOIN person ON favorite_animals.person_id = person.person_id "
        "INNER JOIN countries ON person.own_country_id = countries.country_id "
        "WHERE country = :clicked_country "
        "GROUP BY dates "
        "ORDER BY dates "
    )

    graph_json_line = create_line_chart(
        sql_line,
        x_label="Date",
        y_label="Total",
        graph_title="Number of Entries per day",
        filter_data={"clicked_country": clicked_country},
    )

    # total entries from the clicked country
    sql_entries = text(
        "SELECT COUNT(*) FROM person "
        "INNER JOIN countries "
        "ON person.own_country_id = countries.country_id "
        "INNER JOIN favorite_animals "
        "ON person.person_id = favorite_animals.person_id "
        "WHERE country = :clicked_country "
    )
    total_entries = db.session.execute(
        sql_entries, {"clicked_country": clicked_country}
    ).fetchone()[0]

    graph_data = {
        "animal_chart": graph_json_animal,
        "country_chart": graph_json_country,
        "clicked_country_entries": total_entries,
        "line_chart": graph_json_line,
    }

    # returning the updated data as JSON using jsonify()
    return jsonify(graph_data)
