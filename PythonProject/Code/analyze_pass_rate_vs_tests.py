import pandas as pd
import re
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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

# Create subplots using Plotly
fig = make_subplots(rows=1, cols=2, 
                    subplot_titles=("Pass Rate vs Number of Tests by County", 
                                   "Average Pass Rate by County"),
                    horizontal_spacing=0.1)

# --- Subplot 1: Scatter plot with trendline ---
scatter_fig = px.scatter(county_data, 
                        x='Number of Tests', 
                        y='Pass Rate',
                        hover_data=['County'],
                        trendline="ols")

# Add scatter points to subplot
fig.add_trace(go.Scatter(x=county_data['Number of Tests'], 
                        y=county_data['Pass Rate'],
                        mode='markers',
                        marker=dict(size=8, opacity=0.7, color='#1f77b4'),
                        name='Counties',
                        hovertemplate='<b>%{customdata[0]}</b><br>' +
                                     'Tests: %{x}<br>' +
                                     'Pass Rate: %{y:.2f}%<extra></extra>',
                        customdata=county_data[['County']].values),
             row=1, col=1)

# Extract trendline data and add to subplot
trendline_trace = scatter_fig.data[1]  # Second trace is the trendline
fig.add_trace(go.Scatter(x=trendline_trace.x,
                        y=trendline_trace.y,
                        mode='lines',
                        line=dict(color='red', dash='dash'),
                        name='Trendline',
                        showlegend=False),
             row=1, col=1)

# --- Subplot 2: Bar chart showing pass rates by county ---
# Add bar chart to subplot
county_sorted = county_data.sort_values('Pass Rate', ascending=False)
fig.add_trace(go.Bar(x=county_sorted['County'],
                    y=county_sorted['Pass Rate'],
                    marker=dict(color='#2ca02c', opacity=0.7),
                    name='Pass Rate',
                    showlegend=False,
                    hovertemplate='<b>%{x}</b><br>' +
                                 'Pass Rate: %{y:.2f}%<br>' +
                                 'Total Tests: %{customdata}<extra></extra>',
                    customdata=county_sorted['Number of Tests']),
             row=1, col=2)

# Update layout for both subplots
fig.update_xaxes(title_text="Total Number of Tests", row=1, col=1)
fig.update_yaxes(title_text="Average Pass Rate (%)", row=1, col=1, range=[0, 100])
fig.update_xaxes(title_text="County", row=1, col=2)
fig.update_yaxes(title_text="Average Pass Rate (%)", row=1, col=2, range=[0, 100])

# Update x-axis for bar chart to show rotated labels
fig.update_xaxes(tickangle=45, row=1, col=2)

# Update overall layout
fig.update_layout(
    title='County Analysis: Pass Rate vs Test Volume',
    height=500,
    showlegend=False,
    margin={"r":20, "t":60, "l":20, "b":100}
)

# Show the plot
fig.show()

# Print statistical summary
print("\n" + "="*60)
print("STATISTICAL ANALYSIS BY COUNTY")
print("="*60)
correlation = county_data['Number of Tests'].corr(county_data['Pass Rate'])
r_squared = correlation ** 2
print(f"\nCorrelation Coefficient: {correlation:.4f}")
print(f"R-squared: {r_squared:.4f}")

if abs(correlation) < 0.1:
    strength = "very weak or no"
elif abs(correlation) < 0.3:
    strength = "weak"
elif abs(correlation) < 0.5:
    strength = "moderate"
elif abs(correlation) < 0.7:
    strength = "strong"
else:
    strength = "very strong"

direction = "positive" if correlation > 0 else "negative"

print(f"\nInterpretation: There is a {strength} {direction} correlation")
print("between the total number of tests taken per county and average pass rate.")

print("\n" + "="*60)
print("COUNTY PASS RATES AND TEST VOLUMES")
print("="*60)
for _, row in county_sorted.iterrows():
    print(f"{row['County']:12}: {row['Pass Rate']:5.2f}% "
          f"(total tests: {int(row['Number of Tests'])})")
