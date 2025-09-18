import pandas as pd

# 1️⃣ Process cases_texas_augmented.csv
cases_aug = pd.read_csv("../dataset/raw/cases_texas_augmented.csv")

# Project the desired columns
cases = cases_aug[['id', 'name', 'decision_date', 'jurisdiction_name', 'parties', 'offense', 'punishment', 'decision']]

# Save to cases.csv
cases.to_csv("../dataset/cases.csv", index=False)


# 2️⃣ Process new_cases_texas.csv
new_cases_aug = pd.read_csv("../dataset/raw/new_cases_texas.csv")

# Project the desired columns
new_cases = new_cases_aug[['id', 'name', 'offense']]

# Save to new_cases.csv
new_cases.to_csv("../dataset/new_cases.csv", index=False)


# 3️⃣ Process case_details_texas.csv
details_aug = pd.read_csv("../dataset/raw/case_details_texas.csv")

# Project the desired columns
case_details = details_aug[['head_matter', 'corrections', 'opinions']]

# Rename 'head_matter' to 'matter'
case_details = case_details.rename(columns={'head_matter': 'matter'})

# Save to case_details.csv
case_details.to_csv("../dataset/case_details.csv", index=False)

print("All three files created successfully!")
