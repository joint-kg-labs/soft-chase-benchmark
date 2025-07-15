import pandas as pd
import random
import csv

# Load ISIN reference CSV
isin_df = pd.read_csv('../dataset/ISIN.csv')

# Function to softly vary security names
def soften_name(original_name):
    name_parts = original_name.split()
    new_parts = name_parts.copy()

    if random.random() < 0.3:
        new_parts.append(random.choice(['Fund', 'Trust', 'Securities', 'Shares']))

    if random.random() < 0.2:
        new_parts = [w for w in new_parts if w.lower() not in ['class', 'series', 'fund']]

    if len(new_parts) > 3 and random.random() < 0.1:
        random.shuffle(new_parts[:3])

    return ' '.join(new_parts)

# Function to softly vary descriptions
def soften_description(original_description):
    words = original_description.split()
    new_words = words.copy()

    if random.random() < 0.3:
        new_words.append(random.choice(['Portfolio', 'Strategy', 'Investment', 'Assets']))

    if len(new_words) > 4 and random.random() < 0.2:
        random.shuffle(new_words[:4])

    return ' '.join(new_words)

# Function to generate soft-matching table and collect ground truth
def generate_soft_matching_table(prefix, ref_df, ground_truth_pairs, column_label):
    data = []
    for idx, row in ref_df.iterrows():
        new_id = prefix + ''.join(random.choices('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=10))
        soft_name = soften_name(row['name'])
        soft_desc = soften_description(row['description'])
        country = row['country']
        type_ = row['type']
        data.append([new_id, soft_name, soft_desc, country, type_])

        # Store ground truth: ISIN ID ↔ new generated ID
        ground_truth_pairs.append({
            'ISIN': row['id'],
            column_label: new_id
        })

    return pd.DataFrame(data, columns=['id', 'name', 'description', 'country', 'type'])

# Prepare ground truth list
ground_truth = []

# Generate datasets with tracking for ground truth
cusip_df = generate_soft_matching_table('CUSIP', isin_df, ground_truth, 'CUSIP')
figi_df = generate_soft_matching_table('FIGI', isin_df, ground_truth, 'FIGI')
sedol_df = generate_soft_matching_table('SEDOL', isin_df, ground_truth, 'SEDOL')

# Save datasets
cusip_df.to_csv('CUSIP.csv', index=False, quoting=csv.QUOTE_MINIMAL)
figi_df.to_csv('FIGI.csv', index=False, quoting=csv.QUOTE_MINIMAL)
sedol_df.to_csv('SEDOL.csv', index=False, quoting=csv.QUOTE_MINIMAL)

# Create combined ground truth DataFrame
# Step 1: Pivot ground_truth into wide format
ground_truth_df = pd.DataFrame(ground_truth)
ground_truth_df = ground_truth_df.groupby('ISIN').first().reset_index()

# Save ground truth
ground_truth_df.to_csv('GROUND_TRUTH.csv', index=False, quoting=csv.QUOTE_MINIMAL)

print("Files generated: CUSIP.csv, FIGI.csv, SEDOL.csv, GROUND_TRUTH.csv")
