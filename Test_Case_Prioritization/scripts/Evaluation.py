import pandas as pd
import matplotlib.pyplot as plt
from collections import defaultdict

# --- Load Normalized Data ---
risk_df = pd.read_csv("Test_Case_Prioritization\\data\\normalized_test_case_risk_scores.csv")
coverage_df = pd.read_csv("Test_Case_Prioritization\\data\\normalized_coverage_report.csv")
mutation_df = pd.read_csv("Test_Case_Prioritization\\data\\normalized_mutation_summary.csv")
random_df = pd.read_csv("Test_Case_Prioritization\\data\\normalized_randomized_test_cases.csv")

# --- Determine common test cases across all strategies ---
common_tests = set(risk_df["Normalized_Test_Method"]) & \
               set(coverage_df["Normalized_Test_Method"]) & \
               set(random_df["Normalized_Test_Method"])

# Filter and preserve order
risk_priority = [tc for tc in risk_df["Normalized_Test_Method"] if tc in common_tests]
random_priority = [tc for tc in random_df["Normalized_Test_Method"] if tc in common_tests]
coverage_priority_full = [tc for tc in coverage_df.sort_values(by="Coverage (%)", ascending=True)["Normalized_Test_Method"] if tc in common_tests]
coverage_priority = coverage_priority_full[:len(risk_priority)]  # Trim to same count as others

# --- Create mutant-to-test map ---
mutant_map = defaultdict(list)
mutant_id_counter = 1
for _, row in mutation_df.iterrows():
    test_case = row["Normalized_Test_Method"]
    killed_count = row["Killed"]
    for _ in range(killed_count):
        mutant_id = f"M{mutant_id_counter}"
        mutant_map[mutant_id].append(test_case)
        mutant_id_counter += 1

# --- APFD and FDR Calculation Function ---
def calculate_apfd_with_details(priority_list, mutant_map):
    index_lookup = {tc: idx + 1 for idx, tc in enumerate(priority_list)}
    TF_sum = 0
    valid_mutants = 0
    tf_values = []
    mutant_first_detection = {}

    for mutant, killers in mutant_map.items():
        killer_indices = [index_lookup[tc] for tc in killers if tc in index_lookup]
        if killer_indices:
            TF_i = min(killer_indices)
            tf_values.append(TF_i)
            TF_sum += TF_i
            valid_mutants += 1
            mutant_first_detection[mutant] = TF_i

    n = len(priority_list)
    m = valid_mutants
    if m == 0:
        return None, 0, 0, [], 0.0, []

    apfd = 1 - (TF_sum / (n * m)) + (1 / (2 * n))
    fdr = valid_mutants / 106

    # Generate FDR curve (cumulative mutants detected)
    fdr_curve = []
    detected = set()
    for i in range(n):
        current_test = priority_list[i]
        for mutant, killers in mutant_map.items():
            if mutant not in detected and current_test in killers:
                detected.add(mutant)
        fdr_curve.append(len(detected) / 106)

    return apfd, n, m, tf_values, fdr, fdr_curve

# --- Compute Results ---
results = {}
for name, priority in [("Risk-Based", risk_priority),
                       ("Random Order", random_priority),
                       ("Coverage-Based", coverage_priority)]:
    apfd, n, m, tf_vals, fdr, fdr_curve = calculate_apfd_with_details(priority, mutant_map)
    results[name] = {
        "APFD": apfd,
        "n": n,
        "m": m,
        "TF_sum": sum(tf_vals),
        "TF_values": tf_vals,
        "FDR": fdr,
        "FDR_Curve": fdr_curve
    }

# --- Save Mathematical Results to TXT ---
with open("apfd_results.txt", "w", encoding="utf-8") as f:
    f.write("APFD Results and Mathematical Analysis\n")
    f.write("========================================================================\n\n")
    for name, data in results.items():
        f.write(f"{name} Strategy:\n")
        if data["APFD"] is None:
            f.write("  - No valid mutants matched.\n\n")
            continue
        apfd = data["APFD"]
        n = data["n"]
        m = data["m"]
        tf_sum = data["TF_sum"]
        fdr = data["FDR"]
        f.write(f"  - Total Test Cases (n)      : {n}\n")
        f.write(f"  - Total Mutants (m)         : {m}\n")
        f.write(f"  - Sum of First Kill Indices : {tf_sum}\n")
        f.write(f"  - Fault Detection Rate (FDR): {fdr:.4f}\n")
        f.write(f"  - APFD Formula              : 1 - (Sum TF_i / n*m) + (1 / 2n)\n")
        f.write(f"                              = 1 - ({tf_sum} / {n}*{m}) + (1 / (2*{n}))\n")
        f.write(f"                              = {apfd:.4f}\n\n")

# --- APFD Bar Chart ---
strategies = list(results.keys())
apfd_values = [results[strat]["APFD"] for strat in strategies]
plt.figure(figsize=(8, 5))
plt.bar(strategies, apfd_values)
plt.title("APFD for Each Test Case Prioritization Strategy")
plt.ylabel("APFD Score")
plt.ylim(0, 1)
plt.grid(axis="y")
plt.tight_layout()
plt.savefig("apfd_chart.png")
plt.close()

# --- FDR Curve Plot ---
plt.figure(figsize=(8, 5))
for name, data in results.items():
    plt.plot(range(1, len(data["FDR_Curve"]) + 1), data["FDR_Curve"], label=name)
plt.title("FDR Curves Over Test Execution")
plt.xlabel("Test Case Execution Order")
plt.ylabel("Cumulative Fault Detection Rate (FDR)")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("fdr_curve_chart.png")
plt.close()
