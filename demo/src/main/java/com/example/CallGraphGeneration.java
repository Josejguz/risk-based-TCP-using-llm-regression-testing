package com.example;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.List;

import soot.G;
import soot.Scene;
import soot.SootMethod;
import soot.jimple.toolkits.callgraph.CallGraph;
import soot.jimple.toolkits.callgraph.Edge;
import soot.options.Options;

public class CallGraphGeneration {

    public static void main(String[] args) {

    	String directoryPath = "C:\\Users\\jguzm\\eclipse-workspace\\RiskBasedTCP\\src\\test\\java\\bag";
        File directory = new File(directoryPath);

        if (!directory.exists() || !directory.isDirectory()) {
            System.out.println("Invalid directory path: " + directoryPath);
            System.exit(0);
        }

        List<String> classPaths = new ArrayList<>();
        for (File file : directory.listFiles()) {
            if (file.isFile() && file.getName().endsWith(".java")) {
                classPaths.add(file.getParent());
            }
        }

        if (classPaths.isEmpty()) {
            System.out.println("No Java files found in the directory.");
            System.exit(0);
        }

        // Resetting Soot before use
        G.reset();

        // Detecting Java runtime location
        String javaHome = System.getProperty("java.home");
        String javaRuntimePath = javaHome + File.separator + "lib" + File.separator + "rt.jar"; // For JDK 8 and below
        String javaModulesPath = javaHome + File.separator + "lib" + File.separator + "modules"; // For JDK 9 and above

        String sootClassPath = System.getProperty("java.class.path");
        if (Files.exists(Paths.get(javaRuntimePath))) {
            sootClassPath += File.pathSeparator + javaRuntimePath;
        } else if (Files.exists(Paths.get(javaModulesPath))) {
            sootClassPath += File.pathSeparator + javaModulesPath;
        } else {
            System.out.println("Could not find the Java standard library (rt.jar or modules). Make sure your JAVA_HOME is correctly set.");
            System.exit(0);
        }

        // Configure Soot
        Options.v().set_soot_classpath(sootClassPath);
        Options.v().set_whole_program(true);
        Options.v().set_app(true);
        Options.v().set_allow_phantom_refs(true);
        Options.v().set_process_dir(classPaths);

        // Load all classes and their dependencies
        Scene.v().loadNecessaryClasses();

        // Generate call graph
        CallGraph callGraph = Scene.v().getCallGraph();

        // Create CSV file
        try (FileWriter csvWriter = new FileWriter("call_graph_output.csv")) {
            csvWriter.append("Class Name, Test Case Name, Source Method, Target Method\n");

            // Print the call graph
            for (Edge edge : callGraph) {
                SootMethod src = edge.src();
                SootMethod tgt = edge.tgt();

                String srcClassName = src.getDeclaringClass().getName();
                String tgtClassName = tgt.getDeclaringClass().getName();

                csvWriter.append(srcClassName + ", " + src.getName() + ", " + srcClassName + "." + src.getName() + ", " + tgtClassName + "." + tgt.getName() + "\n");
            }
            csvWriter.flush();
            System.out.println("Call graph has been saved to call_graph_output.csv");

        } catch (IOException e) {
            System.err.println("An error occurred while writing the call graph to the CSV file: " + e.getMessage());
        }
    }
}