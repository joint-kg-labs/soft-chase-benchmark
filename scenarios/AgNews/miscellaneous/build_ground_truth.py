import pandas as pd


def main():
    # --- Load CSV ---
    input_file = "../dataset/raw/news_10k_augmented.csv"  # your CSV with Sentiment
    df = pd.read_csv(input_file)

    # --- Keep only the first 500 columns (if fewer exist, it keeps all) ---
    df = df.iloc[0:500, :]

    # --- Filter Business category ---
    business_df = df[df["Category"] == "Business"]

    # --- Pump: Positive sentiment ---
    pump_df = business_df[business_df["Sentiment"] == "Positive"][["id", "Title", "Description"]]
    pump_df.to_csv("../ground_truth/500/golden_set_pump_fscore.csv", index=False)
    print(f"✅ Pump dataset saved: {len(pump_df)} rows")

    # --- Dump: Negative sentiment ---
    dump_df = business_df[business_df["Sentiment"] == "Negative"][["id", "Title", "Description"]]
    dump_df.to_csv("../ground_truth/500/golden_set_dump_fscore.csv", index=False)
    print(f"✅ Dump dataset saved: {len(dump_df)} rows")

    # --- Optional preview ---
    print("\nPump preview:")
    print(pump_df.head())

    print("\nDump preview:")
    print(dump_df.head())


if __name__ == "__main__":
    main()
