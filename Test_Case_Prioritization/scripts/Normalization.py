import pandas as pd
from sklearn.preprocessing import MinMaxScaler

# Load the dataset
file_path = "C:\\Users\\jguzm\\Research\\Thesis_Project\\Risk_results_V2.csv"
df = pd.read_csv(file_path)

# Define the metric columns to normalize
metric_columns = [
    'Cyclomatic_Complexity', 'Lines_of_Code', 'Dependencies',
    'Inputs', 'FanIn', 'FanOut', 'LCOM'
]

# Initialize the MinMaxScaler
scaler = MinMaxScaler()

# Normalize the metric columns
normalized_values = scaler.fit_transform(df[metric_columns])

# Compute the risk score as the sum of normalized metrics (equal weight)
risk_scores = normalized_values.sum(axis=1)

# Scale the risk scores to a range of 1 to 10
scaler_risk = MinMaxScaler(feature_range=(1, 10))
scaled_risk_scores = scaler_risk.fit_transform(risk_scores.reshape(-1, 1)).flatten()

# Add the Risk_Score column to the original dataframe
df['Risk_Score'] = scaled_risk_scores

# Save the updated dataframe back to the same CSV file (overwrite)
df.to_csv("Risk_results_V2.csv", index=False)

# Optional: print confirmation
print("✅ Risk scores scaled to range 1-10 and CSV file updated.")
