import re
from pathlib import Path

import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output

# --------------------------------------------------
# Load and prepare data; no changes to existing files
# --------------------------------------------------

# Match the pattern used in your other scripts: CSVs live one level up
BASE_DIR = Path(__file__).resolve().parent.parent

driving_data_path = BASE_DIR / "driving_test_data.csv"
age_data_path = BASE_DIR / "Average_Age_Per_County.cleaned.csv"

df_driving = pd.read_csv(driving_data_path)
df_age = pd.read_csv(age_data_path)

def extract_county(text: str):
    """
    Extract the county name from 'Driving Test Centre' strings like:
    'Athlone, Co. Westmeath' -> 'Westmeath'
    """
    match = re.search(r"Co\.?\s+([A-Za-z]+)", str(text))
    return match.group(1) if match else None

# Add 'County' to driving data
df_driving["County"] = df_driving["Driving Test Centre"].apply(extract_county)

# Aggregate mean pass rate per county
county_pass_rate = (
    df_driving
    .dropna(subset=["County", "Pass Rate"])
    .groupby("County", as_index=False)["Pass Rate"]
    .mean()
)

# Clean county names in age data, same as age_map/pass_rate script
df_age["County"] = (
    df_age["County and State"]
    .str.replace(" City", "", regex=False)
    .str.replace(" County", "", regex=False)
    .str.strip()
)

# Aggregate mean age per county
county_age = (
    df_age
    .dropna(subset=["County", "VALUE"])
    .groupby("County", as_index=False)["VALUE"]
    .mean()
)

# Merge datasets
merged_data = (
    pd.merge(county_pass_rate, county_age, on="County", how="inner")
    .rename(columns={"VALUE": "Average_Age"})
)

# Precompute some stats
n_counties = len(merged_data)
corr = merged_data["Average_Age"].corr(merged_data["Pass Rate"])

age_min = float(merged_data["Average_Age"].min())
age_max = float(merged_data["Average_Age"].max())

# --------------------------------------------------
# Create Dash app and layout
# --------------------------------------------------

app = Dash(__name__)

def make_scatter(df: pd.DataFrame):
    fig = px.scatter(
        df,
        x="Average_Age",
        y="Pass Rate",
        hover_data=["County"],
        labels={
            "Average_Age": "Average Age (years)",
            "Pass Rate": "Pass Rate (%)",
        },
        title="Driving Test Pass Rate vs Average Age by County",
        trendline="ols",
    )
    fig.update_layout(
        margin=dict(l=40, r=20, t=60, b=40),
        hovermode="closest",
    )
    return fig

app.layout = html.Div(
    style={"fontFamily": "Arial, sans-serif", "padding": "20px"},
    children=[
        html.H1("Driving Test Dashboard", style={"marginBottom": "0.5rem"}),

        html.P(
            "Comparing average age per county with driving test pass rates.",
            style={"color": "#555", "marginTop": 0},
        ),

        # Top stats row
        html.Div(
            style={
                "display": "flex",
                "gap": "2rem",
                "marginTop": "1rem",
                "marginBottom": "1.5rem",
            },
            children=[
                html.Div([
                    html.Div("Counties with data", style={"fontSize": "0.85rem", "color": "#777"}),
                    html.Div(f"{n_counties}", style={"fontSize": "1.5rem", "fontWeight": "bold"}),
                ]),
                html.Div([
                    html.Div("Correlation (Age vs Pass Rate)", style={"fontSize": "0.85rem", "color": "#777"}),
                    html.Div(f"{corr:.3f}", style={"fontSize": "1.5rem", "fontWeight": "bold"}),
                ]),
            ],
        ),

        # Controls
        html.Div(
            style={"maxWidth": "500px", "marginBottom": "1.5rem"},
            children=[
                html.Label(
                    "Filter by average age range:",
                    style={"fontWeight": "bold"},
                ),
                dcc.RangeSlider(
                    id="age-range-slider",
                    min=age_min,
                    max=age_max,
                    step=0.1,
                    value=[age_min, age_max],
                    tooltip={"placement": "bottom", "always_visible": False},
                    marks={
                        round(age_min, 1): str(round(age_min, 1)),
                        round(age_max, 1): str(round(age_max, 1)),
                    },
                ),
            ],
        ),

        # Scatter plot
        dcc.Graph(
            id="age-pass-scatter",
            figure=make_scatter(merged_data),
            style={"height": "600px"},
        ),

        # Data preview table
        html.H2("Merged Data Preview", style={"marginTop": "2rem"}),
        html.Table(
            id="data-preview-table",
            style={
                "borderCollapse": "collapse",
                "minWidth": "400px",
            },
            children=[
                html.Thead(
                    html.Tr([
                        html.Th("County", style={"border": "1px solid #ccc", "padding": "4px"}),
                        html.Th("Average Age", style={"border": "1px solid #ccc", "padding": "4px"}),
                        html.Th("Pass Rate (%)", style={"border": "1px solid #ccc", "padding": "4px"}),
                    ])
                ),
                html.Tbody([
                    html.Tr([
                        html.Td(row["County"], style={"border": "1px solid #eee", "padding": "4px"}),
                        html.Td(f"{row['Average_Age']:.2f}", style={"border": "1px solid #eee", "padding": "4px"}),
                        html.Td(f"{row['Pass Rate']:.2f}", style={"border": "1px solid #eee", "padding": "4px"}),
                    ])
                    for _, row in merged_data.sort_values("County").head(10).iterrows()
                ]),
            ],
        ),
    ],
)

# --------------------------------------------------
# 3. Callbacks
# --------------------------------------------------

@app.callback(
    Output("age-pass-scatter", "figure"),
    Input("age-range-slider", "value"),
)
def update_scatter(age_range):
    low, high = age_range
    filtered = merged_data[
        (merged_data["Average_Age"] >= low) &
        (merged_data["Average_Age"] <= high)
    ]
    # If the filter wipes everything out, fall back to full data
    if filtered.empty:
        filtered = merged_data
    return make_scatter(filtered)


# --------------------------------------------------
# 4. Entrypoint
# --------------------------------------------------

if __name__ == "__main__":
    # Run with: python dash_app.py
    app.run_server(debug=True)
