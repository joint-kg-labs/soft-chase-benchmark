import pandas as pd
import argparse
from sentence_transformers import SentenceTransformer, util
import torch

"""
Strict Soft Query Evaluator
===========================

This script evaluates soft conjunctive query answers by checking whether
each retrieved fact exactly matches a gold standard fact on all fields
with high semantic similarity (using Sentence-BERT embeddings).

Usage (from command line):
--------------------------
python strict_soft_query_evaluator.py \\
    --gold path/to/gold.csv \\
    --retrieved path/to/retrieved.csv \\
    --model mini \\
    --threshold 0.85

Arguments:
----------
--gold       : Path to the gold standard CSV file (reference answers).
--retrieved  : Path to the retrieved answer CSV file (soft CQ output).
--model      : Embedding model to use (choices: mini, mpnet, distil).
--threshold  : Cosine similarity threshold per field (e.g., 0.85).

Example:
--------
python strict_soft_query_evaluator.py \\
    --gold gold_answers.csv \\
    --retrieved predicted_answers.csv \\
    --model mpnet \\
    --threshold 0.9

Output:
-------
Pretty-printed precision, recall, and F1-score based on full-field matching.

"""



# Supported embedding models
EMBEDDING_MODELS = {
    "mini": "all-MiniLM-L6-v2",
    "mpnet": "all-mpnet-base-v2",
    "distil": "distilbert-base-nli-stsb-mean-tokens"
}

def load_model(name):
    if name not in EMBEDDING_MODELS:
        raise ValueError(f"Unknown model '{name}'. Choose from {list(EMBEDDING_MODELS.keys())}")
    print(f"Loading model: {EMBEDDING_MODELS[name]}")
    return SentenceTransformer(EMBEDDING_MODELS[name])

def fields_above_threshold(fact1_fields, fact2_fields, model, threshold):
    for f1, f2 in zip(fact1_fields, fact2_fields):
        emb1 = model.encode(str(f1), convert_to_tensor=True)
        emb2 = model.encode(str(f2), convert_to_tensor=True)
        sim = util.pytorch_cos_sim(emb1, emb2).item()
        if sim < threshold:
            return False
    return True

def compute_soft_fscore(gold_facts, retrieved_facts, model, threshold=0.8):
    correct_retrieved = 0
    matched_gold = set()

    for rf in retrieved_facts:
        for idx, gf in enumerate(gold_facts):
            if fields_above_threshold(rf, gf, model, threshold):
                correct_retrieved += 1
                matched_gold.add(idx)
                break  # Stop after first full-field match

    precision = correct_retrieved / len(retrieved_facts) if retrieved_facts else 0
    recall = len(matched_gold) / len(gold_facts) if gold_facts else 0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0

    return {
        "precision": precision,
        "recall": recall,
        "f1_score": f1,
        "correct_retrieved": correct_retrieved,
        "total_retrieved": len(retrieved_facts),
        "total_gold": len(gold_facts)
    }

def evaluate_soft_query_answering(gold_csv, retrieved_csv, model_name="mini", threshold=0.8):
    model = load_model(model_name)
    gold_df = pd.read_csv(gold_csv)
    retrieved_df = pd.read_csv(retrieved_csv)

    gold_facts = gold_df.values.tolist()
    retrieved_facts = retrieved_df.values.tolist()

    return compute_soft_fscore(gold_facts, retrieved_facts, model, threshold)

def pretty_print_result(results):
    print("\n==== Strict Fieldwise Evaluation Results ====")
    print(f"Total Gold Facts:       {results['total_gold']}")
    print(f"Total Retrieved Facts:  {results['total_retrieved']}")
    print(f"Correctly Retrieved:    {results['correct_retrieved']}")
    print("--------------------------------------------")
    print(f"Precision:              {results['precision']:.4f}")
    print(f"Recall:                 {results['recall']:.4f}")
    print(f"F1 Score:               {results['f1_score']:.4f}")
    print("================================================\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Strict Evaluation of Soft CQ Answering (All Fields Above Threshold)")
    parser.add_argument("--gold", type=str, required=True, help="Path to CSV file with gold standard facts")
    parser.add_argument("--retrieved", type=str, required=True, help="Path to CSV file with retrieved facts")
    parser.add_argument("--model", type=str, default="mini", choices=EMBEDDING_MODELS.keys(), help="Embedding model to use")
    parser.add_argument("--threshold", type=float, default=0.8, help="Similarity threshold for field match")

    args = parser.parse_args()
    results = evaluate_soft_query_answering(args.gold, args.retrieved, args.model, args.threshold)
    pretty_print_result(results)
