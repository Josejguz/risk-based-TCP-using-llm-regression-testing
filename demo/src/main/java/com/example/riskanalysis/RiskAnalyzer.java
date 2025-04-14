package com.example.riskanalysis;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.stream.Collectors;

import com.example.riskanalysis.model.MethodMetrics;
import com.github.javaparser.StaticJavaParser;
import com.github.javaparser.ast.CompilationUnit;
import com.github.javaparser.ast.body.MethodDeclaration;

public class RiskAnalyzer {

    // Maps to track which methods call which other methods and vice versa
    private static final Map<String, Set<String>> methodCallers = new HashMap<>();
    private static final Map<String, Set<String>> methodCalls = new HashMap<>();

    /**
     * Analyzes all Java files in a given directory and writes the analysis results
     * to the provided text and CSV writers.
     *
     * @param directoryPath The path to the directory containing Java files.
     * @param txtWriter     BufferedWriter for writing text output.
     * @param csvWriter     BufferedWriter for writing CSV output.
     * @throws IOException If an I/O error occurs.
     */
    public static void analyzeDirectory(String directoryPath, BufferedWriter txtWriter, BufferedWriter csvWriter) throws IOException {

        // Collect all Java files in the directory and its subdirectories
        List<File> javaFiles = Files.walk(Paths.get(directoryPath))
            .filter(Files::isRegularFile) // Only regular files
            .filter(path -> path.toString().endsWith(".java")) // Only Java files
            .map(Path::toFile)
            .collect(Collectors.toList());

        // Analyze each Java file
        for (File file : javaFiles) {
            analyzeFile(file, txtWriter, csvWriter);
        }
    }

    /**
     * Analyzes a single Java file, extracting method metrics and writing results
     * to the provided writers.
     *
     * @param file      The Java file to analyze.
     * @param txtWriter BufferedWriter for writing text output.
     * @param csvWriter BufferedWriter for writing CSV output.
     * @throws IOException If an I/O error occurs.
     */
    private static void analyzeFile(File file, BufferedWriter txtWriter, BufferedWriter csvWriter) throws IOException {

        // Write a header for the file analysis
        txtWriter.write("===================================================================================\n");
        txtWriter.write("\nAnalyzing file: " + file.getName() + "\n");

        // Parse the Java file into a CompilationUnit (AST representation)
        CompilationUnit cu = StaticJavaParser.parse(new FileInputStream(file));

        // Find all method declarations in the file
        cu.findAll(MethodDeclaration.class).forEach(method -> {
            try {
                // Get the method name
                String methodName = method.getNameAsString();

                // Initialize the methodCalls map for this method
                methodCalls.putIfAbsent(methodName, new HashSet<>());

                // Visit all method call expressions within this method
                method.accept(new com.github.javaparser.ast.visitor.VoidVisitorAdapter<Void>() {
                    @Override
                    public void visit(com.github.javaparser.ast.expr.MethodCallExpr call, Void arg) {

                        // Record the method being called
                        methodCalls.get(methodName).add(call.getNameAsString());

                        // Record the caller for the called method
                        methodCallers.computeIfAbsent(call.getNameAsString(), k -> new HashSet<>()).add(methodName);
                        super.visit(call, arg);
                    }
                }, null);

                // Create a MethodMetrics object to store metrics for this method
                MethodMetrics metrics = new MethodMetrics();
                metrics.methodName = methodName;
                metrics.fileName = file.getName();

                // Calculate cyclomatic complexity
                metrics.complexity = MetricCalculator.calculateCyclomaticComplexity(method);

                // Calculate lines of code
                metrics.linesOfCode = MetricCalculator.calculateLinesOfCode(method);

                // Calculate dependencies
                metrics.dependencies = MetricCalculator.calculateDependencies(method);

                // Count the number of input parameters
                metrics.inputs = method.getParameters().size();

                // Calculate fan-out (number of methods called by this method)
                metrics.fanOut = methodCalls.get(methodName).size();

                // Calculate fan-in (number of methods that call this method)
                metrics.fanIn = methodCallers.getOrDefault(methodName, Set.of()).size();
                
                // Calculate lack of cohesion in methods (LCOM)
                metrics.lcom = LCOMCalculator.calculate(method);

                // Write the metrics to the text and CSV writers
                txtWriter.write(metrics.toText());
                csvWriter.write(metrics.toCSV());

            } catch (Exception e) {
                
                // Handle any errors that occur during method analysis
                System.err.println("Error analyzing method: " + method.getNameAsString());
                e.printStackTrace();
            }
        });
    }
}
