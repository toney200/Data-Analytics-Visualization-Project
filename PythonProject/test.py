import json
import pandas as pd
import plotly.express as px

# Load your GeoJSON
with open("C:/Users/ciara/PycharmProjects/PythonProject/Counties.geojson", encoding="utf-8") as f:
    geo_map = json.load(f)

# Extract all county names from the file
counties = [f["properties"]["COUNTY"] for f in geo_map["features"]]

# Make a dummy dataframe
df_test = pd.DataFrame({
    "County": counties,
    "Value": [1] * len(counties)
})

fig = px.choropleth(
    df_test,
    geojson=geo_map,
    locations="County",
    featureidkey="properties.COUNTY",
    color="Value"
)

fig.update_geos(fitbounds="geojson", visible=False)
fig.show()
