import pandas as pd
import random
import time

# Load the original CSV file
file_path = "Test_Case_Prioritization/data/test_case_risk_scores_sorted.csv"  # Adjust this if running locally
df = pd.read_csv(file_path)

# Define number of random shuffles
iterations = 1000
shuffled_orders = []

# Use a time-based seed so results vary each run
base_seed = int(time.time())

# Generate unique permutations with varying seeds
for i in range(iterations):
    seed = base_seed + i
    shuffled_indices = list(df.index)
    random.Random(seed).shuffle(shuffled_indices)
    shuffled_orders.append(df.iloc[shuffled_indices].reset_index(drop=True))

# Save the final shuffled result (from the last iteration)
final_result = shuffled_orders[-1]  # Only keep one shuffled version

# Save the final output
output_path = "Test_Case_Prioritization/data/randomized_test_cases.csv"  # Adjust as needed
final_result.to_csv(output_path, index=False)

print(f"Final randomized test cases saved to '{output_path}' with base seed {base_seed}.")
