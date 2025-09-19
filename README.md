# SoftChase Benchmark Suite

This repository provides the benchmark suite for the paper:

**"Softening the Chase: Exploiting the Power of Large Language Models in Ontological Reasoning"**
*Teodoro Baldazzi, Luigi Bellomarini, Davide Benedetto, Matteo Brandetti, Emanuel Sallinger, Adriano Vlad*

---

## Overview

The **SoftChase Benchmark Suite** contains datasets, ontologies, glossaries, prompts, and evaluation scripts to test neurosymbolic reasoning based on the **Soft Chase** procedure.

It complements the Soft Chase framework which integrates **Datalog reasoning** with **LLM-based soft bindings** for robust, context-aware inference.

This benchmark suite enables **reproducible evaluation** of Soft Chase across real-world scenarios, measuring both logical correctness and semantic quality.

---

## Repository Structure

```bash
soft-chase-benchmark/
├── scenarios/
│   ├── AnmPay/                 # Scenario 1: Anti-Money Laundering (Finance)
│   ├── CaseLaw/                 # Scenario 2: Legal Compliance and Case Matching
│   ├── AgNews/                  # Scenario 3: News Topic Categorization (Text classification)
│   └── FI-Integ/                # Scenario 4: Financial Integration (Entity alignment)
│       ├── dataset/             # Raw facts and input data
│       ├── generation_script/   # Data generation or preprocessing scripts
│       ├── glossary/            # Domain-specific verbalizations
│       ├── ground_truth/        # Gold standard facts for evaluation
│       ├── ontology/            # Datalog± rules (TGDs, constraints)
│       └── prompt/              # LLM prompts and templates
│
├── utils/
│   ├── fscore_evaluator.py          # Precision, Recall, F1-score evaluation
│   ├── rouge_metrics_evaluator.py   # ROUGE-N and ROUGE-L textual similarity
│   └── verbalizer_from_glossary.py  # Natural language verbalization of facts
│
└── .gitignore.txt
```

---

## Scenarios

The benchmark suite includes four scenarios, each designed to highlight a different strength of the **Soft Chase** framework: handling noise, semantic approximation, domain reasoning, and flexible data integration.

* **AnmPay – Payment Categorization & Anomaly Detection**
  This scenario models anti–money laundering and anomaly detection in financial payments. Payment records often contain **misspelled names, abbreviations, or free-text reasons** provided by customers. The Soft Chase is used to **match payments with accounts despite noisy fields**, classify payments into categories such as business-to-business or customer-to-customer, and then detect **anomalous transactions** whose behavior deviates from the account’s usual patterns.

* **CaseLaw – Legal Precedent and Compliance Reasoning**
  Based on a large repository of U.S. court decisions, this scenario focuses on **linking new cases to relevant precedents**. The Soft Chase combines **textual similarity** (e.g., matching case names in head matters and opinions) with **logical propagation rules** (e.g., citation chains) to determine which past cases should be considered as precedents. This enables **context-aware compliance reasoning** in the legal domain, where vocabulary and references can vary significantly.

* **AgNews – Noisy Text Classification and Sentiment Analysis**
  This scenario evaluates reasoning over **news datasets that are incomplete, inconsistent, or noisily labeled**. The Soft Chase is applied to categorize news articles into topics such as Business, Sports, or Technology, and to perform tasks like **detecting stock-related news and sentiment analysis**. By tolerating missing values and approximate textual matches, the framework demonstrates robustness in real-world NLP contexts where data quality is often imperfect.

* **FI-Integ – Financial Entity Alignment**
  This scenario tests the ability of the Soft Chase to **integrate heterogeneous financial data sources**. Instruments such as stocks or bonds are registered under different identifiers (ISIN, CUSIP, FIGI, SEDOL), each with varying formats, naming conventions, and descriptions. The task is to **reconcile equivalent instruments across these registries** by relying on soft matches over textual attributes, enabling **flexible data integration** across domains where schema mismatches are common.

---

## Evaluation Metrics

Use the scripts under `utils/` to compute **semantic correctness** and **textual similarity**:

* **F-score Evaluation** (`fscore_evaluator.py`):

  * Computes Precision, Recall, and F1-score between inferred and ground-truth facts.
* **ROUGE Evaluation** (`rouge_metrics_evaluator.py`):

  * Measures textual similarity (ROUGE-N, ROUGE-L) for verbalized outputs.
* **Verbalizer** (`verbalizer_from_glossary.py`):

  * Converts structured facts into natural language using domain-specific glossaries.

---

## Usage

1. **Run the Soft Chase engine** with one of the scenario datasets.
2. **Compare results** against the ground truth:

```bash
python utils/fscore_evaluator.py --ground_truth scenarios/CaseLaw/ground_truth/gt.csv --predictions results/caselaw_output.csv
```

```bash
python utils/rouge_metrics_evaluator.py --reference scenarios/CaseLaw/glossary/verbalized_gt.txt --candidate results/caselaw_output.txt
```

3. Use `verbalizer_from_glossary.py` to generate human-readable fact descriptions.

---

## Citation

If you use this benchmark in your research, please cite:

```bibtex
@inproceedings{softchase2025,
  title={Softening the Chase: Exploiting the Power of Large Language Models in Ontological Reasoning},
  author={Baldazzi, Teodoro and Bellomarini, Luigi and Benedetto, Davide and Brandetti, Matteo and Sallinger, Emanuel and Vlad, Adriano},
  booktitle={Proceedings of ...},
  year={2025}
}
```

---

## License

This benchmark suite is released under the **Creative Commons Attribution-NonCommercial 4.0 International License (CC BY-NC 4.0)**.
You may share and adapt the material for non-commercial use with proper attribution.

---

## Contact and Contributions

Contributions are welcome! Please open issues or pull requests.
For questions, contact the authors of the accompanying paper.
