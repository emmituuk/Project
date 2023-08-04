// script for result.html

const map = document.getElementById("choropleth-map");
const clickedCountryResult = document.getElementById("clicked_country_result");
const clickedCountryName = document.getElementById("clicked_country");
const clickedCountryEntries = document.getElementById("clicked_country_entries");

let lastClickedCountry = null;

// function to add or remove a marker for the clicked country
function toggleMarkerForCountry(countryName, addMarker) {
  const markerIndex = mapJson.data.findIndex(
    (data) => data.locations[0] === countryName
  );

  if (markerIndex !== -1) {
    mapJson.data[markerIndex].marker = {
      line: { color: addMarker ? "Red" : "rgba(0, 0, 0, 0)", width: 2 },
    };
    mapJson.data[markerIndex].z = addMarker ? [0] : [null];
  } else if (addMarker) {
    // if a marker doesn't exist, add a new marker for the clicked country
    mapJson.data.push({
      colorscale: [
        [0, "rgba(0, 0, 0, 0)"],
        [1, "rgba(0, 0, 0, 0)"],
      ],
      locationmode: "country names",
      locations: [countryName],
      type: "choropleth",
      marker: { line: { color: "Red", width: 2 } },
      showscale: false,
      z: [0],
      text: [countryName],
      hoverinfo: "text",
    });
  }
}

map.on("plotly_click", function (data) {
  const clicked_country = data.points[0].location;

  // show the clicked_country_result div when click some country
  clickedCountryResult.style.display = "block";

  // update the clicked country name in the HTML
  clickedCountryName.textContent = clicked_country;

  // check if the same country is clicked again, reset charts and map marker
  if (clicked_country === lastClickedCountry) {
    resetCharts();
    return;
  }

  fetch("/updated_graphs?clicked_country=" + clicked_country)
    .then((response) => response.json())
    .then((data) => {
      // parsing the JSON data received from the response
      const graphJsonAnimal = JSON.parse(data.animal_chart);
      const graphJsonCountry = JSON.parse(data.country_chart);
      const graphJsonLine = JSON.parse(data.line_chart);
      const clickedCountryEntriesData = JSON.parse(
        data.clicked_country_entries
      );

      // updating the bar charts with the new data and layout
      Plotly.newPlot(
        "bar-graph-animal",
        graphJsonAnimal.data,
        graphJsonAnimal.layout
      );
      Plotly.newPlot(
        "bar-graph-country",
        graphJsonCountry.data,
        graphJsonCountry.layout
      );
      Plotly.newPlot("line-chart", graphJsonLine.data, graphJsonLine.layout);

      // updating the total entries from the clicked country
      clickedCountryEntries.textContent = clickedCountryEntriesData;

      // add the marker for the clicked country
      toggleMarkerForCountry(clicked_country, true);

      // remove marker for the previous country
      if (lastClickedCountry) {
        toggleMarkerForCountry(lastClickedCountry, false);
      }
      // updating the choropleth map
      Plotly.update("choropleth-map", mapJson.data, mapJson.layout);

      // storing the clicked country for reference
      lastClickedCountry = clicked_country;
    })
    .catch((error) => {
      console.error("Error:", error);
    });
});

// function to reset charts, marker and the clicked_country_result div
function resetCharts() {
  // reset charts
  function resetChart(chartId, chartData, chartLayout) {
    Plotly.newPlot(chartId, chartData, chartLayout);
  }
  resetChart("bar-graph-animal", graphJsonAnimal.data, graphJsonAnimal.layout);
  resetChart("bar-graph-country", graphJsonCountry.data, graphJsonCountry.layout);
  resetChart("line-chart", graphJsonLine.data, graphJsonLine.layout);

  // reset marker around the clicked country
  if (lastClickedCountry) {
    toggleMarkerForCountry(lastClickedCountry, false);
    Plotly.update("choropleth-map", mapJson.data, mapJson.layout);
  }
  lastClickedCountry = null;

  // hide the clicked_country_result div
  clickedCountryResult.style.display = "None";
}
