#!/usr/bin/env python3
"""
Build a pairwise golden set for F-score evaluation from a wide mapping file.

Input format: a CSV with identifier families as columns (e.g., ISIN,CUSIP,FIGI,SEDOL),
one entity per row. For each row, the script outputs all ordered pairs of matching IDs:
(id_a, id_b) and (id_b, id_a).

Examples:
  # Run with defaults
  ./build_golden_pairs.py

  # Custom input/output
  ./build_golden_pairs.py -i ../dataset/100/GROUND_TRUTH.csv -o golden_set_fscore.csv

  # Only use specific families/columns
  ./build_golden_pairs.py -i GROUND_TRUTH.csv -o golden.csv --families ISIN CUSIP FIGI
"""

import argparse
import csv
from itertools import combinations
from pathlib import Path
from typing import List

import pandas as pd

# ----------------------------
# Defaults
# ----------------------------
DEFAULT_INPUT = "../ground_truth/100/GROUND_TRUTH.csv"
DEFAULT_OUTPUT = "../ground_truth/100/golden_set_fscore.csv"
DEFAULT_QUOTING = "minimal"  # minimal | all | nonnumeric | none

def _csv_quoting_mode(mode_str: str) -> int:
    return {
        "minimal": csv.QUOTE_MINIMAL,
        "all": csv.QUOTE_ALL,
        "nonnumeric": csv.QUOTE_NONNUMERIC,
        "none": csv.QUOTE_NONE,
    }[mode_str]

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Create a pairwise golden set CSV (id1,id2) from a wide ground-truth mapping."
    )
    p.add_argument("-i", "--input", default=DEFAULT_INPUT,
                   help=f"Input wide CSV (default: {DEFAULT_INPUT})")
    p.add_argument("-o", "--output", default=DEFAULT_OUTPUT,
                   help=f"Output CSV filepath (default: {DEFAULT_OUTPUT})")
    p.add_argument("--families", nargs="*", default=None,
                   help="Optional subset of columns to use (e.g., ISIN CUSIP FIGI). Defaults to all non-empty columns.")
    p.add_argument("--csv-quoting", choices=["minimal", "all", "nonnumeric", "none"],
                   default=DEFAULT_QUOTING, help=f"CSV quoting mode (default: {DEFAULT_QUOTING})")
    return p.parse_args()

def main() -> None:
    args = parse_args()
    df = pd.read_csv(args.input)

    # Determine which columns (families) to use
    if args.families:
        missing = set(args.families) - set(df.columns)
        if missing:
            raise ValueError(f"Input CSV missing requested families/columns: {', '.join(sorted(missing))}")
        families: List[str] = list(args.families)
    else:
        # default to all columns
        families = list(df.columns)

    # Build ordered pairs (id1,id2) for each row (both directions)
    pairs = []
    for _, row in df.iterrows():
        # Collect non-empty values from the chosen families
        vals = []
        for col in families:
            v = row[col]
            if pd.notna(v) and str(v).strip() != "":
                vals.append(str(v).strip())
        # Unique within the row (just in case)
        vals = list(dict.fromkeys(vals))
        # For each unordered pair, emit both directions
        for a, b in combinations(vals, 2):
            pairs.append((a, b))
            pairs.append((b, a))

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    quoting = _csv_quoting_mode(args.csv_quoting)
    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, quoting=quoting)
        writer.writerow(["id1", "id2"])
        writer.writerows(pairs)

    print(f"Wrote {len(pairs):,} rows to {out_path}")

if __name__ == "__main__":
    main()
