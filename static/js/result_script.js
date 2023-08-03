// script for result.html

// variable to store the last clicked country
let lastClickedCountry = null;

// function to add a marker for the clicked country
function addMarkerForCountry(countryName) {
  // check if a marker already exists for the clicked country
  const existingMarkerIndex = mapJson.data.findIndex(
    (data) => data.locations[0] === countryName
  );

  if (existingMarkerIndex === -1) {
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
  } else {
    // if a marker already exists, update its properties to highlight the selected country
    mapJson.data[existingMarkerIndex].marker = {
      line: { color: "Red", width: 2 },
    };
    mapJson.data[existingMarkerIndex].z = [0];
  }
}

function removeMarkerForCountry(countryName) {
  const previousMarkerIndex = mapJson.data.findIndex(
    (data) => data.locations[0] === countryName
  );
  if (previousMarkerIndex !== -1) {
    mapJson.data[previousMarkerIndex].marker = {
      line: { color: "rgba(0, 0, 0, 0)", width: 2 },
    };
    mapJson.data[previousMarkerIndex].z = [null];
  }
}

const map = document.getElementById("choropleth-map");
map.on("plotly_click", function (data) {
  const clicked_country = data.points[0].location;

  // show the clicked_country_result div when click some country
  document.getElementById("clicked_country_result").style.display = "block";

  // update the clicked country name in the HTML
  document.getElementById("clicked_country").textContent = clicked_country;

  // check if the same country is clicked again, reset charts and map marker
  if (clicked_country === lastClickedCountry) {
    resetCharts();
    return;
  }

  fetch("/updated_bar_charts?clicked_country=" + clicked_country)
    .then((response) => response.json())
    .then((data) => {
      // parsing the JSON data received from the response
      const graphJsonAnimal = JSON.parse(data.animal_chart);
      const graphJsonCountry = JSON.parse(data.country_chart);
      const clickedCountryEntries = JSON.parse(data.clicked_country_entries);
      const graphJsonLine = JSON.parse(data.line_chart);

      // total entries from the clicked country
      document.getElementById("clicked_country_entries").textContent =
        clickedCountryEntries;

      // updating the bar chart with the new data and layout
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

      // add the marker for the clicked country
      addMarkerForCountry(clicked_country);

      // remove marker for the previous country
      if (lastClickedCountry) {
        const previousMarkerIndex = mapJson.data.findIndex(
          (data) => data.locations[0] === lastClickedCountry
        );
        if (previousMarkerIndex !== -1) {
          mapJson.data[previousMarkerIndex].marker = {
            line: { color: "rgba(0, 0, 0, 0)", width: 2 },
          };
          mapJson.data[previousMarkerIndex].z = [null];
        }
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

  // reset marker around the clicked country
  if (lastClickedCountry) {
    removeMarkerForCountry(lastClickedCountry);
    Plotly.update("choropleth-map", mapJson.data, mapJson.layout);
  }
  lastClickedCountry = null;

  // hide the clicked_country_result div
  document.getElementById("clicked_country_result").style.display = "None";
}
