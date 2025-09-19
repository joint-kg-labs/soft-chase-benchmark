import pandas as pd

# Load the CSVs
relevant_cases = pd.read_csv("../dataset/raw/relevant_cases_augmented.csv")
should_cite = pd.read_csv("../dataset/raw/should_cite.csv")

# Keep only rows where convicted == True
convicted_cases = relevant_cases[relevant_cases["convicted"] == True]

# Join should_cite.idCited with convicted_cases.id
joined = should_cite.merge(convicted_cases, left_on="idCited", right_on="id", how="inner")

# Project the required columns
golden_set = joined[["idNewCase", "idCited", "name"]]

# Save to CSV
golden_set.to_csv("../ground_truth/golden_set_relevantCase_fscore.csv", index=False)

print("✅ File saved as golden_set_relevantCase_fscore.csv")
