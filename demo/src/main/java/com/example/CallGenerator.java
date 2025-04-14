package com.example;
import java.io.File;
import java.io.FileWriter;
import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;

import soot.G;
import soot.PackManager;
import soot.Scene;
import soot.SootClass;
import soot.SootMethod;
import soot.options.Options;


public class CallGenerator {

    public static void main(String[] args) {
        String targetClass = "org.apache.commons.collections4.BagUtilsTest";
        String commonsPath = "C:\\Users\\jguzm\\Downloads\\commons-collections_Version2\\commons-collections4-4.5.0-M2-src";
        String outputDir = "soot_output";

        if (args.length >= 1) targetClass = args[0];
        if (args.length >= 2) commonsPath = args[1];
        if (args.length >= 3) outputDir = args[2];

        String targetClasses = commonsPath + "/target/classes";
        String targetTestClasses = commonsPath + "/target/test-classes";
        String classPath = targetClasses + ":" + targetTestClasses;

        System.out.println("Target class: " + targetClass);
        System.out.println("Class path: " + classPath);
        System.out.println("Output directory: " + outputDir);

        new File(outputDir).mkdirs();

        try {
            G.reset();
            Options.v().set_prepend_classpath(true);
            Options.v().set_allow_phantom_refs(true);
            Options.v().set_soot_classpath(classPath);
            Options.v().set_output_format(Options.output_format_jimple);
            Options.v().set_output_dir(outputDir);
            Options.v().set_keep_line_number(true);
            Options.v().set_whole_program(true);
            Options.v().set_app(true);
            Options.v().setPhaseOption("cg", "enabled:true");
            Options.v().setPhaseOption("cg", "verbose:true");
            Options.v().setPhaseOption("cg", "all-reachable:true");
            Options.v().set_no_bodies_for_excluded(true);

            List<String> processDirs = new ArrayList<>();
            processDirs.add(targetClasses);
            processDirs.add(targetTestClasses);
            Options.v().set_process_dir(processDirs);

            SootClass c = Scene.v().loadClassAndSupport(targetClass);
            c.setApplicationClass();

            System.out.println("Loading necessary classes...");
            Scene.v().loadNecessaryClasses();

            System.out.println("Running Soot packs to generate call graph...");
            PackManager.v().runPacks();

            soot.jimple.toolkits.callgraph.CallGraph cg = Scene.v().getCallGraph();
            System.out.println("Call graph generated with " + cg.size() + " edges");

            File csvFile = new File(outputDir, "callgraph.csv");

            try (PrintWriter writer = new PrintWriter(new FileWriter(csvFile))) {
                writer.println("TestCase,Source,Target");

                int count = 0;
                Iterator<soot.jimple.toolkits.callgraph.Edge> edgeIt = cg.iterator();
                while (edgeIt.hasNext()) {
                    soot.jimple.toolkits.callgraph.Edge edge = edgeIt.next();
                    SootMethod src = edge.src();
                    SootMethod tgt = edge.tgt();

                    if (src.getDeclaringClass().isApplicationClass()) {
                        String srcStr = simplifyMethodName(src);
                        String tgtStr = simplifyMethodName(tgt);

                        // Try to extract test case name based on test class or method
                        String testCaseName = extractTestCaseName(src);

                        writer.println(escapeCsv(testCaseName) + "," + escapeCsv(srcStr) + "," + escapeCsv(tgtStr));
                        count++;
                    }
                }

                System.out.println("Wrote " + count + " call graph edges to CSV");
            }

            System.out.println("Call graph written to " + csvFile.getAbsolutePath());

        } catch (Exception e) {
            System.err.println("Error generating call graph: " + e.getMessage());
            e.printStackTrace();
        }
    }

    private static String simplifyMethodName(SootMethod method) {
        return method.getDeclaringClass().getName() + "." + method.getName();
    }

    private static String extractTestCaseName(SootMethod method) {
        String className = method.getDeclaringClass().getName();
        String methodName = method.getName();

        if (className.toLowerCase().contains("test") || methodName.toLowerCase().contains("test")) {
            return className + "#" + methodName;
        } else {
            return "";
        }
    }

    private static String escapeCsv(String input) {
        if (input == null) return "";
        if (input.contains(",") || input.contains("\"")) {
            input = input.replace("\"", "\"\"");
            return "\"" + input + "\"";
        }
        return input;
    }
}
