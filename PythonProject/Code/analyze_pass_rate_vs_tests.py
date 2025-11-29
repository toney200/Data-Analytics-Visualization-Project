import pandas as pd
import re
import plotly.express as px

# Read the cleaned CSV file
df = pd.read_csv('../ROA30.20251112T121150_cleaned.csv')

# Extract county from 'Driving Test Centre'
def extract_county(text):
    match = re.search(r"Co\.?\s+([A-Za-z]+)", str(text))
    return match.group(1) if match else None

df["County"] = df["Driving Test Centre"].apply(extract_county)

# Remove rows with NaN values in Pass Rate or Number of Tests
df_clean = df.dropna(subset=['Pass Rate', 'Number of Tests', 'County'])

# Aggregate data by county
county_data = df_clean.groupby('County').agg({
    'Pass Rate': 'mean',
    'Number of Tests': 'sum'
}).reset_index()

# Filter out counties with very few tests (less reliable data)
county_data = county_data[county_data['Number of Tests'] >= 50]

# Create scatter plot
fig = px.scatter(
    county_data,
    x='Number of Tests',
    y='Pass Rate',
    hover_data=['County'],
    labels={
        'Number of Tests': 'Total Number of Tests',
        'Pass Rate': 'Pass Rate (%)'
    },
    title='Pass Rate vs Number of Tests by County',
    trendline="ols"
)

# Update layout to match center chart style
fig.update_layout(
    height=600,
    margin={"r":20, "t":60, "l":50, "b":50},
    showlegend=False
)

# Update hover template for scatter points
fig.update_traces(
    hovertemplate='<b>%{customdata[0]}</b><br>' +
                  'Tests: %{x:,}<br>' +
                  'Pass Rate: %{y:.2f}%<extra></extra>',
    selector=dict(mode='markers')
)

# Show the plot
fig.show()