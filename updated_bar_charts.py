from flask import Blueprint, request, jsonify
from models import db
from app import text

import json
import plotly
import plotly.graph_objs as go
import pandas as pd


updated_bar_charts_bp = Blueprint("updated_bar_charts", __name__)


@updated_bar_charts_bp.route("/updated_bar_charts", methods=["GET"])
def updated_bar_charts():
    clicked_country = request.args.get("clicked_country")

    # if a specific country is clicked, filtering by that country - favorite animals
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
        "ORDER BY COUNT(*) DESC "
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
        yaxis=dict(
            title="Total",
            tickvals=list(range(0, max(total) + 1)),
        ),
        plot_bgcolor="rgba(220, 201, 155, 0.17)",
    )
    graph_figure_animal = go.Figure(data=graph_data, layout=graph_layout)

    graph_json_animal = json.dumps(
        graph_figure_animal, cls=plotly.utils.PlotlyJSONEncoder
    )

    # if a specific country is clicked, filtering by that country - favorite countries

    sql = text(
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
    result = db.session.execute(sql, {"clicked_country": clicked_country}).fetchall()

    # processing the data
    favorite_country = [row[0] for row in result]
    total = [row[1] for row in result]

    # creating the graph using Plotly
    graph_data = [
        go.Bar(
            x=favorite_country,
            y=total,
            marker=dict(color="rgb(69, 147, 165)"),
        )
    ]

    graph_layout = go.Layout(
        title="Favorite countries TOP 5",
        xaxis=dict(title="Country"),
        yaxis=dict(
            title="Total",
            tickvals=list(range(0, max(total) + 1)),
        ),
        plot_bgcolor="rgba(220, 201, 155, 0.17)",
    )
    graph_figure_country = go.Figure(data=graph_data, layout=graph_layout)

    graph_json_country = json.dumps(
        graph_figure_country, cls=plotly.utils.PlotlyJSONEncoder
    )

    # if a specific country is clicked, filtering by that country - line chart
    sql = text(
        "SELECT DATE(favorite_animals.created_on) AS d, COUNT(*) "
        "FROM favorite_animals "
        "INNER JOIN person ON favorite_animals.person_id = person.person_id "
        "INNER JOIN countries ON person.own_country_id = countries.country_id "
        "WHERE country = :clicked_country "
        "GROUP BY d "
        "ORDER BY d "
    )
    result = db.session.execute(sql, {"clicked_country": clicked_country}).fetchall()

    dates = [row[0] for row in result]
    total = [row[1] for row in result]

    graph_data = [
        go.Scatter(
            x=dates,
            y=total,
            mode="lines+markers",
            marker=dict(color="rgb(69, 147, 165)"),
        )
    ]

    # x-axis: making tickvals and text 'MMM DD' to the layout of the line chart
    first_date = pd.to_datetime(min(dates))
    last_date = pd.to_datetime(max(dates))
    num_unique_dates = len(set(dates))

    date_difference = (last_date - first_date).days

    if num_unique_dates == 2 and date_difference == 1:
        # if only two different dates next to each other, show every day
        date_range = pd.date_range(start=first_date, end=last_date, freq="D")
    else:
        date_range = pd.date_range(start=first_date, end=last_date, freq="2D")

    formatted_dates = [date.strftime("%b %d") for date in date_range]

    # y-axis: making ticvals
    min_total = min(total)
    max_total = max(total)
    total_range = range(min_total, max_total + 1)

    graph_layout = go.Layout(
        title="Number of Entries per day",
        xaxis=dict(
            title="Date", tickvals=date_range, ticktext=formatted_dates, tickangle=45
        ),
        yaxis=dict(
            title="Total",
            tickvals=list(total_range),
            tickformat="d",
        ),
        plot_bgcolor="rgba(220, 201, 155, 0.17)",
    )
    graph_figure_line = go.Figure(data=graph_data, layout=graph_layout)

    graph_json_line = json.dumps(graph_figure_line, cls=plotly.utils.PlotlyJSONEncoder)

    # total entries from the clicked country
    sql = text(
        "SELECT COUNT(*) FROM person "
        "INNER JOIN countries "
        "ON person.own_country_id = countries.country_id "
        "INNER JOIN favorite_animals "
        "ON person.person_id = favorite_animals.person_id "
        "WHERE country = :clicked_country "
    )
    total_entries = db.session.execute(
        sql, {"clicked_country": clicked_country}
    ).fetchone()[0]

    graph_data = {
        "animal_chart": graph_json_animal,
        "country_chart": graph_json_country,
        "clicked_country_entries": total_entries,
        "line_chart": graph_json_line,
    }

    # returning the updated data as JSON using jsonify()
    return jsonify(graph_data)
