import os
import re
import pandas as pd

def extract_class_and_method(signature):
    """Extract class and method names from a fully qualified signature."""
    match = re.search(r'<<.*\.(\w+): .* (\w+)\(.*\)>>', signature)
    if match:
        class_name = match.group(1)
        method_name = match.group(2)
        return f"{class_name}.{method_name}"
    return None

def is_test_method(method_signature):
    """Check if a method is a test case (starts with 'test')."""
    return method_signature.split('.')[-1].startswith("test")

def process_callgraph_directory_to_single_file(input_dir, output_file):
    """Process all _callgraph.csv files in a directory and save to a single output CSV."""
    all_data = []

    for filename in os.listdir(input_dir):
        if filename.endswith("_callgraph.csv"):
            filepath = os.path.join(input_dir, filename)
            with open(filepath, 'r') as f:
                lines = f.readlines()

            for line in lines[1:]:  # Skip header
                parts = line.strip().split(">>,<<")
                if len(parts) == 2:
                    src_raw = parts[0] + ">>"
                    tgt_raw = "<<" + parts[1]
                    src_clean = extract_class_and_method(src_raw)
                    tgt_clean = extract_class_and_method(tgt_raw)
                    if src_clean and tgt_clean and is_test_method(src_clean):
                        all_data.append((src_clean, tgt_clean))

    df = pd.DataFrame(all_data, columns=["source class and name", "callgraph edges"])
    df.to_csv(output_file, index=False)
    print(f"All results written to {output_file}")

# Example usage
if __name__ == "__main__":
    input_dir = "C:/Users/jguzm/Downloads/soot_output/soot_output"
    output_file = "Test_Case_Prioritization/data/final_callgraph.csv"
    process_callgraph_directory_to_single_file(input_dir, output_file)
