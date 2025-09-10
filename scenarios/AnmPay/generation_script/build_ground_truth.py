import pandas as pd

# Load CSVs
payments = pd.read_csv("../dataset/payments.csv")
accounts = pd.read_csv("../dataset/accounts.csv")  # Not directly needed here, but loaded if useful
reason_variations = pd.read_csv("../dataset/reason_variations.csv")
base_reasons = pd.read_csv("../generation_script/base_reasons.csv")

# 1) Map payment_reason -> base_reason
payments = payments.merge(reason_variations, how="left",
                          left_on="payment_reason", right_on="variation")

# 2) Map base_reason -> category
payments = payments.merge(base_reasons, how="left",
                          left_on="base_reason", right_on="reason")

# Cleanup (drop extra cols)
payments = payments.drop(columns=["variation", "reason"])

# 3) Count categories per bic_origin
category_counts = (
    payments.groupby(["bic_origin", "category"])
    .size()
    .reset_index(name="count")
)

# 4) Get dominant category + its frequency
dominant = (
    category_counts.sort_values(["bic_origin", "count"], ascending=[True, False])
    .drop_duplicates("bic_origin", keep="first")
    .rename(columns={"category": "dominant_category", "count": "dominant_count"})
)

# 5) Join back to payments
payments = payments.merge(dominant[["bic_origin", "dominant_category", "dominant_count"]],
                          on="bic_origin", how="left")

# 6) Extract anomalous payments (category != dominant) and drop duplicates
anomalies = (
    payments[payments["category"] != payments["dominant_category"]]
    .drop_duplicates()
)

print("\nAnomalous payments (not matching dominant category):")
print(anomalies[["payment_id", "bic_origin", "payment_reason",
                 "category", "dominant_category", "dominant_count"]])

anomalies[["payment_id"]].to_csv("../ground_truth/golden_set_fscore.csv", index=False)
