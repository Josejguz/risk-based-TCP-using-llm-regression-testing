package com.example;
import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.util.HashMap;
import java.util.Map;

public class CallGraphRiskAnalyzer {
    public static void main(String[] args) {
        String callGraphFile = "call_graph.csv";  // Input Call Graph CSV
        String riskScoreFile = "Predicted_Risk_Scores.csv";  // Input Risk Score CSV

        // Load risk scores into a HashMap
        Map<String, Double> riskScores = loadRiskScores(riskScoreFile);

        // Compute total risk scores for source methods
        Map<String, Double> totalRiskScores = computeTotalRiskScores(callGraphFile, riskScores);

        // Display total risk scores
        System.out.println("Total Risk Scores per Source Method:");
        for (Map.Entry<String, Double> entry : totalRiskScores.entrySet()) {
            System.out.println("Method: " + entry.getKey() + ", Total Risk Score: " + entry.getValue());
        }
    }

    /**
     * Reads the predicted risk score CSV and maps method names to their risk scores.
     */
    private static Map<String, Double> loadRiskScores(String filePath) {
        Map<String, Double> riskScores = new HashMap<>();
        try (BufferedReader br = new BufferedReader(new FileReader(filePath))) {
            String line;
            br.readLine(); // Skip header line
            while ((line = br.readLine()) != null) {
                String[] parts = line.split(",");
                if (parts.length >= 3) {
                    String method = parts[1].trim(); // Method name
                    double riskScore = Double.parseDouble(parts[2].trim()); // Risk Score
                    riskScores.put(method, riskScore);
                }
            }
        } catch (IOException e) {
            System.err.println("Error reading risk score file: " + e.getMessage());
        }
        return riskScores;
    }

    /**
     * Computes the total risk score for each source method in the call graph.
     */
    private static Map<String, Double> computeTotalRiskScores(String filePath, Map<String, Double> riskScores) {
        Map<String, Double> totalRiskScores = new HashMap<>();
        try (BufferedReader br = new BufferedReader(new FileReader(filePath))) {
            String line;
            br.readLine(); // Skip header line
            while ((line = br.readLine()) != null) {
                String[] parts = line.split(",");
                if (parts.length >= 4) {
                    String sourceMethod = parts[1].trim(); // Source method
                    String targetMethod = parts[3].trim(); // Target method

                    // Get risk score of the target method
                    double riskScore = riskScores.getOrDefault(targetMethod, 0.0);

                    // Accumulate risk score for source method
                    totalRiskScores.put(sourceMethod, totalRiskScores.getOrDefault(sourceMethod, 0.0) + riskScore);
                }
            }
        } catch (IOException e) {
            System.err.println("Error reading call graph file: " + e.getMessage());
        }
        return totalRiskScores;
    }
}