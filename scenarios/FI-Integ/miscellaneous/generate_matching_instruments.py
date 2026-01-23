#!/usr/bin/env python3
"""
Generate softly-matching identifier datasets (e.g., CUSIP/FIGI/SEDOL) from an ISIN reference CSV,
and produce a wide-format ground-truth mapping.

Examples:
  # Run with all defaults
  ./generate_soft_ids.py

  # Basic: read ISIN.csv and generate all 3 + ground truth in ./out
  ./generate_soft_ids.py -i ../dataset/10k/ISIN.csv -o out

  # Only CUSIP & FIGI, custom prefixes and id length
  ./generate_soft_ids.py -i ISIN.csv -o out --ids CUSIP FIGI --prefix CUSIP=CUS FIGI=BBG --id-length 10

  # Reproducible, sample 2,000 rows from input, custom quoting
  ./generate_soft_ids.py -i ISIN.csv -o out -r 2000 --seed 123 --csv-quoting all

  # Add a custom ID family "MYID" with its own prefix
  ./generate_soft_ids.py -i ISIN.csv -o out --ids MYID --prefix MYID=MYX
"""

import argparse
import csv
import random
from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd

# ----------------------------
# Defaults
# ----------------------------
DEFAULT_INPUT = "../dataset/100/ISIN.csv"
DEFAULT_IDS = ["CUSIP", "FIGI", "SEDOL"]
DEFAULT_OUTPUT_DIR = "../dataset/100"
DEFAULT_ID_LENGTH = 10          # random suffix after prefix
DEFAULT_SEED = 42
DEFAULT_SAMPLE_ROWS = None      # use all rows
DEFAULT_NAME_APPEND_P = 0.3
DEFAULT_NAME_STRIP_P = 0.2
DEFAULT_NAME_SHUFFLE_P = 0.1
DEFAULT_DESC_APPEND_P = 0.3
DEFAULT_DESC_SHUFFLE_P = 0.2

# ----------------------------
# Softening helpers
# ----------------------------
def soften_name(original_name: str,
                append_p: float,
                strip_p: float,
                shuffle_p: float) -> str:
    name_parts = original_name.split()
    new_parts = name_parts.copy()

    if random.random() < append_p:
        new_parts.append(random.choice(['Fund', 'Trust', 'Securities', 'Shares']))

    if random.random() < strip_p:
        new_parts = [w for w in new_parts if w.lower() not in ['class', 'series', 'fund']]

    if len(new_parts) > 3 and random.random() < shuffle_p:
        # shuffle only the first 3 tokens for subtlety
        first_three = new_parts[:3]
        random.shuffle(first_three)
        new_parts = first_three + new_parts[3:]

    return ' '.join(new_parts)

def soften_description(original_description: str,
                       append_p: float,
                       shuffle_p: float) -> str:
    words = original_description.split()
    new_words = words.copy()

    if random.random() < append_p:
        new_words.append(random.choice(['Portfolio', 'Strategy', 'Investment', 'Assets']))

    if len(new_words) > 4 and random.random() < shuffle_p:
        first_four = new_words[:4]
        random.shuffle(first_four)
        new_words = first_four + new_words[4:]

    return ' '.join(new_words)

# ----------------------------
# Core generation
# ----------------------------
def new_id(prefix: str, id_length: int) -> str:
    return prefix + ''.join(random.choices('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=id_length))

def generate_soft_matching_table(prefix: str,
                                 ref_df: pd.DataFrame,
                                 ground_truth_pairs: List[Dict[str, str]],
                                 column_label: str,
                                 id_length: int,
                                 name_params: Tuple[float, float, float],
                                 desc_params: Tuple[float, float]) -> pd.DataFrame:
    name_append_p, name_strip_p, name_shuffle_p = name_params
    desc_append_p, desc_shuffle_p = desc_params

    rows = []
    for _, row in ref_df.iterrows():
        nid = new_id(prefix, id_length)
        soft_name = soften_name(row['name'], name_append_p, name_strip_p, name_shuffle_p)
        soft_desc = soften_description(row['description'], desc_append_p, desc_shuffle_p)
        rows.append([nid, soft_name, soft_desc, row['country'], row['type']])

        # Ground truth mapping: ISIN -> new family ID
        ground_truth_pairs.append({'ISIN': row['id'], column_label: nid})

    return pd.DataFrame(rows, columns=['id', 'name', 'description', 'country', 'type'])

# ----------------------------
# CLI
# ----------------------------
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create softly-matching ID datasets (CUSIP/FIGI/SEDOL/etc.) from an ISIN CSV and a ground-truth map."
    )

    # I/O
    parser.add_argument(
        "-i", "--input",
        default=DEFAULT_INPUT,
        help=f"Path to ISIN CSV with columns: id,name,description,country,type (default: {DEFAULT_INPUT})"
    )
    parser.add_argument(
        "-o", "--outdir",
        default=DEFAULT_OUTPUT_DIR,
        help=f"Output directory (default: {DEFAULT_OUTPUT_DIR})"
    )
    parser.add_argument(
        "--csv-quoting",
        choices=["minimal", "all", "nonnumeric", "none"],
        default="minimal",
        help="CSV quoting mode (default: minimal)"
    )

    # What to generate
    parser.add_argument(
        "--ids", nargs="+",
        default=DEFAULT_IDS,
        help=f"ID families to generate (default: {', '.join(DEFAULT_IDS)}). Example: --ids CUSIP FIGI"
    )
    parser.add_argument(
        "--prefix", nargs="*",
        default=[],
        help="Override prefixes per ID family, e.g. --prefix CUSIP=CUS FIGI=BBG SEDOL=SDL"
    )

    # Controls
    parser.add_argument(
        "--id-length", type=int,
        default=DEFAULT_ID_LENGTH,
        help=f"Random suffix length (default: {DEFAULT_ID_LENGTH})"
    )
    parser.add_argument(
        "--seed", type=int,
        default=DEFAULT_SEED,
        help=f"Random seed (default: {DEFAULT_SEED})"
    )
    parser.add_argument(
        "-r", "--rows", type=int,
        default=DEFAULT_SAMPLE_ROWS,
        help="Optionally sample N rows from the ISIN input (default: all rows)"
    )

    # Softening probabilities
    parser.add_argument(
        "--name-append-p", type=float,
        default=DEFAULT_NAME_APPEND_P,
        help=f"Prob. to append name token (default: {DEFAULT_NAME_APPEND_P})"
    )
    parser.add_argument(
        "--name-strip-p", type=float,
        default=DEFAULT_NAME_STRIP_P,
        help=f"Prob. to strip tokens ['class','series','fund'] (default: {DEFAULT_NAME_STRIP_P})"
    )
    parser.add_argument(
        "--name-shuffle-p", type=float,
        default=DEFAULT_NAME_SHUFFLE_P,
        help=f"Prob. to shuffle first 3 name tokens (default: {DEFAULT_NAME_SHUFFLE_P})"
    )
    parser.add_argument(
        "--desc-append-p", type=float,
        default=DEFAULT_DESC_APPEND_P,
        help=f"Prob. to append desc token (default: {DEFAULT_DESC_APPEND_P})"
    )
    parser.add_argument(
        "--desc-shuffle-p", type=float,
        default=DEFAULT_DESC_SHUFFLE_P,
        help=f"Prob. to shuffle first 4 desc tokens (default: {DEFAULT_DESC_SHUFFLE_P})"
    )

    return parser.parse_args()

def _csv_quoting_mode(mode_str: str) -> int:
    return {
        "minimal": csv.QUOTE_MINIMAL,
        "all": csv.QUOTE_ALL,
        "nonnumeric": csv.QUOTE_NONNUMERIC,
        "none": csv.QUOTE_NONE,
    }[mode_str]

def parse_prefix_overrides(pairs: List[str]) -> Dict[str, str]:
    mapping: Dict[str, str] = {}
    for p in pairs:
        if "=" not in p:
            raise ValueError(f"Invalid --prefix entry '{p}'. Use the form FAMILY=PREFIX (e.g., CUSIP=CUS).")
        fam, pref = p.split("=", 1)
        fam = fam.strip()
        pref = pref.strip()
        if not fam or not pref:
            raise ValueError(f"Invalid --prefix entry '{p}'. FAMILY and PREFIX must be non-empty.")
        mapping[fam] = pref
    return mapping

def main() -> None:
    args = parse_args()
    random.seed(args.seed)

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    quoting = _csv_quoting_mode(args.csv_quoting)
    ids_to_make = args.ids
    prefix_overrides = parse_prefix_overrides(args.prefix)

    # Read ISIN CSV
    isin_df = pd.read_csv(args.input)

    # Basic schema check
    required_cols = {'id', 'name', 'description', 'country', 'type'}
    missing = required_cols - set(isin_df.columns)
    if missing:
        raise ValueError(f"Input CSV missing columns: {', '.join(sorted(missing))}")

    # Optional sampling
    if args.rows is not None and args.rows < len(isin_df):
        isin_df = isin_df.sample(n=args.rows, random_state=args.seed).reset_index(drop=True)

    # Prepare ground truth collector
    ground_truth: List[Dict[str, str]] = []

    # Generate each requested family
    name_params = (args.name_append_p, args.name_strip_p, args.name_shuffle_p)
    desc_params = (args.desc_append_p, args.desc_shuffle_p)

    outputs = []
    for fam in ids_to_make:
        prefix = prefix_overrides.get(fam, fam)  # default prefix is the family name
        df = generate_soft_matching_table(
            prefix=prefix,
            ref_df=isin_df,
            ground_truth_pairs=ground_truth,
            column_label=fam,
            id_length=args.id_length,
            name_params=name_params,
            desc_params=desc_params
        )
        out_path = outdir / f"{fam}.csv"
        df.to_csv(out_path, index=False, quoting=quoting)
        outputs.append(str(out_path))

    # Build wide ground truth: one row per ISIN with columns for each family
    gt_df = pd.DataFrame(ground_truth)
    gt_df = gt_df.groupby('ISIN').first().reset_index()

    gt_path = outdir / "GROUND_TRUTH.csv"
    gt_df.to_csv(gt_path, index=False, quoting=quoting)
    outputs.append(str(gt_path))

    print("Files generated:")
    for p in outputs:
        print(" -", p)

if __name__ == "__main__":
    main()
