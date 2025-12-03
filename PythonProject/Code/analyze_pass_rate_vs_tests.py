import pandas as pd
import re
import plotly.express as px

# Read the cleaned CSV file
df = pd.read_csv('../ROA30.20251112T121150_cleaned.csv')

# Read population data
df_population = pd.read_csv('../PEA08.20251203T161259.csv')

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

# Prepare population data - extract county names and convert population to actual numbers
df_population['County'] = df_population['County'].str.replace('Co. ', '', regex=False)
# Convert from thousands to actual population numbers
df_population['Population'] = df_population['VALUE'] * 1000

# Create population lookup for counties only (exclude Ireland total)
population_lookup = df_population[df_population['County'] != 'Ireland'].set_index('County')['Population'].to_dict()

# Add population data to county data
county_data['Population'] = county_data['County'].map(population_lookup)

# Remove counties without population data and filter out counties with very few tests
county_data = county_data.dropna(subset=['Population'])
county_data = county_data[county_data['Number of Tests'] >= 50]

# Calculate normalized metrics per thousand population
county_data['Tests_per_1000'] = (county_data['Number of Tests'] / county_data['Population']) * 1000

# Create scatter plot
fig = px.scatter(
    county_data,
    x='Tests_per_1000',
    y='Pass Rate',
    hover_data=['County', 'Number of Tests', 'Population'],
    labels={
        'Tests_per_1000': 'Tests per 1,000 Population',
        'Pass Rate': 'Pass Rate (%)'
    },
    title='Pass Rate vs Tests per 1,000 Population by County',
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
                  'Tests per 1,000: %{x:.1f}<br>' +
                  'Pass Rate: %{y:.1f}%<br>' +
                  'Total Tests: %{customdata[1]:,}<br>' +
                  'Population: %{customdata[2]:,.0f}<extra></extra>',
    selector=dict(mode='markers')
)

# Show the plot
fig.show()