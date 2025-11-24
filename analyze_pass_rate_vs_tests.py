import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

# Read the cleaned CSV file
df = pd.read_csv('ROA30.20251112T121150_cleaned.csv')

# Remove rows with NaN values in Pass Rate or Number of Tests
df_clean = df.dropna(subset=['Pass Rate', 'Number of Tests'])

# Filter out rows where Number of Tests is 0 or very small (less reliable data)
df_clean = df_clean[df_clean['Number of Tests'] >= 10]

# Create the figure with two subplots
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

# --- Subplot 1: Scatter plot with all data points ---
ax1.scatter(df_clean['Number of Tests'], df_clean['Pass Rate'], 
            alpha=0.5, s=30, color='#1f77b4')

# Add trend line
z = np.polyfit(df_clean['Number of Tests'], df_clean['Pass Rate'], 1)
p = np.poly1d(z)
x_trend = np.linspace(df_clean['Number of Tests'].min(), 
                      df_clean['Number of Tests'].max(), 100)
ax1.plot(x_trend, p(x_trend), "r--", linewidth=2, label=f'Trend: y={z[0]:.4f}x+{z[1]:.2f}')

# Calculate correlation coefficient
correlation = df_clean['Number of Tests'].corr(df_clean['Pass Rate'])
r_squared = correlation ** 2

ax1.set_xlabel('Number of Tests', fontsize=12, fontweight='bold')
ax1.set_ylabel('Pass Rate (%)', fontsize=12, fontweight='bold')
ax1.set_title(f'Pass Rate vs Number of Tests\nCorrelation: {correlation:.3f} (R² = {r_squared:.3f})', 
              fontsize=14, fontweight='bold')
ax1.grid(True, alpha=0.3, linestyle='--')
ax1.legend()
ax1.set_ylim(0, 100)

# --- Subplot 2: Binned analysis for clearer pattern ---
# Create bins for number of tests
bins = [0, 50, 100, 200, 500, 1000, 5000]
bin_labels = ['10-50', '51-100', '101-200', '201-500', '501-1000', '1000+']

df_clean['Test_Bins'] = pd.cut(df_clean['Number of Tests'], 
                                bins=bins, 
                                labels=bin_labels, 
                                include_lowest=True)

# Calculate average pass rate for each bin
binned_data = df_clean.groupby('Test_Bins', observed=True).agg({
    'Pass Rate': ['mean', 'std', 'count']
}).reset_index()

binned_data.columns = ['Test_Range', 'Avg_Pass_Rate', 'Std_Pass_Rate', 'Count']

# Create bar plot with error bars
x_pos = range(len(binned_data))
bars = ax2.bar(x_pos, binned_data['Avg_Pass_Rate'], 
               yerr=binned_data['Std_Pass_Rate'],
               alpha=0.7, color='#2ca02c', capsize=5)

# Add count labels on top of bars
for i, (bar, count) in enumerate(zip(bars, binned_data['Count'])):
    height = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2., height + 2,
             f'n={int(count)}',
             ha='center', va='bottom', fontsize=9)

ax2.set_xlabel('Number of Tests Range', fontsize=12, fontweight='bold')
ax2.set_ylabel('Average Pass Rate (%)', fontsize=12, fontweight='bold')
ax2.set_title('Average Pass Rate by Test Volume\n(with standard deviation)', 
              fontsize=14, fontweight='bold')
ax2.set_xticks(x_pos)
ax2.set_xticklabels(binned_data['Test_Range'], rotation=45, ha='right')
ax2.grid(True, alpha=0.3, linestyle='--', axis='y')
ax2.set_ylim(0, 100)

plt.tight_layout()
plt.savefig('pass_rate_vs_tests_analysis.png', dpi=300, bbox_inches='tight')
print("Chart saved as 'pass_rate_vs_tests_analysis.png'")
plt.show()

# Print statistical summary
print("\n" + "="*60)
print("STATISTICAL ANALYSIS")
print("="*60)
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
print("between the number of tests taken and pass rate.")

print("\n" + "="*60)
print("AVERAGE PASS RATES BY TEST VOLUME")
print("="*60)
for _, row in binned_data.iterrows():
    print(f"{row['Test_Range']:12} tests: {row['Avg_Pass_Rate']:5.2f}% "
          f"(±{row['Std_Pass_Rate']:5.2f}%, n={int(row['Count'])})")
