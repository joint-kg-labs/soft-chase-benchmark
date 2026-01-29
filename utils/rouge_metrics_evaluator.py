import argparse
from typing import Dict, List, Tuple

import pandas as pd
from rouge_score import rouge_scorer

# Optional but recommended for speed
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel


def load_text_facts(file_path: str) -> List[str]:
    df = pd.read_csv(file_path, header=None)
    return df[0].astype(str).tolist()


def build_topk_candidates(
    gold: List[str],
    retrieved: List[str],
    topk: int,
    min_sim: float = 0.0,
    ngram_range: Tuple[int, int] = (1, 2),
    max_features: int = 200_000,
) -> Tuple[Dict[int, List[int]], Dict[int, List[int]]]:
    """
    Returns:
      - cand_gold_for_retrieved: map r_idx -> list of gold indices to compare against
      - cand_retrieved_for_gold: map g_idx -> list of retrieved indices to compare against

    If topk <= 0, uses all pairs (exact, but slow).
    """
    G, R = len(gold), len(retrieved)
    if topk <= 0:
        all_gold = list(range(G))
        all_retr = list(range(R))
        return (
            {ri: all_gold for ri in range(R)},
            {gi: all_retr for gi in range(G)},
        )

    # TF-IDF fit on combined corpus for consistent vocabulary
    corpus = gold + retrieved
    vectorizer = TfidfVectorizer(
        lowercase=True,
        ngram_range=ngram_range,
        max_features=max_features,
        dtype=float,
    )
    X = vectorizer.fit_transform(corpus)
    X_gold = X[:G]
    X_retr = X[G:]

    # Cosine similarity for TF-IDF vectors is dot product because vectors are L2-normalized
    # We'll compute:
    #  - for each retrieved: top-k gold
    #  - for each gold: top-k retrieved
    cand_gold_for_retrieved: Dict[int, List[int]] = {}
    cand_retrieved_for_gold: Dict[int, List[int]] = {}

    # retrieved -> gold
    sim_rg = linear_kernel(X_retr, X_gold)  # shape (R, G)
    for ri in range(R):
        row = sim_rg[ri]
        # get topk indices without full sort
        k = min(topk, G)
        top_idx = row.argsort()[-k:][::-1]
        if min_sim > 0.0:
            top_idx = [gi for gi in top_idx if row[gi] >= min_sim]
        cand_gold_for_retrieved[ri] = list(top_idx)

    # gold -> retrieved
    sim_gr = sim_rg.T  # shape (G, R)
    for gi in range(G):
        row = sim_gr[gi]
        k = min(topk, R)
        top_idx = row.argsort()[-k:][::-1]
        if min_sim > 0.0:
            top_idx = [ri for ri in top_idx if row[ri] >= min_sim]
        cand_retrieved_for_gold[gi] = list(top_idx)

    return cand_gold_for_retrieved, cand_retrieved_for_gold


def compute_rouge_bestmatch_with_candidates(
    gold: List[str],
    retrieved: List[str],
    cand_gold_for_retrieved: Dict[int, List[int]],
    cand_retrieved_for_gold: Dict[int, List[int]],
) -> Tuple[float, float, float, float]:
    """
    Computes:
      - ROUGE-1 Precision (best match per retrieved, averaged)
      - ROUGE-1 Recall    (best match per gold, averaged)
      - ROUGE-L Precision (best match per retrieved, averaged)
      - ROUGE-L Recall    (best match per gold, averaged)

    Uses a single RougeScorer call per evaluated pair, requesting both rouge1 and rougeL.
    """
    scorer = rouge_scorer.RougeScorer(["rouge1", "rougeL"], use_stemmer=True)

    best_p_r1 = [0.0] * len(retrieved)
    best_p_rl = [0.0] * len(retrieved)
    best_r_r1 = [0.0] * len(gold)
    best_r_rl = [0.0] * len(gold)

    # Precision side: for each retrieved, compare only candidate golds
    for ri, rf in enumerate(retrieved):
        best_p1 = 0.0
        best_pL = 0.0
        for gi in cand_gold_for_retrieved.get(ri, []):
            gf = gold[gi]
            scores = scorer.score(gf, rf)
            r1 = scores["rouge1"]
            rl = scores["rougeL"]
            if r1.precision > best_p1:
                best_p1 = r1.precision
            if rl.precision > best_pL:
                best_pL = rl.precision
        best_p_r1[ri] = best_p1
        best_p_rl[ri] = best_pL

    # Recall side: for each gold, compare only candidate retrieveds
    for gi, gf in enumerate(gold):
        best_r1 = 0.0
        best_rL = 0.0
        for ri in cand_retrieved_for_gold.get(gi, []):
            rf = retrieved[ri]
            scores = scorer.score(gf, rf)
            r1 = scores["rouge1"]
            rl = scores["rougeL"]
            if r1.recall > best_r1:
                best_r1 = r1.recall
            if rl.recall > best_rL:
                best_rL = rl.recall
        best_r_r1[gi] = best_r1
        best_r_rl[gi] = best_rL

    r1_p = sum(best_p_r1) / len(best_p_r1) if best_p_r1 else 0.0
    r1_r = sum(best_r_r1) / len(best_r_r1) if best_r_r1 else 0.0
    rl_p = sum(best_p_rl) / len(best_p_rl) if best_p_rl else 0.0
    rl_r = sum(best_r_rl) / len(best_r_rl) if best_r_rl else 0.0
    return r1_p, r1_r, rl_p, rl_r


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate ROUGE-1 and ROUGE-L with top-k candidate filtering")
    parser.add_argument("--gold", type=str, required=True, help="CSV with gold standard verbalized facts (one per line)")
    parser.add_argument("--retrieved", type=str, required=True, help="CSV with retrieved verbalized facts (one per line)")

    # Speed/quality knobs
    parser.add_argument(
        "--topk",
        type=int,
        default=20,
        help="Compare each item only to top-k candidates by TF-IDF similarity. Use 0 for exact all-pairs (slow). Default: 20",
    )
    parser.add_argument(
        "--min-sim",
        type=float,
        default=0.0,
        help="Optional minimum TF-IDF cosine similarity threshold to keep a candidate (0 disables).",
    )
    parser.add_argument(
        "--tfidf-max-features",
        type=int,
        default=200_000,
        help="Max TF-IDF vocabulary size. Lower = faster/less memory. Default: 200000",
    )

    args = parser.parse_args()

    gold = load_text_facts(args.gold)
    retrieved = load_text_facts(args.retrieved)

    cand_gold_for_retrieved, cand_retrieved_for_gold = build_topk_candidates(
        gold=gold,
        retrieved=retrieved,
        topk=args.topk,
        min_sim=args.min_sim,
        ngram_range=(1, 2),
        max_features=args.tfidf_max_features,
    )

    r1_p, r1_r, rl_p, rl_r = compute_rouge_bestmatch_with_candidates(
        gold=gold,
        retrieved=retrieved,
        cand_gold_for_retrieved=cand_gold_for_retrieved,
        cand_retrieved_for_gold=cand_retrieved_for_gold,
    )

    print("\n==== ROUGE Evaluation (top-k candidate filtering) ====")
    print(f"Top-k: {args.topk} (0 = exact all-pairs)")
    print(f"ROUGE-1 Precision: {r1_p:.4f}")
    print(f"ROUGE-1 Recall:    {r1_r:.4f}")
    print(f"ROUGE-L Precision: {rl_p:.4f}")
    print(f"ROUGE-L Recall:    {rl_r:.4f}")
