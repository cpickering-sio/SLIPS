run("16-bit");
setAutoThreshold("Default dark 16-bit no-reset");
//run("Threshold...");
setThreshold(0, 252, "raw");
run("Measure");
setThreshold(0, 252, "raw");
