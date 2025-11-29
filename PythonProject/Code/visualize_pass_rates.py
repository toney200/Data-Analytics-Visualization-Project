import pandas as pd
import plotly.graph_objects as go

# Read the cleaned CSV file
df = pd.read_csv('../ROA30.20251112T121150_cleaned.csv')

# Filter for 'All driving test centres' to get overall pass rates
df_filtered = df[df['Driving Test Centre'] == 'All driving test centres'].copy()

# Extract year and month from the 'Month' column
df_filtered['Year'] = df_filtered['Month'].str.split().str[0]
df_filtered['Month_Name'] = df_filtered['Month'].str.split().str[1]

# Define month order for proper sorting
month_order = ['January', 'February', 'March', 'April', 'May', 'June', 
               'July', 'August', 'September', 'October', 'November', 'December']

# Convert month names to categorical with proper order
df_filtered['Month_Num'] = pd.Categorical(df_filtered['Month_Name'], 
                                          categories=month_order, 
                                          ordered=True)

# Group by year and month to get data for each year separately
yearly_monthly_data = df_filtered.groupby(['Year', 'Month_Num'], observed=True)['Pass Rate'].mean().reset_index()

# Create the plot using Plotly
fig = go.Figure()

# Get unique years and create a color palette
years = sorted(yearly_monthly_data['Year'].unique())
colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f']

# Add a line for each year
for i, year in enumerate(years):
    year_data = yearly_monthly_data[yearly_monthly_data['Year'] == year]
    
    fig.add_trace(go.Scatter(
        x=year_data['Month_Num'].astype(str),
        y=year_data['Pass Rate'],
        mode='lines+markers',
        line=dict(color=colors[i % len(colors)], width=2),
        marker=dict(size=6, color=colors[i % len(colors)]),
        name=f'{year}',
        hovertemplate='<b>%{x} %{fullData.name}</b><br>' +
                      'Pass Rate: %{y:.2f}%<extra></extra>'
    ))

# Update layout to match the center chart style
fig.update_layout(
    title='Driving Test Pass Rates by Month and Year',
    xaxis_title='Month',
    yaxis_title='Pass Rate (%)',
    yaxis=dict(range=[0, 100]),
    xaxis=dict(tickangle=45),
    showlegend=True,
    legend=dict(title='Year'),
    height=600,
    margin={"r":20, "t":60, "l":50, "b":50}
)

# Show the plot
fig.show()
