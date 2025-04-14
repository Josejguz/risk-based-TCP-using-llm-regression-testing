package com.example.riskanalysis;

import java.util.HashSet;
import java.util.Set;

import com.github.javaparser.ast.body.MethodDeclaration;
import com.github.javaparser.ast.expr.MethodCallExpr;
import com.github.javaparser.ast.expr.ObjectCreationExpr;
import com.github.javaparser.ast.visitor.VoidVisitorAdapter;

public class MetricCalculator {

    /**
     * Calculates the cyclomatic complexity of a given method.
     * Cyclomatic complexity is determined by counting the number of decision points in the method.
     * 
     * @param method The method declaration to analyze.
     * @return The cyclomatic complexity of the method.
     */
    public static int calculateCyclomaticComplexity(MethodDeclaration method) {
        int complexity = 1; // Start with a base complexity of 1.
        
        // Add complexity for each type of control flow statement.
        complexity += method.findAll(com.github.javaparser.ast.stmt.IfStmt.class).size(); // Count 'if' statements.
        complexity += method.findAll(com.github.javaparser.ast.stmt.ForStmt.class).size(); // Count 'for' loops.
        complexity += method.findAll(com.github.javaparser.ast.stmt.WhileStmt.class).size(); // Count 'while' loops.
        complexity += method.findAll(com.github.javaparser.ast.stmt.DoStmt.class).size(); // Count 'do-while' loops.
        complexity += method.findAll(com.github.javaparser.ast.stmt.SwitchStmt.class).size(); // Count 'switch' statements.
        complexity += method.findAll(com.github.javaparser.ast.stmt.CatchClause.class).size(); // Count 'catch' blocks.
        
        // Add complexity for logical operators '&&' and '||' in binary expressions.
        complexity += method.findAll(com.github.javaparser.ast.expr.BinaryExpr.class,
                be -> be.getOperator().asString().equals("&&") || be.getOperator().asString().equals("||")).size();
        
        return complexity; // Return the total calculated complexity.
    }

    /**
     * Calculates the number of lines of code (LOC) in a given method.
     * This is done by summing up the line ranges of all statements in the method body.
     * 
     * @param method The method declaration to analyze.
     * @return The total number of lines of code in the method.
     */
    public static int calculateLinesOfCode(MethodDeclaration method) {
        return method.getBody().map(body -> 
            body.getStatements().stream()

                // Calculate the line range for each statement and sum them up.
                .mapToInt(stmt -> stmt.getEnd().map(p -> p.line).orElse(0) - stmt.getBegin().map(p -> p.line).orElse(0) + 1)
                .sum()
        ).orElse(0); // Return 0 if the method body is empty or absent.
    }

    /**
     * Calculates the number of dependencies in a given method.
     * Dependencies are determined by counting method calls and object creations within the method.
     * 
     * @param method The method declaration to analyze.
     * @return The total number of dependencies in the method.
     */
    public static int calculateDependencies(MethodDeclaration method) {
        
        Set<String> calls = new HashSet<>(); // Set to store unique method call names.
        Set<String> creations = new HashSet<>(); // Set to store unique object creation types.

        // Use a visitor to traverse the method and collect method calls and object creations.
        method.accept(new VoidVisitorAdapter<Void>() {
            @Override
            public void visit(MethodCallExpr call, Void arg) {
                calls.add(call.getNameAsString()); // Add the method call name to the set.
                super.visit(call, arg); // Continue visiting other nodes.
            }

            @Override
            public void visit(ObjectCreationExpr creation, Void arg) {
                creations.add(creation.getType().asString()); // Add the object creation type to the set.
                super.visit(creation, arg); // Continue visiting other nodes.
            }
        }, null);

        // Return the total number of unique method calls and object creations.
        return calls.size() + creations.size();
    }
}
