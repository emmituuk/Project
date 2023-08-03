from flask import Blueprint, render_template
from models import db
from flask import render_template
from app import text

import json
import plotly
import plotly.graph_objs as go

result_bp = Blueprint("result", __name__)


@result_bp.route("/result")
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
        colorbar_title="Number of Entries",
        colorbar=dict(x=-0.2, y=0.54),
        text=[row[0] for row in result],
        hoverinfo="text",
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

    # values and creating the line chart, how many values added per day
    sql = text(
        "SELECT DATE(created_on), COUNT(*) FROM favorite_animals "
        "GROUP BY DATE(created_on) "
        "ORDER BY DATE(created_on)"
    )

    result = db.session.execute(sql).fetchall()
    date = [row[0] for row in result]
    total = [row[1] for row in result]

    graph_data = [
        go.Scatter(
            x=date,
            y=total,
            mode="lines+markers",
            marker=dict(color="rgb(69, 147, 165)"),
        )
    ]

    graph_layout = go.Layout(
        title="Number of Entries per day",
        xaxis=dict(title="Date"),
        yaxis=dict(title="Total"),
        plot_bgcolor="rgba(220, 201, 155, 0.17)",
    )
    graph_figure_line = go.Figure(data=graph_data, layout=graph_layout)

    graph_json_line = json.dumps(graph_figure_line, cls=plotly.utils.PlotlyJSONEncoder)

    # using render_template to pass graphJSONs to html
    return render_template(
        "result.html",
        graph_json_animal=graph_json_animal,
        graph_json_country=graph_json_country,
        map_json=map_json,
        total_entries=total_entries,
        graph_json_line=graph_json_line,
    )
