import pandas as pd
import plotly.express as px
from pathlib import Path

# Set base directory to project root
BASE_DIR = Path(__file__).resolve().parent.parent
csv_path = BASE_DIR / "ROA30.20251112T121150_cleaned.csv"

# Read the driving test data
df = pd.read_csv(csv_path)

# Remove rows with NaN values and filter out 'All driving test centres'
df_clean = df.dropna(subset=['Driving Test Centre', 'Number of Tests'])
df_clean = df_clean[df_clean['Driving Test Centre'] != 'All driving test centres']

# Aggregate data by driving test center
center_data = (
    df_clean.groupby("Driving Test Centre", as_index=False).agg({
        'Pass Rate': 'mean',
        'Number of Tests': 'sum'
    })
)

# Create scatter plot
fig = px.scatter(
    center_data,
    x='Number of Tests',
    y='Pass Rate',
    hover_data=['Driving Test Centre'],
    labels={
        'Number of Tests': 'Total Number of Tests',
        'Pass Rate': 'Pass Rate (%)'
    },
    title='Pass Rate vs Number of Tests by Driving Test Centre',
    trendline="ols"
)

# Update layout
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

fig.show()