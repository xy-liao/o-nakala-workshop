# Sample R Script for Data Analysis
# This script demonstrates basic data analysis on sample data

# Load required libraries
library(ggplot2)
library(dplyr)

# Read data
data <- read.csv("../data/analysis_results.csv")

# Basic summary statistics
summary_stats <- summary(data)
print(summary_stats)

# Create a simple plot
if ("value" %in% names(data)) {
  p <- ggplot(data, aes(x = variable, y = value)) +
    geom_boxplot() +
    theme_minimal() +
    labs(title = "Sample Data Analysis",
         x = "Variable",
         y = "Value")
  
  # Save the plot
  ggsave("../images/analysis_plot.png", plot = p, width = 8, height = 6)
}

# Perform statistical analysis
if (exists("summary_stats")) {
  write.csv(summary_stats, "../data/summary_statistics.csv", row.names = FALSE)
}
