package com.example.riskanalysis;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

import com.github.javaparser.ast.body.MethodDeclaration;
import com.github.javaparser.ast.expr.NameExpr;
import com.github.javaparser.ast.expr.VariableDeclarationExpr;
import com.github.javaparser.ast.visitor.VoidVisitorAdapter;

public class LCOMCalculator {

    /**
     * Calculates the Lack of Cohesion of Methods (LCOM) for a single method using component-based analysis.
     *
     * @param method The method to analyze.
     * @return The LCOM value for the method.
     */
    public static int calculate(MethodDeclaration method) {
        // Step 1: Extract all variables used in the method
        Set<String> variables = new HashSet<>();
        method.accept(new VoidVisitorAdapter<Void>() {
            @Override
            public void visit(VariableDeclarationExpr varDecl, Void arg) {
                varDecl.getVariables().forEach(var -> variables.add(var.getNameAsString()));
                super.visit(varDecl, arg);
            }

            @Override
            public void visit(NameExpr nameExpr, Void arg) {
                variables.add(nameExpr.getNameAsString());
                super.visit(nameExpr, arg);
            }
        }, null);

        // Step 2: Divide the method into components (e.g., statements, expressions)
        List<Set<String>> components = new ArrayList<>();
        method.accept(new VoidVisitorAdapter<Void>() {
            @Override
            public void visit(VariableDeclarationExpr varDecl, Void arg) {
                Set<String> componentVars = new HashSet<>();
                varDecl.getVariables().forEach(var -> componentVars.add(var.getNameAsString()));
                components.add(componentVars);
                super.visit(varDecl, arg);
            }

            @Override
            public void visit(NameExpr nameExpr, Void arg) {
                Set<String> componentVars = new HashSet<>();
                componentVars.add(nameExpr.getNameAsString());
                components.add(componentVars);
                super.visit(nameExpr, arg);
            }
        }, null);

        // Step 3: Calculate P (shared variables) and Q (no shared variables)
        int P = 0, Q = 0;
        for (int i = 0; i < components.size(); i++) {
            for (int j = i + 1; j < components.size(); j++) {
                Set<String> intersection = new HashSet<>(components.get(i));
                intersection.retainAll(components.get(j));
                if (intersection.isEmpty()) Q++;
                else P++;
            }
        }

        // Step 4: Compute LCOM = max(0, Q - P)
        return Math.max(0, Q - P);
    }
}
