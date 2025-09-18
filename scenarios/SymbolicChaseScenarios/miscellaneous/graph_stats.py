#!/usr/bin/env python3
import os
import sys
import pandas as pd

def analyze_graph(csv_path):
    """Read a CSV file containing a binary relation (edges) and return node/edge counts."""
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        print(f"⚠️ Could not read {csv_path}: {e}")
        return None

    if df.shape[1] < 2:
        print(f"⚠️ Skipping {csv_path}: less than 2 columns found")
        return None

    # assume first two columns are source and target
    src_col, tgt_col = df.columns[0], df.columns[1]
    edges = list(zip(df[src_col], df[tgt_col]))

    num_edges = len(edges)
    nodes = set(df[src_col]).union(set(df[tgt_col]))
    num_nodes = len(nodes)

    return {
        "file": os.path.basename(csv_path),
        "nodes": num_nodes,
        "edges": num_edges,
    }

def main(folder_path):
    if not os.path.isdir(folder_path):
        print(f"❌ {folder_path} is not a valid folder.")
        sys.exit(1)

    csv_files = [f for f in os.listdir(folder_path) if f.endswith(".csv")]
    if not csv_files:
        print(f"❌ No CSV files found in {folder_path}")
        sys.exit(1)

    print(f"📊 Graph statistics for {len(csv_files)} CSV file(s) in {folder_path}:\n")
    for csv_file in csv_files:
        csv_path = os.path.join(folder_path, csv_file)
        stats = analyze_graph(csv_path)
        if stats:
            print(f"{stats['file']}: {stats['nodes']} nodes, {stats['edges']} edges")

if __name__ == "__main__":
    folder = "../graphs"
    main(folder)
