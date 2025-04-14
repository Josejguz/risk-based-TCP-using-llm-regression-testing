import os
import csv
from bs4 import BeautifulSoup

def extract_test_coverage_from_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')

    class_name = soup.title.string.strip() if soup.title else "UnknownClass"
    table = soup.find('table', {'id': 'coveragetable'})
    if not table:
        return []

    results = []
    rows = table.find_all('tr')[1:]  # Skip header
    for row in rows:
        cols = row.find_all('td')
        if len(cols) < 3:
            continue
        method_link = cols[0].find('a')
        if method_link:
            method_name = method_link.text.strip()
            if not method_name.startswith("test"):
                continue  # Only include test methods

            coverage_str = cols[2].text.strip().replace('%', '')
            try:
                coverage = float(coverage_str)
            except ValueError:
                coverage = 0.0  # Handle "n/a" as 0%
            results.append((class_name, method_name, coverage))

    return results

def scan_directory_and_generate_csv(root_dir, output_csv):
    all_results = []
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if (
                filename.endswith('.html')
                and not filename.endswith('.java.html')
                and filename.endswith('Test.html')  # Likely to be test class coverage
            ):
                full_path = os.path.join(dirpath, filename)
                all_results.extend(extract_test_coverage_from_file(full_path))

    # Sort by coverage descending
    all_results.sort(key=lambda x: x[2], reverse=True)

    with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Class Name', 'Test Case', 'Coverage (%)'])
        writer.writerows(all_results)

    print(f"CSV file generated at: {output_csv}")

# Example usage:
scan_directory_and_generate_csv("C:\\Users\\jguzm\\eclipse-workspace\\RiskBasedTCP\\Coverage Results_V1\\Thesis\\src_test_java", 'coverage_report.csv')
