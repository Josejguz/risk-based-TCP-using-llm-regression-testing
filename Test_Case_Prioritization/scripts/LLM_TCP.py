import pandas as pd

# Load the risk scores file
risk_scores_df = pd.read_csv("Test_Case_Prioritization\\data\\Predicted_Risk_Scores_1(1).csv")

# Create a key in the format: ClassName.MethodName (e.g., ArrayStack.push)
risk_scores_df["lookup_key"] = risk_scores_df["File"].str.replace(".java", "", regex=False) + "." + risk_scores_df["Method"]

# Load the callgraph file
callgraph_df = pd.read_csv("Test_Case_Prioritization\\data\\final_callgraph.csv")

# Prepare lookup key for callgraph (already in Class.Method format)
callgraph_df["lookup_key"] = callgraph_df["callgraph edges"]

# Merge to attach risk scores to each method call in the graph
merged_df = callgraph_df.merge(
    risk_scores_df[["lookup_key", "Predicted_Risk_Score"]],
    on="lookup_key",
    how="left"
)

# Group by test case and sum the risk scores
test_case_risks = merged_df.groupby("source class and name")["Predicted_Risk_Score"].sum().reset_index()
test_case_risks.columns = ["Test_Case", "Total_Risk_Score"]

# Sort by descending risk
test_case_risks_sorted = test_case_risks.sort_values(by="Total_Risk_Score", ascending=False)

# Save output
test_case_risks_sorted.to_csv("Test_Case_Prioritization/data/test_case_risk_scores_sorted.csv", index=False)
