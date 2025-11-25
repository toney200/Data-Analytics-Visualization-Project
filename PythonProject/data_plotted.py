import pandas as pd
import re
import json
import plotly.express as px

# 1. Load your RSA data
df = pd.read_csv("C:/Users/ciara/PycharmProjects/PythonProject/driving_test_data.csv")

# 2. Extract county from 'Driving Test Centre'
def extract_county(text):
    match = re.search(r"Co\.?\s+([A-Za-z]+)", str(text))
    return match.group(1) if match else None

df["County"] = df["Driving Test Centre"].apply(extract_county)

# 3. Aggregate mean pass rate per county
county_pass_rate = (
    df.groupby("County", as_index=False)["Pass Rate"].mean()
)

# 4. Load the SIMPLE Ireland counties GeoJSON (from SimpleMaps)
with open("C:/Users/ciara/PycharmProjects/PythonProject/ie.json") as f:
    ireland_counties = json.load(f)

# Check a property's keys once (optional)
print(ireland_counties["features"][0]["properties"])

# Most SimpleMaps country files use "name" for the region name
geojson_county_field = "name"

# IMPORTANT: make our county labels match the GeoJSON naming
# (SimpleMaps uses "Clare", "Cavan", "Cork", etc. – same as your data)
county_pass_rate["County_key"] = county_pass_rate["County"].str.title().str.strip()

# 5. Plot
fig = px.choropleth(
    county_pass_rate,
    geojson=ireland_counties,
    locations="County_key",
    featureidkey=f"properties.{geojson_county_field}",
    color="Pass Rate",
    color_continuous_scale="Viridis",
    labels={"Pass Rate": "Average Driving Test Pass Rate (%)"},
)

fig.update_geos(
    fitbounds="geojson",
    visible=False
)

fig.update_layout(
    title="Driving Test Pass Rate by County (Ireland)",
    margin={"r":0, "t":50, "l":0, "b":0}
)

fig.show()
