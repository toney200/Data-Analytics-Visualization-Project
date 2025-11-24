import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Read the cleaned CSV file
df = pd.read_csv('ROA30.20251112T121150_cleaned.csv')

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

# Group by month name and calculate mean pass rate across all years
monthly_data = df_filtered.groupby('Month_Num', observed=True)['Pass Rate'].mean()

# Create the plot
plt.figure(figsize=(14, 8))

# Plot a single line aggregating all years by month
plt.plot(range(len(monthly_data)), monthly_data.values, marker='o', 
         linewidth=2, markersize=8, color='#1f77b4')

# Customize the plot
plt.title('Average Driving Test Pass Rates by Month\n(All Driving Test Centres, All Years Combined)', 
          fontsize=16, fontweight='bold', pad=20)
plt.xlabel('Month', fontsize=14, fontweight='bold')
plt.ylabel('Pass Rate (%)', fontsize=14, fontweight='bold')
plt.grid(True, alpha=0.3, linestyle='--')
plt.xticks(range(len(monthly_data)), month_order[:len(monthly_data)], rotation=45, ha='right')
plt.ylim(0, 100)  # Set y-axis range from 0 to 100
plt.tight_layout()

# Show the plot
plt.show()
