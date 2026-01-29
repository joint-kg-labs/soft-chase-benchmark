#!/usr/bin/env python3
import pandas as pd
import argparse
from pathlib import Path
from collections import Counter

DEFAULT_GOLD = "../scenarios/AgNews/chase/short/dump.csv"
DEFAULT_RETRIEVED = "../scenarios/AgNews/ground_truth/500/golden_set_dump_fscore.csv"


def load_df(csv_path: str) -> pd.DataFrame:
    p = Path(csv_path)
    if not p.exists():
        raise FileNotFoundError(f"CSV not found: {csv_path}")

    try:
        # Robust to quotes + embedded newlines + delimiter differences
        return pd.read_csv(
            p,
            engine="python",
            sep=None,               # auto-detect delimiter
            quotechar='"',
            doublequote=True,
            escapechar="\\",
            dtype=str,
            keep_default_na=False,
            na_values=[],
            on_bad_lines="warn",
        )
    except TypeError:
        # Older pandas fallback
        return pd.read_csv(
            p,
            engine="python",
            sep=None,
            quotechar='"',
            doublequote=True,
            escapechar="\\",
            dtype=str,
            keep_default_na=False,
            na_values=[],
            error_bad_lines=False,  # type: ignore
            warn_bad_lines=True,    # type: ignore
        )


def normalize_series(s: pd.Series, ignore_case: bool, strip: bool) -> pd.Series:
    s = s.fillna("").astype(str)
    if strip:
        s = s.str.strip()
    if ignore_case:
        s = s.str.lower()
    return s


def get_id_series(df: pd.DataFrame, id_col: str | None) -> pd.Series:
    """
    Prefer explicit id_col if present; otherwise use the first column.
    """
    if id_col and id_col in df.columns:
        return df[id_col]
    # fallback: first column
    if df.shape[1] < 1:
        raise ValueError("CSV has no columns.")
    return df.iloc[:, 0]


def compute_fscore_from_ids(gold_ids: list[str], retrieved_ids: list[str]) -> dict:
    gold_counts = Counter(gold_ids)

    correct = 0
    for rid in retrieved_ids:
        if gold_counts.get(rid, 0) > 0:
            correct += 1
            gold_counts[rid] -= 1

    total_retrieved = len(retrieved_ids)
    total_gold = len(gold_ids)

    precision = correct / total_retrieved if total_retrieved else 0.0
    recall = correct / total_gold if total_gold else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0

    return {
        "precision": precision,
        "recall": recall,
        "f1_score": f1,
        "correct_retrieved": correct,
        "total_retrieved": total_retrieved,
        "total_gold": total_gold,
    }


def pretty_print_result(results: dict) -> None:
    print("\n==== ID-based Strict Equality Evaluation Results ====")
    print(f"Total Gold IDs:        {results['total_gold']}")
    print(f"Total Retrieved IDs:   {results['total_retrieved']}")
    print(f"Correctly Retrieved:   {results['correct_retrieved']}")
    print("-----------------------------------------------------")
    print(f"Precision:             {results['precision']:.4f}")
    print(f"Recall:                {results['recall']:.4f}")
    print(f"F1 Score:              {results['f1_score']:.4f}")
    print("=====================================================\n")


def main():
    parser = argparse.ArgumentParser(description="F-score evaluator using ONLY the first column (ID) from both CSVs")
    parser.add_argument("--gold", type=str, default=DEFAULT_GOLD, help=f"Gold CSV path (default: {DEFAULT_GOLD})")
    parser.add_argument("--retrieved", type=str, default=DEFAULT_RETRIEVED, help=f"Retrieved CSV path (default: {DEFAULT_RETRIEVED})")
    parser.add_argument("--id-col", type=str, default=None,
                        help="Optional ID column name. If not present, first column is used.")
    parser.add_argument("--ignore-case", action="store_true", help="Lowercase IDs before comparing")
    parser.add_argument("--strip", action="store_true", help="Strip whitespace around IDs before comparing")

    args = parser.parse_args()

    gold_df = load_df(args.gold)
    ret_df = load_df(args.retrieved)

    gold_ids = normalize_series(get_id_series(gold_df, args.id_col), args.ignore_case, args.strip).tolist()
    ret_ids = normalize_series(get_id_series(ret_df, args.id_col), args.ignore_case, args.strip).tolist()

    results = compute_fscore_from_ids(gold_ids, ret_ids)
    pretty_print_result(results)


if __name__ == "__main__":
    main()
