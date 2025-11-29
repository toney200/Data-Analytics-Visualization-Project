import pandas as pd
import re
import json
import plotly.express as px
from pathlib import Path

# Set base directory to project root
BASE_DIR = Path(__file__).resolve().parent.parent
csv_path = BASE_DIR / "ROA30.20251112T121150_cleaned.csv"
geojson_path = BASE_DIR / "ie.json"

# Read the driving test data
df = pd.read_csv(csv_path)

# Extract county from 'Driving Test Centre'
def extract_county(text):
    match = re.search(r"Co\.?\s+([A-Za-z]+)", str(text))
    return match.group(1) if match else None

df["County"] = df["Driving Test Centre"].apply(extract_county)

# Remove rows with NaN values in County and Number of Tests
df_clean = df.dropna(subset=['County', 'Number of Tests'])

# Aggregate total number of tests by county
county_tests = (
    df_clean.groupby("County", as_index=False)["Number of Tests"].sum()
)

# Load the Ireland counties GeoJSON
with open(geojson_path) as f:
    ireland_counties = json.load(f)

# Check a property's keys once (optional)
print(ireland_counties["features"][0]["properties"])

# Most SimpleMaps country files use "name" for the region name
geojson_county_field = "name"

# Make our county labels match the GeoJSON naming
county_tests["County_key"] = county_tests["County"].str.title().str.strip()

# Create choropleth map
fig = px.choropleth(
    county_tests,
    geojson=ireland_counties,
    locations="County_key",
    featureidkey=f"properties.{geojson_county_field}",
    color="Number of Tests",
    color_continuous_scale="Blues",
    labels={"Number of Tests": "Total Number of Tests"},
)

fig.update_geos(
    fitbounds="geojson",
    visible=False
)

fig.update_layout(
    title="Total Number of Driving Tests per County in Ireland",
    margin={"r":0, "t":50, "l":0, "b":0}
)

fig.show()