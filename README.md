# SoftChase Benchmark Suite

This repository contains the benchmark suite for the paper:

**"Softening the Chase: Exploiting the Power of Large Language Models in Ontological Reasoning"**

Authors: Teodoro Baldazzi, Luigi Bellomarini, Davide Benedetto, Matteo Brandetti, Emanuel Sallinger, Adriano Vlad

---

## Overview

The SoftChase benchmark suite provides data, ontologies, glossaries, and evaluation tools for testing neurosymbolic reasoning based on the Soft Chase procedure. It includes four real-world industrial scenarios along with prompts, ground truths, and metric evaluation scripts to support reproducibility and benchmarking.

---

## Repository Structure

```

soft-chase-benchmark/
├── scenarios/
│   ├── AnmPay/                # Scenario 1: Anti-Money Laundering (Finance)
│   ├── CaseLaw/              # Scenario 2: Legal Compliance and Case Matching
│   ├── ComCrawl/             # Scenario 3: Web Knowledge Integration
│   └── FI-Integ/             # Scenario 4: Financial Integration (Multi-source alignment)
│       ├── dataset/          # Raw facts and example data
│       ├── generation\_script/ # Scripted data generation or transformation
│       ├── glossary/         # Domain-specific verbalizations
│       ├── ground\_truth/     # Gold standard facts for evaluation
│       ├── ontology/         # Datalog± rules (e.g., TGDs)
│       └── prompt/           # LLM prompts and input templates
│
├── utils/
│   ├── fscore\_evaluator.py           # Computes Precision, Recall, F1-score
│   ├── rouge\_metrics\_evaluator.py   # Computes ROUGE-N and ROUGE-L scores
│   └── verbalizer\_from\_glossary.py  # Converts structured facts into natural language using glossary
│
└── .gitignore.txt

````

---

## Scenarios

Each folder under `scenarios/` contains:

* Input data (`dataset/`)
* Soft Chase rules (`ontology/`)
* LLM prompts (`prompt/`)
* Verbalization glossaries (`glossary/`)
* Ground truth sets (`ground_truth/`)
* Optional data generation or conversion tools (`generation_script/`)

These represent distinct application domains including:

* **AnmPay**: Financial payment categorization and anti-money laundering
* **CaseLaw**: Legal document linking and compliance
* **ComCrawl**: Open-domain knowledge fusion
* **FI-Integ**: Financial entity alignment across heterogeneous systems

---

## Evaluation

Use the tools under `utils/` to evaluate:

* Semantic correctness of query answering
* Textual similarity of verbalized outputs
* Standard metrics such as:

  * Precision, Recall, F1
  * ROUGE-N (unigram, bigram)
  * ROUGE-L (Longest Common Subsequence)

Ground truth is compared against inferred facts using a similarity function with configurable thresholds.

---

## Citation

If you use this benchmark in your research, please cite:

```
@inproceedings{}
```

---

## License


---

## Contact and Contributions


---


