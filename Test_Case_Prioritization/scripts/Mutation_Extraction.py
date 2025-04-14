import pandas as pd
import os
import re

# Load CSV
file_path = 'Test_Case_Prioritization\data\mutations.csv'  # Adjust if running locally
df = pd.read_csv(file_path, header=None)

# Assign column names manually since headers aren't properly defined
df.columns = [
    'File', 'Class', 'Mutator', 'Method', 'Line', 'Status', 'Test'
]

# Normalize status and extract only relevant fields
processed = df[['Class', 'Status', 'Test']].copy()
processed['Class'] = processed['Class'].apply(lambda x: x.split('.')[-1])
processed['Test'] = processed['Test'].apply(
    lambda x: re.search(r'method:(.*?)\)', x).group(1) + '()' if isinstance(x, str) and re.search(r'method:(.*?)\)', x) else x
)
processed['MutantStatus'] = processed['Status'].apply(lambda x: 'Killed' if x == 'KILLED' else 'Alive')

# Group by Class, Test, and count mutants killed/alive
summary = processed.groupby(['Class', 'Test', 'MutantStatus']).size().unstack(fill_value=0).reset_index()

# Export summary to CSV
output_path = 'Test_Case_Prioritization/data/mutation_summary.csv'
os.makedirs(os.path.dirname(output_path), exist_ok=True)
summary.to_csv(output_path, index=False)
print(f"Summary exported to {output_path}")

# Display summary
def print_summary(df):
    for _, row in df.iterrows():
        print(f"Class: {row['Class']}")
        print(f"  Test: {row['Test']}")
        print(f"    Killed: {row.get('Killed', 0)}")
        print(f"    Alive: {row.get('Alive', 0)}\n")

# Run summary
print_summary(summary)