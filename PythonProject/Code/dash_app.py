import re
import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output

# ======================================================
# 1. LOAD ALL DATA (mirror your script logic)
# ======================================================

BASE_DIR = Path(__file__).resolve().parent.parent

# Main datasets
driving_path = BASE_DIR / "driving_test_data.csv"
age_path = BASE_DIR / "Average_Age_Per_County.cleaned.csv"
geo_path = BASE_DIR / "ie.json"
driving_monthly_path = BASE_DIR / "ROA30.20251112T121150_cleaned.csv"

df_driving = pd.read_csv(driving_path)
df_age = pd.read_csv(age_path)

# Extract county (consistent with multiple scripts)
def extract_county(text):
    match = re.search(r"Co\.?\s+([A-Za-z]+)", str(text))
    return match.group(1) if match else None

df_driving["County"] = df_driving["Driving Test Centre"].apply(extract_county)

# -----------------------------
# Pass rate per county
# -----------------------------
county_pass = (
    df_driving
    .dropna(subset=["Pass Rate", "County"])
    .groupby("County", as_index=False)["Pass Rate"]
    .mean()
)

# -----------------------------
# Average age per county
# -----------------------------
df_age["County"] = (
    df_age["County and State"]
    .str.replace(" City", "", regex=False)
    .str.replace(" County", "", regex=False)
    .str.strip()
)

county_age = (
    df_age
    .dropna(subset=["County", "VALUE"])
    .groupby("County", as_index=False)["VALUE"]
    .mean()
)

# -----------------------------
# County test counts
# -----------------------------
df_driving_tests = df_driving.dropna(subset=["County", "Number of Tests"])
county_tests = (
    df_driving_tests
    .groupby("County", as_index=False)["Number of Tests"]
    .sum()
)

# -----------------------------
# Merge for scatter Age vs Pass Rate
# -----------------------------
merged_age_pass = pd.merge(county_pass, county_age, on="County", how="inner")
merged_age_pass = merged_age_pass.rename(columns={"VALUE": "Average_Age"})

# -----------------------------
# Merge for Pass Rate vs Number of Tests (county)
# -----------------------------
county_pass_tests = pd.merge(county_pass, county_tests, on="County", how="inner")


# ======================================================
# 2. LOAD GEOJSON (SimpleMaps Ireland)
# ======================================================

with open(geo_path, "r") as f:
    geojson = json.load(f)

GEO_KEY = "name"  # simplemaps property key

def geo_key_clean(x):
    return str(x).title().strip()

county_pass["County_key"] = county_pass["County"].apply(geo_key_clean)
county_age["County_key"] = county_age["County"].apply(geo_key_clean)
county_tests["County_key"] = county_tests["County"].apply(geo_key_clean)


# ======================================================
# 3. PREBUILD ALL FIGURES
# ======================================================

# ------------------------------------------------------
# FIG 1: Scatter — Pass Rate vs Average Age
# ------------------------------------------------------
fig_scatter_age = px.scatter(
    merged_age_pass,
    x="Average_Age",
    y="Pass Rate",
    hover_data=["County"],
    title="Pass Rate vs Average Age (County Level)",
    trendline="ols"
)
fig_scatter_age.update_layout(margin=dict(l=20, r=20, t=40, b=20))

# ------------------------------------------------------
# FIG 2: Pass Rate Choropleth Map
# ------------------------------------------------------
fig_pass_map = px.choropleth(
    county_pass,
    geojson=geojson,
    locations="County_key",
    featureidkey=f"properties.{GEO_KEY}",
    color="Pass Rate",
    color_continuous_scale="Viridis",
    title="Driving Test Pass Rate by County"
)
fig_pass_map.update_geos(fitbounds="geojson", visible=False)
fig_pass_map.update_layout(margin=dict(l=0, r=0, t=50, b=0))

# ------------------------------------------------------
# FIG 3: Average Age Map
# ------------------------------------------------------
fig_age_map = px.choropleth(
    county_age,
    geojson=geojson,
    locations="County_key",
    featureidkey=f"properties.{GEO_KEY}",
    color="VALUE",
    color_continuous_scale="Viridis",
    labels={"VALUE": "Average Age"},
    title="Average Age by County"
)
fig_age_map.update_geos(fitbounds="geojson", visible=False)
fig_age_map.update_layout(margin=dict(l=0, r=0, t=50, b=0))

# ------------------------------------------------------
# FIG 4: Number of Tests Map
# (from tests_map.py)
# ------------------------------------------------------
fig_tests_map = px.choropleth(
    county_tests,
    geojson=geojson,
    locations="County_key",
    featureidkey=f"properties.{GEO_KEY}",
    color="Number of Tests",
    color_continuous_scale="Blues",
    title="Total Number of Driving Tests by County"
)
fig_tests_map.update_geos(fitbounds="geojson", visible=False)
fig_tests_map.update_layout(margin=dict(l=0, r=0, t=50, b=0))

# ------------------------------------------------------
# FIG 5: Pass Rate vs Number of Tests (county-level)
# ------------------------------------------------------
fig_pass_vs_tests = px.scatter(
    county_pass_tests,
    x="Number of Tests",
    y="Pass Rate",
    hover_data=["County"],
    trendline="ols",
    title="Pass Rate vs Number of Tests (County Level)"
)
fig_pass_vs_tests.update_layout(margin=dict(l=20, r=20, t=40, b=20))

# ------------------------------------------------------
# FIG 6: Monthly Pass Rates Over Time
# (from visualize_pass_rates.py)
# ------------------------------------------------------
df_monthly = pd.read_csv(driving_monthly_path)

df_monthly_filtered = df_monthly[df_monthly["Driving Test Centre"] == "All driving test centres"].copy()

df_monthly_filtered["Year"] = df_monthly_filtered["Month"].str.split().str[0]
df_monthly_filtered["Month_Name"] = df_monthly_filtered["Month"].str.split().str[1]

month_order = [
    "January","February","March","April","May","June",
    "July","August","September","October","November","December"
]

df_monthly_filtered["Month_Num"] = pd.Categorical(
    df_monthly_filtered["Month_Name"],
    categories=month_order,
    ordered=True
)

monthly_grouped = (
    df_monthly_filtered
    .groupby(["Year", "Month_Num"], observed=True)["Pass Rate"]
    .mean()
    .reset_index()
)

fig_monthly = go.Figure()

years = sorted(monthly_grouped["Year"].unique())
palette = px.colors.qualitative.Plotly

for i, y in enumerate(years):
    d = monthly_grouped[monthly_grouped["Year"] == y]
    fig_monthly.add_trace(go.Scatter(
        x=d["Month_Num"].astype(str),
        y=d["Pass Rate"],
        mode="lines+markers",
        name=str(y),
        line=dict(width=2, color=palette[i % len(palette)])
    ))

fig_monthly.update_layout(
    title="Monthly Pass Rates by Year",
    xaxis_title="Month",
    yaxis_title="Pass Rate (%)",
    margin=dict(l=20, r=20, t=40, b=20),
    height=600
)


# ======================================================
# 4. DASH APP LAYOUT (TABS)
# ======================================================

app = Dash(__name__)

# Header and footer styles: blue -> cyan gradient
header_style = {
    "background": "linear-gradient(90deg, #232b91, #00f9ff)",
    "color": "white",
    "padding": "18px 24px",
    "textAlign": "center",
    "borderRadius": "8px",
    "boxShadow": "0 2px 6px rgba(0,0,0,0.15)",
}

footer_style = {
    "background": "linear-gradient(90deg, #232b91, #00f9ff)",
    "color": "white",
    "padding": "12px 16px",
    "textAlign": "center",
    "borderRadius": "6px",
    "fontSize": "14px",
    "position": "fixed",
    "left": 0,
    "right": 0,
    "bottom": 0,
    "width": "100%",
    "zIndex": 1000,
}

app.layout = html.Div([
    # Header (gradient)
    html.Div([
        html.H1("Driving Test Analytics Dashboard", style={"margin": "0", "fontWeight": "700"}),
        html.Div("Interactive visualisations of driving test pass rates and related metrics", style={"opacity": "0.9", "marginTop": "6px"}),
    ], style=header_style),

    # Modern styled tabs
    dcc.Tabs(
        id="tabs",
        value="tab_scatter_age",
        children=[
            dcc.Tab(label="Pass Rate vs Age", value="tab_scatter_age"),
            dcc.Tab(label="Pass Rate Map", value="tab_pass_map"),
            dcc.Tab(label="Average Age Map", value="tab_age_map"),
            dcc.Tab(label="Tests Map", value="tab_tests_map"),
            dcc.Tab(label="Pass Rate vs Tests", value="tab_pass_tests"),
            dcc.Tab(label="Monthly Trends", value="tab_monthly"),
        ]
    ),

    html.Div(id="tab-content", style={"marginTop": "20px"}),

    # Footer (gradient)
    html.Div([
        html.Div("© 2025 Driving Test Analytics", style={"fontWeight": "600"}),
        html.Div("Built with Plotly Dash", style={"opacity": "0.9", "marginTop": "4px"}),
    ], style=footer_style)
])


# ======================================================
# 5. CALLBACK — Render correct figure per tab
# ======================================================

@app.callback(
    Output("tab-content", "children"),
    Input("tabs", "value")
)
def render_tab(tab):
    if tab == "tab_scatter_age":
        return dcc.Graph(figure=fig_scatter_age, style={"height": "700px"})
    elif tab == "tab_pass_map":
        return dcc.Graph(figure=fig_pass_map, style={"height": "700px"})
    elif tab == "tab_age_map":
        return dcc.Graph(figure=fig_age_map, style={"height": "700px"})
    elif tab == "tab_tests_map":
        return dcc.Graph(figure=fig_tests_map, style={"height": "700px"})
    elif tab == "tab_pass_tests":
        return dcc.Graph(figure=fig_pass_vs_tests, style={"height": "700px"})
    elif tab == "tab_monthly":
        return dcc.Graph(figure=fig_monthly, style={"height": "700px"})
    return html.Div("Tab not found.")


# ======================================================
# 6. RUN SERVER
# ======================================================

if __name__ == "__main__":
    app.run(debug=True)
