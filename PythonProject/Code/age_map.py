import pandas as pd
import re
import json
import plotly.express as px
from pathlib import Path

# Set base directory to project root
BASE_DIR = Path(__file__).resolve().parent.parent
csv_path = BASE_DIR / "Average_Age_Per_County.cleaned.csv"
geojson_path = BASE_DIR / "ie.json"

df_age = pd.read_csv(csv_path)

df_age["County"] = df_age["County and State"].str.replace(" City", "").str.replace(" County", "").str.strip()


county_age = (
    df_age.groupby("County", as_index=False)["VALUE"].mean()
)


with open(geojson_path) as f:
    ireland_counties = json.load(f)

# Check a property's keys once (optional)
print(ireland_counties["features"][0]["properties"])

# Most SimpleMaps country files use "name" for the region name
geojson_county_field = "name"

# IMPORTANT: make our county labels match the GeoJSON naming
# (SimpleMaps uses "Clare", "Cavan", "Cork", etc. – same as your data)
county_age["County_key"] = county_age["County"].str.title().str.strip()

# 5. Plot
fig = px.choropleth(
    county_age,
    geojson=ireland_counties,
    locations="County_key",
    featureidkey=f"properties.{geojson_county_field}",
    color="VALUE",
    color_continuous_scale="Viridis",
    labels={"VALUE": "Average Age per County"},
)

fig.update_geos(
    fitbounds="geojson",
    visible=False
)

fig.update_layout(
    title="Average age per county in Ireland",
    margin={"r":0, "t":50, "l":0, "b":0}
)

fig.show()
