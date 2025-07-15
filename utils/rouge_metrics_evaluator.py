import pandas as pd
from rouge_score import rouge_scorer
import argparse

"""
Example usage:

Assuming you have two CSV files:
- `gold.csv` containing the gold standard verbalized facts (one per line)
- `retrieved.csv` containing the retrieved verbalized facts (one per line)

Run the script as:

    python evaluate_rouge_metrics.py --gold gold.csv --retrieved retrieved.csv

This will compute and print:

    - ROUGE-N Precision
    - ROUGE-N Recall
    - ROUGE-L Precision
    - ROUGE-L Recall

Each metric is calculated by comparing every retrieved fact against all gold facts using the highest matching score (as described in the soft CQ answering evaluation specification).
"""


def load_text_facts(file_path):
    df = pd.read_csv(file_path, header=None)
    return df[0].astype(str).tolist()

def compute_match_n_precision_recall(gold_facts, retrieved_facts, n=1):
    scorer = rouge_scorer.RougeScorer([f'rouge{n}'], use_stemmer=True)
    total_match_n_retrieved = 0
    total_ngrams_retrieved = 0

    for rf in retrieved_facts:
        best_match = 0
        best_total = 0
        for gf in gold_facts:
            scores = scorer.score(gf, rf)[f'rouge{n}']
            match = scores.precision * scores.predicted_count
            if match > best_match:
                best_match = match
                best_total = scores.predicted_count
        total_match_n_retrieved += best_match
        total_ngrams_retrieved += best_total

    total_match_n_gold = 0
    total_ngrams_gold = 0

    for gf in gold_facts:
        best_match = 0
        best_total = 0
        for rf in retrieved_facts:
            scores = scorer.score(gf, rf)[f'rouge{n}']
            match = scores.recall * scores.reference_count
            if match > best_match:
                best_match = match
                best_total = scores.reference_count
        total_match_n_gold += best_match
        total_ngrams_gold += best_total

    precision = total_match_n_retrieved / total_ngrams_retrieved if total_ngrams_retrieved else 0
    recall = total_match_n_gold / total_ngrams_gold if total_ngrams_gold else 0
    return precision, recall

def compute_lcs_precision_recall(gold_facts, retrieved_facts):
    scorer = rouge_scorer.RougeScorer(['rougeL'], use_stemmer=True)
    lcs_match_retrieved = 0
    lcs_total_retrieved = 0
    for rf in retrieved_facts:
        best_lcs = 0
        length_rf = len(rf.split())
        for gf in gold_facts:
            score = scorer.score(gf, rf)['rougeL']
            lcs = score.precision * length_rf
            best_lcs = max(best_lcs, lcs)
        lcs_match_retrieved += best_lcs
        lcs_total_retrieved += length_rf

    lcs_match_gold = 0
    lcs_total_gold = 0
    for gf in gold_facts:
        best_lcs = 0
        length_gf = len(gf.split())
        for rf in retrieved_facts:
            score = scorer.score(gf, rf)['rougeL']
            lcs = score.recall * length_gf
            best_lcs = max(best_lcs, lcs)
        lcs_match_gold += best_lcs
        lcs_total_gold += length_gf

    precision = lcs_match_retrieved / lcs_total_retrieved if lcs_total_retrieved else 0
    recall = lcs_match_gold / lcs_total_gold if lcs_total_gold else 0
    return precision, recall

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate ROUGE-N and ROUGE-L for soft CQ answers")
    parser.add_argument("--gold", type=str, required=True, help="CSV with gold standard verbalized facts")
    parser.add_argument("--retrieved", type=str, required=True, help="CSV with retrieved verbalized facts")
    args = parser.parse_args()

    gold = load_text_facts(args.gold)
    retrieved = load_text_facts(args.retrieved)

    r1_p, r1_r = compute_match_n_precision_recall(gold, retrieved, n=1)
    rl_p, rl_r = compute_lcs_precision_recall(gold, retrieved)

    print("\n==== ROUGE Evaluation ====")
    print(f"ROUGE-1 Precision: {r1_p:.4f}")
    print(f"ROUGE-1 Recall:    {r1_r:.4f}")
    print(f"ROUGE-L Precision: {rl_p:.4f}")
    print(f"ROUGE-L Recall:    {rl_r:.4f}")
