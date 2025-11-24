import pandas as pd

# Read the CSV file
input_file = 'ROA30.20251112T121150.csv'
output_file = 'ROA30.20251112T121150_cleaned.csv'

# Read the CSV
df = pd.read_csv(input_file)

# Fill blank cells with 'NaN' for Pass Rate and Number of Tests columns
df['Pass Rate'] = df['Pass Rate'].fillna('NaN')
df['Number of Tests'] = df['Number of Tests'].fillna('NaN')

# Save the updated CSV
df.to_csv(output_file, index=False)

print(f"Successfully filled blank cells with 'NaN' in Pass Rate and Number of Tests columns")
print(f"Output saved to: {output_file}")
