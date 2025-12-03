import pandas as pd
import re
import json
import plotly.express as px
from pathlib import Path

# Set base directory to project root
BASE_DIR = Path(__file__).resolve().parent.parent
csv_path = BASE_DIR / "ROA30.20251112T121150_cleaned.csv"
geojson_path = BASE_DIR / "ie.json"
population_path = BASE_DIR / "PEA08.20251203T161259.csv"

# Read the driving test data and population data
df = pd.read_csv(csv_path)
df_population = pd.read_csv(population_path)

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

# Prepare population data
df_population['County'] = df_population['County'].str.replace('Co. ', '', regex=False)
df_population['Population'] = df_population['VALUE'] * 1000  # Convert from thousands
population_lookup = df_population[df_population['County'] != 'Ireland'].set_index('County')['Population'].to_dict()

# Add population data to county tests
county_tests['Population'] = county_tests['County'].map(population_lookup)
county_tests = county_tests.dropna(subset=['Population'])

# Calculate tests per 1,000 population
county_tests['Tests_per_1000'] = (county_tests['Number of Tests'] / county_tests['Population']) * 1000

# Load the Ireland counties GeoJSON
with open(geojson_path) as f:
    ireland_counties = json.load(f)

# Check a property's keys once (optional)
print(ireland_counties["features"][0]["properties"])

# Most SimpleMaps country files use "name" for the region name
geojson_county_field = "name"

# Make our county labels match the GeoJSON naming
county_tests["County_key"] = county_tests["County"].str.title().str.strip()

# Create choropleth map using tests per 1,000 population
fig = px.choropleth(
    county_tests,
    geojson=ireland_counties,
    locations="County_key",
    featureidkey=f"properties.{geojson_county_field}",
    color="Tests_per_1000",
    color_continuous_scale="Blues",
    labels={"Tests_per_1000": "Tests per 1,000 Population"},
    hover_data={"Number of Tests": True, "Population": ":,.0f"}
)

fig.update_geos(
    fitbounds="geojson",
    visible=False
)

fig.update_layout(
    title="Driving Tests per 1,000 Population by County in Ireland",
    margin={"r":0, "t":50, "l":0, "b":0}
)

fig.show()