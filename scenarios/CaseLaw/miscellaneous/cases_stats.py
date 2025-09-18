import pandas as pd

# Load the CSV
df = pd.read_csv("../dataset/raw/relevant_cases.csv")

# Count occurrences of each decision type
decision_counts = df['decision'].value_counts()

# Print all decision types and counts
for decision, count in decision_counts.items():
    print(f"{decision}: {count}")

