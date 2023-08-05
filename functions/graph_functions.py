import json
from models import db
import pandas as pd
import plotly
import plotly.graph_objs as go


# function for creating the bar charts - used result.py, updated_graphs.py
def create_bar_graph(sql, x_label, y_label, graph_title, filter_data=None):
    if filter_data:
        result = db.session.execute(sql, filter_data).fetchall()
    else:
        result = db.session.execute(sql).fetchall()

    x_data = [row[0] for row in result]
    y_data = [row[1] for row in result]

    graph_data = [go.Bar(x=x_data, y=y_data, marker=dict(color="rgb(69, 147, 165)"))]

    graph_layout = go.Layout(
        title=graph_title,
        xaxis=dict(title=x_label),
        yaxis=dict(title=y_label, tickvals=list(range(0, max(y_data) + 1))),
        plot_bgcolor="rgba(220, 201, 155, 0.17)",
    )
    graph_figure = go.Figure(data=graph_data, layout=graph_layout)

    return json.dumps(graph_figure, cls=plotly.utils.PlotlyJSONEncoder)


# function for creating the line chart - used result.py, updated_graphs.py
def create_line_chart(sql, x_label, y_label, graph_title, filter_data=None):
    if filter_data:
        result = db.session.execute(sql, filter_data).fetchall()
        # customized axis settings for filtered data
        dates = [row[0] for row in result]
        total = [row[1] for row in result]

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
        min_total = 0
        max_total = max(total)
        total_range = range(min_total, max_total + 1)

        graph_layout = go.Layout(
            title=graph_title,
            xaxis=dict(
                title=x_label,
                tickvals=date_range,
                ticktext=formatted_dates,
                tickangle=45,
            ),
            yaxis=dict(
                title=y_label,
                tickvals=list(total_range),
            ),
            plot_bgcolor="rgba(220, 201, 155, 0.17)",
        )
    else:
        result = db.session.execute(sql).fetchall()
        # default axis settings
        dates = [row[0] for row in result]
        total = [row[1] for row in result]

        graph_layout = go.Layout(
            title=graph_title,
            xaxis=dict(title=x_label),
            yaxis=dict(title=y_label),
            plot_bgcolor="rgba(220, 201, 155, 0.17)",
        )

    graph_data = [
        go.Scatter(
            x=dates,
            y=total,
            mode="lines+markers",
            marker=dict(color="rgb(69, 147, 165)"),
        )
    ]

    graph_figure_line = go.Figure(data=graph_data, layout=graph_layout)

    return json.dumps(graph_figure_line, cls=plotly.utils.PlotlyJSONEncoder)


# function to create the Chorolepth map - used result.py
def create_choropleth_map(sql, colorbar_title, graph_title):
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
        colorbar_title=colorbar_title,
        text=[row[0] for row in result],
        hoverinfo="text",
    )
    layout = go.Layout(
        title=graph_title,
        geo=dict(projection_type="natural earth"),
        height=400,
    )
    map_figure = go.Figure(data=data, layout=layout)
    return json.dumps(map_figure, cls=plotly.utils.PlotlyJSONEncoder)
