package com.example.riskanalysis;

import com.example.riskanalysis.model.MethodMetrics;

// This class is responsible for calculating a risk score based on various metrics of a method.
public class RiskScoreCalculator {

    /**
     * Calculates the risk score for a given method based on its metrics.
     * 
     * @param m An instance of MethodMetrics containing various metrics of the method.
     *          The metrics include:
     *          - complexity: The cyclomatic complexity of the method.
     *          - linesOfCode: The number of lines of code in the method.
     *          - dependencies: The number of dependencies the method has.
     *          - inputs: The number of input parameters the method takes.
     *          - fanIn: The number of other methods that call this method.
     *          - fanOut: The number of methods this method calls.
     *          - lcom: The lack of cohesion in methods (LCOM) metric.
     * 
     * @return The calculated risk score as a double. The score is the average of all the metrics.
     */
    public static double calculate(MethodMetrics m) {
        // Sum up all the metrics and divide by the total number of metrics (7) to get the average.
        return (m.complexity + m.linesOfCode + m.dependencies + m.inputs + m.fanIn + m.fanOut + m.lcom) / 7.0;
    }
}
