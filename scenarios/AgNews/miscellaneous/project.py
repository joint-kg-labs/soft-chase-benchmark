import pandas as pd

# --- Input / Output ---
input_file = "../dataset/raw/news_10k_augmented.csv"  # your input CSV
output_file = "../dataset/agnews500.csv"  # projected output CSV

# --- Load CSV ---
df = pd.read_csv(input_file)

# --- Project desired columns ---
projected = df[["id", "Title", "Description"]]

# --- Save result ---
projected.to_csv(output_file, index=False)

print(f"✅ Projected file saved to {output_file}")
print(projected.head())  # preview first 5 rows

