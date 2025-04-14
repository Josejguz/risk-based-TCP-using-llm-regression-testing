package com.example;

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintWriter;
import java.util.Arrays;
import java.util.HashMap;
import java.util.Map;

public class RiskScoreCalculator {

    private static final Map<String, Double> riskScores = new HashMap<>();

    public static void main(String[] args) {

        String callGraphFile = "C:\\Users\\jguzm\\Research\\Thesis_Project\\call_graph_output.csv";
        String riskScoresFile = "C:\\Users\\jguzm\\Research\\Thesis_Project\\Predicted_Risk_Scores_1(1).csv";

        loadRiskScores(riskScoresFile);
        processCallGraph(callGraphFile);
    }

    private static void loadRiskScores(String fileName) {
        try (BufferedReader br = new BufferedReader(new FileReader(fileName))) {
            String line;
            br.readLine(); // Skip header
            while ((line = br.readLine()) != null) {
                String[] parts = line.split(",");
                if (parts.length >= 2) {
                    String methodName = parts[0];
                    String riskScoreStr = parts[1];

                    try {
                        double riskScore = Double.parseDouble(riskScoreStr);
                        riskScores.put(methodName, riskScore);
                    } catch (NumberFormatException e) {
                        // If the risk score is not a number, we assign it a score of 0.0
                        riskScores.put(methodName, 0.0);
                    }
                }
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    private static void processCallGraph(String fileName) {
        try (BufferedReader br = new BufferedReader(new FileReader(fileName));
             PrintWriter writer = new PrintWriter(new FileWriter("final_risk_scores.csv"))) {

            writer.println("Class Name,Test Case,Final Risk Score");
            String line;
            br.readLine(); // Skip header

            while ((line = br.readLine()) != null) {
                String[] parts = line.split(",");
                if (parts.length >= 3) {
                    String className = parts[0];
                    String testCase = parts[1];
                    String[] methods = parts[2].split(" \\| ");

                    double totalRiskScore = Arrays.stream(methods)
                            .mapToDouble(method -> riskScores.getOrDefault(method, 0.0))
                            .sum();

                    writer.println(className + "," + testCase + "," + totalRiskScore);
                }
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
