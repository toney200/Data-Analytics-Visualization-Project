import pandas as pd
import re
import plotly.express as px
from pathlib import Path

# Set base directory to project root
BASE_DIR = Path(__file__).resolve().parent.parent

# Load driving test data
driving_data_path = BASE_DIR / "driving_test_data.csv"
df_driving = pd.read_csv(driving_data_path)

# Load age data
age_data_path = BASE_DIR / "Average_Age_Per_County.cleaned.csv"
df_age = pd.read_csv(age_data_path)

# Load population data
population_data_path = BASE_DIR / "PEA08.20251203T161259.csv"
df_population = pd.read_csv(population_data_path)

# Extract county from driving test centre names
def extract_county(text):
    match = re.search(r"Co\.?\s+([A-Za-z]+)", str(text))
    return match.group(1) if match else None

df_driving["County"] = df_driving["Driving Test Centre"].apply(extract_county)

# Calculate mean pass rate per county from driving data
county_pass_rate = (
    df_driving.groupby("County", as_index=False)["Pass Rate"].mean()
)

# Clean county names from age data
df_age["County"] = df_age["County and State"].str.replace(" City", "").str.replace(" County", "").str.strip()

# Calculate mean age per county from age data
county_age = (
    df_age.groupby("County", as_index=False)["VALUE"].mean()
)

# Prepare population data
df_population['County'] = df_population['County'].str.replace('Co. ', '', regex=False)
df_population['Population'] = df_population['VALUE'] * 1000  # Convert from thousands
population_lookup = df_population[df_population['County'] != 'Ireland'].set_index('County')['Population'].to_dict()

# Merge the datasets on County
merged_data = pd.merge(county_pass_rate, county_age, on="County", how="inner")

# Add population data
merged_data['Population'] = merged_data['County'].map(population_lookup)
merged_data = merged_data.dropna(subset=['Population'])

# Calculate normalized opacity based on population (0.3 to 1.0 range)
min_pop = merged_data['Population'].min()
max_pop = merged_data['Population'].max()
merged_data['Opacity'] = 0.3 + 0.7 * (merged_data['Population'] - min_pop) / (max_pop - min_pop)

# Rename columns for clarity
merged_data = merged_data.rename(columns={"VALUE": "Average_Age"})

# Create scatterplot with trendline and population-based opacity
fig = px.scatter(
    merged_data,
    x="Average_Age",
    y="Pass Rate",
    hover_data=["County", "Population"],
    labels={
        "Average_Age": "Average Age",
        "Pass Rate": "Pass Rate (%)"
    },
    title="Driving Test Pass Rate vs Average Age by County (Size = Population)",
    trendline="ols"  # Ordinary Least Squares regression line
)

# Update marker opacity based on population
fig.update_traces(marker=dict(opacity=merged_data['Opacity']))

# Update layout
fig.update_layout(
    showlegend=False,
    margin={"r":20, "t":50, "l":20, "b":20}
)

# Show the plot
fig.show()