import argparse
import csv
from pathlib import Path
from typing import List, Tuple, Dict, Optional

import pandas as pd
import torch
from sentence_transformers import SentenceTransformer, util


EMBEDDING_MODELS = {
    "mini": "all-MiniLM-L6-v2",
    "mpnet": "all-mpnet-base-v2",
    "distil": "distilbert-base-nli-stsb-mean-tokens",
}


def load_model(name: str) -> SentenceTransformer:
    if name not in EMBEDDING_MODELS:
        raise ValueError(f"Unknown model '{name}'. Choose from {list(EMBEDDING_MODELS.keys())}")
    print(f"Loading model: {EMBEDDING_MODELS[name]}")
    return SentenceTransformer(EMBEDDING_MODELS[name])


def read_csv(path: str) -> pd.DataFrame:
    return pd.read_csv(
        path,
        engine="python",
        escapechar="\\",
        quoting=csv.QUOTE_MINIMAL,
        dtype=str,
        keep_default_na=False,
    )


def normalize_df(df: pd.DataFrame, ignore_case: bool, strip: bool) -> pd.DataFrame:
    out = df.copy()
    for c in out.columns:
        s = out[c].astype(str)
        if strip:
            s = s.str.strip()
        if ignore_case:
            s = s.str.lower()
        out[c] = s
    return out


def row_signature(row: List[str], sep: str = " | ") -> str:
    # Used only for candidate retrieval
    return sep.join(str(x) for x in row)


@torch.inference_mode()
def embed_texts(
    model: SentenceTransformer,
    texts: List[str],
    batch_size: int = 256,
    device: Optional[str] = None,
) -> torch.Tensor:
    return model.encode(
        texts,
        batch_size=batch_size,
        convert_to_tensor=True,
        show_progress_bar=True,
        device=device,
        normalize_embeddings=True,  # important: cosine sim becomes dot product
    )


def fields_above_threshold_emb(
    rf_embs: torch.Tensor,   # shape: (F, D)
    gf_embs: torch.Tensor,   # shape: (F, D)
    threshold: float,
) -> bool:
    # cosine sim per field = dot product because embeddings are normalized
    sims = (rf_embs * gf_embs).sum(dim=1)  # (F,)
    return bool(torch.all(sims >= threshold).item())


def compute_soft_fscore_optimized(
    gold_rows: List[List[str]],
    retrieved_rows: List[List[str]],
    model: SentenceTransformer,
    threshold: float = 0.8,
    topk: int = 50,
    batch_size: int = 256,
    candidate_field: str = "concat",   # "concat" or "first"
    device: Optional[str] = None,
) -> Dict:
    """
    topk:
      - 0 => exact all-pairs check (slow, but embeddings are still cached so much faster than original)
      - >0 => approximate: only compare each row to top-k candidates
    """
    if not gold_rows or not retrieved_rows:
        return {
            "precision": 0.0,
            "recall": 0.0,
            "f1_score": 0.0,
            "correct_retrieved": 0,
            "total_retrieved": len(retrieved_rows),
            "total_gold": len(gold_rows),
        }

    F = min(len(gold_rows[0]), len(retrieved_rows[0]))

    # Build per-field text lists (so we can embed fieldwise once)
    gold_cols = list(zip(*[r[:F] for r in gold_rows]))        # F lists of length G
    retr_cols = list(zip(*[r[:F] for r in retrieved_rows]))   # F lists of length R

    # Embed all fields (fieldwise embeddings, cached once)
    print("\nEmbedding GOLD fields...")
    gold_field_embs = []
    for f in range(F):
        gold_field_embs.append(embed_texts(model, list(gold_cols[f]), batch_size=batch_size, device=device))
    # gold_field_embs[f] shape: (G, D)

    print("\nEmbedding RETRIEVED fields...")
    retr_field_embs = []
    for f in range(F):
        retr_field_embs.append(embed_texts(model, list(retr_cols[f]), batch_size=batch_size, device=device))
    # retr_field_embs[f] shape: (R, D)

    # Candidate retrieval embeddings (one vector per row)
    if candidate_field == "first":
        gold_keys = [r[0] for r in gold_rows]
        retr_keys = [r[0] for r in retrieved_rows]
    else:
        gold_keys = [row_signature(r[:F]) for r in gold_rows]
        retr_keys = [row_signature(r[:F]) for r in retrieved_rows]

    print("\nEmbedding row keys for candidate retrieval...")
    gold_key_emb = embed_texts(model, gold_keys, batch_size=batch_size, device=device)
    retr_key_emb = embed_texts(model, retr_keys, batch_size=batch_size, device=device)

    # Precompute similarity matrix in chunks (avoid huge memory if large)
    G = len(gold_rows)
    R = len(retrieved_rows)

    def topk_gold_for_retrieved(ri: int) -> List[int]:
        if topk <= 0:
            return list(range(G))
        sims = util.cos_sim(retr_key_emb[ri:ri+1], gold_key_emb).squeeze(0)  # (G,)
        k = min(topk, G)
        vals, idx = torch.topk(sims, k=k, largest=True)
        return idx.tolist()

    # Precision: for each retrieved, find a matching gold (unique gold matching like your original via matched_gold)
    matched_gold = set()
    correct_retrieved = 0

    print("\nScoring (retrieved -> gold)...")
    for ri in range(R):
        candidates = topk_gold_for_retrieved(ri)
        found = False

        # Build rf field embedding matrix once: (F, D)
        rf_mat = torch.stack([retr_field_embs[f][ri] for f in range(F)], dim=0)

        for gi in candidates:
            if gi in matched_gold:
                continue

            gf_mat = torch.stack([gold_field_embs[f][gi] for f in range(F)], dim=0)
            if fields_above_threshold_emb(rf_mat, gf_mat, threshold):
                matched_gold.add(gi)
                correct_retrieved += 1
                found = True
                break

        # If no match, continue
        _ = found

    precision = correct_retrieved / R if R else 0.0
    recall = len(matched_gold) / G if G else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0

    return {
        "precision": precision,
        "recall": recall,
        "f1_score": f1,
        "correct_retrieved": correct_retrieved,
        "total_retrieved": R,
        "total_gold": G,
        "topk": topk,
        "threshold": threshold,
        "fields_used": F,
        "candidate_field": candidate_field,
    }


def pretty_print_result(results: Dict) -> None:
    print("\n==== Soft Fieldwise Evaluation Results (Optimized) ====")
    print(f"Total Gold Facts:       {results['total_gold']}")
    print(f"Total Retrieved Facts:  {results['total_retrieved']}")
    print(f"Correctly Retrieved:    {results['correct_retrieved']}")
    print("------------------------------------------------------")
    print(f"Precision:              {results['precision']:.4f}")
    print(f"Recall:                 {results['recall']:.4f}")
    print(f"F1 Score:               {results['f1_score']:.4f}")
    print("------------------------------------------------------")
    print(f"Threshold:              {results.get('threshold')}")
    print(f"Top-k candidates:       {results.get('topk')} (0 = exact all-pairs)")
    print(f"Fields compared:        {results.get('fields_used')}")
    print(f"Candidate key:          {results.get('candidate_field')} (first|concat)")
    print("======================================================\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Optimized Soft CQ Evaluation (all fields above threshold)")
    parser.add_argument("--gold", type=str, required=True, help="Path to CSV file with gold standard facts")
    parser.add_argument("--retrieved", type=str, required=True, help="Path to CSV file with retrieved facts")
    parser.add_argument("--model", type=str, default="mini", choices=EMBEDDING_MODELS.keys(), help="Embedding model to use")
    parser.add_argument("--threshold", type=float, default=0.8, help="Similarity threshold per field")

    # Speed/quality knobs
    parser.add_argument("--topk", type=int, default=50, help="Top-k candidate gold rows per retrieved (0 = exact all-pairs)")
    parser.add_argument("--batch-size", type=int, default=256, help="Embedding batch size")
    parser.add_argument("--candidate-field", choices=["concat", "first"], default="concat",
                        help="How to build candidate retrieval key: concat all fields or only first field")
    parser.add_argument("--ignore-case", action="store_true", help="Lowercase fields before comparing")
    parser.add_argument("--strip", action="store_true", help="Strip whitespace around fields before comparing")
    parser.add_argument("--device", type=str, default=None, help="Force device (e.g. 'cpu' or 'cuda')")

    args = parser.parse_args()

    model = load_model(args.model)

    gold_df = read_csv(args.gold)
    ret_df = read_csv(args.retrieved)

    gold_df = normalize_df(gold_df, ignore_case=args.ignore_case, strip=args.strip)
    ret_df = normalize_df(ret_df, ignore_case=args.ignore_case, strip=args.strip)

    if gold_df.shape[1] != ret_df.shape[1]:
        print(
            f"WARNING: column count mismatch: gold has {gold_df.shape[1]} cols, "
            f"retrieved has {ret_df.shape[1]} cols. Extra columns are ignored (fieldwise compare uses min columns)."
        )

    gold_rows = gold_df.values.tolist()
    ret_rows = ret_df.values.tolist()

    results = compute_soft_fscore_optimized(
        gold_rows=gold_rows,
        retrieved_rows=ret_rows,
        model=model,
        threshold=args.threshold,
        topk=args.topk,
        batch_size=args.batch_size,
        candidate_field=args.candidate_field,
        device=args.device,
    )
    pretty_print_result(results)
