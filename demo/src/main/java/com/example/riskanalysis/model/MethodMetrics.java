package com.example.riskanalysis.model;

public class MethodMetrics {
    
    // Fields to store various metrics related to a method
    public String fileName; // Name of the file containing the method
    public String methodName; // Name of the method
    public int complexity; // Cyclomatic complexity of the method
    public int linesOfCode; // Number of lines of code in the method
    public int dependencies; // Number of dependencies the method has
    public int inputs; // Number of input parameters for the method
    public int fanIn; // Number of other methods that call this method
    public int fanOut; // Number of methods this method calls
    public int lcom; // Lack of Cohesion in Methods (LCOM) metric

    /**
     * Converts the method metrics into a human-readable text format.
     * @return A formatted string containing all the metrics of the method.
     */
    public String toText() {
        return String.format("Method: %s\n  - Cyclomatic Complexity: %d\n  - Lines of Code: %d\n  - Dependencies: %d\n  - Inputs: %d\n  - Fan-In: %d\n  - Fan-Out: %d\n  - LCOM: %d\n\n",
                methodName, complexity, linesOfCode, dependencies, inputs, fanIn, fanOut, lcom);
    }

    /**
     * Converts the method metrics into a CSV (Comma-Separated Values) format.
     * Escapes double quotes in fileName and methodName to ensure valid CSV formatting.
     * @return A CSV-formatted string containing all the metrics of the method.
     */
    public String toCSV() {
        return String.format("\"%s\",\"%s\",%d,%d,%d,%d,%d,%d,%d\n",
                fileName.replace("\"", "\"\""), // Escape double quotes in fileName
                methodName.replace("\"", "\"\""), // Escape double quotes in methodName
                complexity, linesOfCode, dependencies, inputs, fanIn, fanOut, lcom);
    }
}
