package com.example.riskanalysis;
import java.io.BufferedWriter;
import java.io.FileWriter;

/**
 * The Main class serves as the entry point for the Risk Analysis application.
 * It performs a risk analysis on Java source files located in a specified directory
 * and outputs the results to both a text file and a CSV file.
 *
 * <p>Functionality:
 * - Reads Java source files from the specified directory.
 * - Analyzes each file for various metrics such as cyclomatic complexity, lines of code,
 *   dependencies, inputs, fan-in, fan-out, lack of cohesion of methods (LCOM), and calculates a risk score.
 * - Writes the analysis results to "Risk_results.txt" and "Risk_results.csv".
 *
 * <p>Usage:
 * - Update the `path` variable to point to the directory containing the Java source files to analyze.
 * - Run the program, and the results will be saved in the current working directory.
 *
 * <p>Output:
 * - "Risk_results.txt": A human-readable summary of the risk analysis.
 * - "Risk_results.csv": A detailed CSV file containing metrics for each analyzed method.
 *
 * @throws Exception if an error occurs during file writing or directory analysis.
 */
public class Main {
    public static void main(String[] args) throws Exception {
        String path = "C:\\Users\\jguzm\\Downloads\\commons-collections_Version2\\commons-collections4-4.5.0-M2-src\\src\\main\\java\\org\\apache\\commons\\collections4\\collection";
        try (BufferedWriter txtWriter = new BufferedWriter(new FileWriter("Risk_results_V2.txt"));
             BufferedWriter csvWriter = new BufferedWriter(new FileWriter("Risk_results_V2.csv"))) {

            txtWriter.write("Risk Analysis Results:\n");
            csvWriter.write("File,Method,Cyclomatic_Complexity,Lines_of_Code,Dependencies,Inputs,FanIn,FanOut,LCOM\n");

            RiskAnalyzer.analyzeDirectory(path, txtWriter, csvWriter);

            System.out.println("Analysis complete.");
        }
    }
}