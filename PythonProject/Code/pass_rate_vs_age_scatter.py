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

# Merge the two datasets on County
merged_data = pd.merge(county_pass_rate, county_age, on="County", how="inner")

# Rename columns for clarity
merged_data = merged_data.rename(columns={"VALUE": "Average_Age"})

# Create scatterplot with trendline
fig = px.scatter(
    merged_data,
    x="Average_Age",
    y="Pass Rate",
    hover_data=["County"],
    labels={
        "Average_Age": "Average Age",
        "Pass Rate": "Pass Rate (%)"
    },
    title="Driving Test Pass Rate vs Average Age by County",
    trendline="ols"  # Ordinary Least Squares regression line
)

# Update layout
fig.update_layout(
    showlegend=False,
    margin={"r":20, "t":50, "l":20, "b":20}
)

# Show the plot
fig.show()