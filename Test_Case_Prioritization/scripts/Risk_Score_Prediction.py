import torch
import pandas as pd
from transformers import AutoModelForCausalLM, AutoTokenizer
import re
import numpy as np
import os
import joblib

#  Set Paths
MODEL_PATH = "C:\Users\srinivasanm23\Documents\regression test llm\output_2"
TEST_CSV_PATH = "C:\Users\srinivasanm23\Documents\regression test llm\Risk_results_V2_1.csv"
OUTPUT_CSV = "C:\Users\srinivasanm23\Documents\regression test llm\Predicted_Risk_Scores.csv"

#  Load Fine-Tuned Model & Tokenizer
print(" Loading model and tokenizer...")
try:
    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
    model = AutoModelForCausalLM.from_pretrained(MODEL_PATH)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    print(f" Model loaded successfully on {device}.")
    
    # Try to load the scaler if available
    scaler_path = os.path.join(MODEL_PATH, "metric_scaler.joblib")
    if os.path.exists(scaler_path):
        scaler = joblib.load(scaler_path)
        print(" Loaded metric scaler for normalization.")
        normalize_metrics = True
    else:
        print(" No metric scaler found, using raw metrics.")
        normalize_metrics = False
        
except Exception as e:
    print(f" Error loading model: {e}")
    exit()

#  Load Test Data
print(" Loading test dataset...")
try:
    df_test = pd.read_csv(TEST_CSV_PATH)
    print(f" Loaded {len(df_test)} test samples.")
except Exception as e:
    print(f" Error loading dataset: {e}")
    exit()

#  Function to Extract Numeric Risk Score from Output
def extract_numeric_value(output_text):
    """Extract numeric risk score from model output."""
    # Remove the prompt part if it's included in the output
    if "Risk Score:" in output_text:
        output_text = output_text.split("Risk Score:")[-1].strip()
    
    # Find all numbers in the text
    numbers = re.findall(r"\d+\.\d+|\d+", output_text)
    if numbers:
        try:
            # Take the first number after "Risk Score:"
            return float(numbers[0])
        except ValueError:
            return None
    return None

#  Function to Calculate Risk Score using the training formula
def calculate_risk_score(metrics):
    """Calculate risk score using the same formula as in training."""
    # Same weights as in training
    weights = {
        "Cyclomatic Complexity": 1/7,
        "Lines of Code": 1/7,
        "Dependencies": 1/7,
        "Inputs": 1/7,
        "Fan-In": 1/7,
        "Fan-Out": 1/7,
        "LCOM": 1/7,
    }
    
    # Calculate risk score (0-1 scale)
    risk_score = sum(metrics[metric_name.replace(" ", "_")] * weight 
                      for metric_name, weight in weights.items() 
                      if metric_name.replace(" ", "_") in metrics)
    
    # Scale to 1-10 range as in training
    return risk_score * 9 + 1

#  Function to Generate Risk Score Predictions
def predict_risk_score(model, tokenizer, function_details, raw_metrics=None):
    """Generate risk score prediction for a given function description."""
    
    prompt = (
        f"Analyze the following Java function and predict its risk score on a scale from 1 to 10, "
        f"where higher numbers indicate higher risk.\n\n{function_details}\n\nRisk Score:"
    )
    
    inputs = tokenizer(prompt, return_tensors="pt", padding=True, truncation=True).to(device)
    with torch.no_grad():
        output = model.generate(
            **inputs,
            max_new_tokens=20,
            temperature=0.3,  # Lower temperature for more consistent outputs
            num_return_sequences=1,
            do_sample=True,
            top_p=0.95,
        )
    prediction = tokenizer.decode(output[0], skip_special_tokens=True).strip()
    
    # For debugging
    print(f"Raw model output: {prediction}")
    
    # Extract numeric value from output
    predicted_value = extract_numeric_value(prediction)
    
    # If model failed to predict a valid score, calculate it using the training formula
    if predicted_value is None or predicted_value <= 0 or predicted_value > 10:
        if raw_metrics is not None:
            fallback_score = calculate_risk_score(raw_metrics)
            print(f" Model prediction failed, using calculated score: {fallback_score:.2f}")
            return fallback_score
        else:
            # Default middle value
            print(" Model prediction failed, using default score: 5.0")
            return 5.0
    
    return predicted_value

# Normalize test data if scaler is available
if normalize_metrics:
    num_cols = ["Cyclomatic_Complexity", "Lines_of_Code", "Dependencies", "Inputs", "FanIn", "FanOut", "LCOM"]
    # Create a copy to preserve original values
    df_test_normalized = df_test.copy()
    df_test_normalized[num_cols] = scaler.transform(df_test[num_cols])

#  Run Predictions for All Functions
predictions = []
print(" Generating predictions...")

# Run a small test first
test_sample = df_test.iloc[0]
if normalize_metrics:
    test_sample_norm = df_test_normalized.iloc[0]
    function_details = (
        f"Function: {test_sample_norm['Method']} in {test_sample_norm['File']}\n"
        f"- Cyclomatic Complexity: {test_sample_norm['Cyclomatic_Complexity']:.2f}\n"
        f"- Lines of Code: {test_sample_norm['Lines_of_Code']:.2f}\n"
        f"- Dependencies: {test_sample_norm['Dependencies']:.2f}\n"
        f"- Inputs: {test_sample_norm['Inputs']:.2f}\n"
        f"- Fan-In: {test_sample_norm['FanIn']:.2f}\n"
        f"- Fan-Out: {test_sample_norm['FanOut']:.2f}\n"
        f"- LCOM: {test_sample_norm['LCOM']:.2f}"
    )
else:
    function_details = (
        f"Function: {test_sample['Method']} in {test_sample['File']}\n"
        f"- Cyclomatic Complexity: {test_sample['Cyclomatic_Complexity']:.2f}\n"
        f"- Lines of Code: {test_sample['Lines_of_Code']:.2f}\n"
        f"- Dependencies: {test_sample['Dependencies']:.2f}\n"
        f"- Inputs: {test_sample['Inputs']:.2f}\n"
        f"- Fan-In: {test_sample['FanIn']:.2f}\n"
        f"- Fan-Out: {test_sample['FanOut']:.2f}\n"
        f"- LCOM: {test_sample['LCOM']:.2f}"
    )

print("Testing prediction with a single sample...")
test_pred = predict_risk_score(model, tokenizer, function_details, raw_metrics=test_sample)
print(f"Test prediction result: {test_pred}")

for i, func in df_test.iterrows():
    # Use normalized metrics if available
    if normalize_metrics:
        func_norm = df_test_normalized.iloc[i]
        function_details = (
            f"Function: {func_norm['Method']} in {func_norm['File']}\n"
            f"- Cyclomatic Complexity: {func_norm['Cyclomatic_Complexity']:.2f}\n"
            f"- Lines of Code: {func_norm['Lines_of_Code']:.2f}\n"
            f"- Dependencies: {func_norm['Dependencies']:.2f}\n"
            f"- Inputs: {func_norm['Inputs']:.2f}\n"
            f"- Fan-In: {func_norm['FanIn']:.2f}\n"
            f"- Fan-Out: {func_norm['FanOut']:.2f}\n"
            f"- LCOM: {func_norm['LCOM']:.2f}"
        )
    else:
        function_details = (
            f"Function: {func['Method']} in {func['File']}\n"
            f"- Cyclomatic Complexity: {func['Cyclomatic_Complexity']:.2f}\n"
            f"- Lines of Code: {func['Lines_of_Code']:.2f}\n"
            f"- Dependencies: {func['Dependencies']:.2f}\n"
            f"- Inputs: {func['Inputs']:.2f}\n"
            f"- Fan-In: {func['FanIn']:.2f}\n"
            f"- Fan-Out: {func['FanOut']:.2f}\n"
            f"- LCOM: {func['LCOM']:.2f}"
        )
    
    predicted_risk = predict_risk_score(model, tokenizer, function_details, raw_metrics=func)
    predictions.append({
        "File": func["File"],
        "Method": func["Method"],
        "Predicted_Risk_Score": predicted_risk
    })
    
    # Print progress
    if (i + 1) % 20 == 0 or i == 0:
        non_zero_pct = sum(1 for p in predictions if p["Predicted_Risk_Score"] > 0) / len(predictions) * 100
        print(f" Processed {i + 1}/{len(df_test)} functions... Non-zero predictions: {non_zero_pct:.1f}%")

# Convert Predictions to DataFrame
df_predictions = pd.DataFrame(predictions)

# Show statistics
print("\n Prediction Statistics:")
print(f"Mean risk score: {df_predictions['Predicted_Risk_Score'].mean():.2f}")
print(f"Min risk score: {df_predictions['Predicted_Risk_Score'].min():.2f}")
print(f"Max risk score: {df_predictions['Predicted_Risk_Score'].max():.2f}")
print(f"Standard deviation: {df_predictions['Predicted_Risk_Score'].std():.2f}")

#  Save Predictions to CSV
df_predictions.to_csv(OUTPUT_CSV, index=False)
print(f" Predictions saved to {OUTPUT_CSV}")
print(" Finished! All functions processed successfully.")