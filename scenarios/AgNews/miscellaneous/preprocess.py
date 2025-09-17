import pandas as pd

# Load CSV
df = pd.read_csv("../dataset/news_100k.csv")

# Regex to match stock-related words: stock(s), stock-market, equity/ies, share(s)
pattern = r'\b(stock[s\-]?\w*|equit(y|ies)|share[s]?)\b'

# Filter rows matching any of these terms in Description
stock_df = df[df['Description'].str.contains(pattern, case=False, regex=True)].copy()
non_stock_df = df[~df['Description'].str.contains(pattern, case=False, regex=True)].copy()

# Add flag column
stock_df['IsStock'] = True
non_stock_df['IsStock'] = False

# Determine number of rows to sample
n_total = 10000
n_each = n_total // 2

# Sample rows
stock_sample = stock_df.sample(n=min(n_each, len(stock_df)), random_state=42)
non_stock_sample = non_stock_df.sample(n=min(n_each, len(non_stock_df)), random_state=42)

# Combine the samples and shuffle
combined_sample = pd.concat([stock_sample, non_stock_sample]).sample(frac=1, random_state=42).reset_index(drop=True)

# Save to CSV
combined_sample.to_csv("../dataset/news_10k_balanced.csv", index=False)

print(f"Sampled {len(stock_sample)} stock-related rows and {len(non_stock_sample)} non-stock rows.")
print(f"Total sampled rows: {len(combined_sample)}")
