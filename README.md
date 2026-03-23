# SoftChase Benchmark Suite

Benchmark datasets, ontologies, glossaries, prompts, and evaluation utilities for the paper:

**Softening the Chase: Exploiting the Power of Large Language Models in Datalog-based Reasoning**  
*Teodoro Baldazzi, Luigi Bellomarini, Davide Benedetto, Matteo Brandetti, Emanuel Sallinger, Adriano Vlad*

---

## Overview

The **SoftChase Benchmark Suite** is the companion repository for the **Soft Chase** framework, a neurosymbolic approach that combines:

- **Datalog-based reasoning**
- **LLM-based soft bindings**
- **context-aware inference over noisy, heterogeneous, and partially structured data**

This repository collects the material needed to evaluate Soft Chase across multiple application domains, including:

- datasets
- ontologies
- domain glossaries
- prompt templates
- ground-truth outputs
- evaluation scripts

The goal of the benchmark is to support **systematic and reproducible evaluation** of Soft Chase along two main dimensions:

- **reasoning quality**, such as Precision, Recall, and F1
- **semantic/textual quality**, such as ROUGE-based similarity on verbalized outputs

It expoits the **RAG Module** implemented in this [https://github.com/joint-kg-labs/soft-chase] repository.
The istructions to use it are located in the README.md file.

---

## Repository Structure

```text
soft-chase-benchmark/
├── scenarios/
│   ├── AnmPay/                  # Payment categorization and anomaly detection
│   │   ├── dataset/             # Raw facts and input data
│   │   ├── generation_script/   # Data generation or preprocessing scripts
│   │   ├── glossary/            # Domain-specific verbalizations and context
│   │   ├── ground_truth/        # Gold-standard facts for evaluation
│   │   ├── ontology/            # Datalog± rules and constraints
│   │   └── prompt/              # LLM prompts and templates
│   │
│   ├── CaseLaw/                 # Legal precedent and compliance reasoning
│   │   ├── dataset/
│   │   ├── generation_script/
│   │   ├── glossary/
│   │   ├── ground_truth/
│   │   ├── ontology/
│   │   └── prompt/
│   │
│   ├── AgNews/                  # Noisy text classification and sentiment analysis
│   │   ├── dataset/
│   │   ├── generation_script/
│   │   ├── glossary/
│   │   ├── ground_truth/
│   │   ├── ontology/
│   │   └── prompt/
│   │
│   ├── FI-Integ/                # Financial entity alignment and integration
│   │   ├── dataset/
│   │   ├── generation_script/
│   │   ├── glossary/
│   │   ├── ground_truth/
│   │   ├── ontology/
│   │   └── prompt/
│   │
│   └── SymbolicChaseScenarios/  # Pure symbolic chase benchmarks and support material
│       ├── graphs/              # Graph datasets for symbolic chase experiments
│       ├── ontology/            # Symbolic ontologies (e.g., TC, SG)
│       └── miscellaneous/       # Auxiliary files, notes, and experiment resources
│
├── utils/
│   ├── fscore_evaluator.py          # Precision / Recall / F1 evaluation
│   ├── rouge_metrics_evaluator.py   # ROUGE-N / ROUGE-L evaluation
│   └── verbalizer_from_glossary.py  # Fact verbalization using scenario glossaries
│
└── .gitignore
````

---

## Benchmark Scenarios

The suite includes four scenarios, each designed to stress a different capability of the Soft Chase framework.

### 1. AnmPay — Payment Categorization and Anomaly Detection

This scenario focuses on financial payments, where records often contain:

* misspelled names
* abbreviations
* free-text payment reasons
* incomplete or noisy fields

Soft Chase is used to:

* associate payments with accounts despite noisy textual fields
* classify transactions into categories such as **B2B**, **C2B**, or **C2C**
* detect anomalous payments whose category deviates from the usual behavior of the originator account

This scenario highlights **reasoning under semantic approximation**.

### 2. CaseLaw — Legal Precedent and Compliance Reasoning

This scenario is based on **CaseLaw** ([https://case.law/](https://case.law/)), a large corpus of U.S. court decisions, and targets **precedent discovery** and **compliance-oriented reasoning**.

Soft Chase combines:

* approximate matching over legal text
* citation and propagation rules
* recursive reasoning over precedent chains

The task is to identify which past cases should be considered relevant precedents for new cases, even when legal references are phrased differently or expressed indirectly.

This scenario highlights **domain-specific reasoning** and **recursive inference over semantically rich text**.

### 3. AgNews — Noisy Text Classification and Sentiment Analysis

This scenario is based on the **AG News Classification Dataset** ([Kaggle](https://www.kaggle.com/datasets/amananandrai/ag-news-classification-dataset)) and evaluates reasoning over news data that may be:

- incomplete
- inconsistently labeled
- semantically noisy

Soft Chase is applied to:

- categorize articles into topics
- identify stock-related content
- support sentiment-oriented downstream reasoning

This scenario highlights **robustness to noisy and weakly structured textual data**.

### 4. FI-Integ — Financial Entity Alignment

This scenario studies the integration of heterogeneous financial registries, where the same instrument may appear under different identifier systems such as:

* **ISIN**
* **CUSIP**
* **FIGI**
* **SEDOL**

The task is to reconcile equivalent entities across sources despite differences in:

* naming conventions
* descriptions
* schema structure
* identifier systems

This scenario highlights **flexible data integration through soft semantic matching**.

---

## Included Resources

Each scenario may contain the following components:

* **dataset/**: input facts or raw source data
* **generation_script/**: preprocessing or synthetic data generation scripts
* **glossary/**: domain context, predicate verbalizations, and rule verbalizations
* **ground_truth/**: gold-standard facts used for evaluation
* **ontology/**: Datalog± rules, constraints, and scenario logic
* **prompt/**: prompt templates used for LLM-assisted soft binding

---

## Evaluation Utilities

The `utils/` directory contains scripts to evaluate both structured and verbalized outputs.

### `fscore_evaluator.py`

Computes:

* **Precision**
* **Recall**
* **F1-score**

between predicted facts and gold-standard facts.

### `rouge_metrics_evaluator.py`

Computes:

* **ROUGE-N**
* **ROUGE-L**

to measure the similarity between generated verbalizations and reference verbalizations.

### `verbalizer_from_glossary.py`

Transforms structured facts into natural-language descriptions using the glossary of a scenario.

---

## Basic Usage

### 1. Run the Soft Chase engine

Execute your Soft Chase implementation on one of the scenario datasets and store the inferred facts in an output file.

### 2. Evaluate fact-level correctness

Example:

```bash
python utils/fscore_evaluator.py \
  --ground_truth scenarios/CaseLaw/ground_truth/gt.csv \
  --predictions results/caselaw_output.csv
```

### 3. Evaluate verbalized outputs

Example:

```bash
python utils/rouge_metrics_evaluator.py \
  --reference scenarios/CaseLaw/glossary/verbalized_gt.txt \
  --candidate results/caselaw_output.txt
```

### 4. Generate verbalized facts

Use the glossary-based verbalizer to convert structured outputs into human-readable text before running text-level evaluation.

---

## What This Benchmark Measures

The benchmark is intended to support evaluation of Soft Chase along two complementary axes.

### Fact-level reasoning quality

Measures whether the system derives the correct structured facts.

Typical metrics:

* Precision
* Recall
* F1-score

### Text-level semantic quality

Measures whether the verbalized outputs align with reference descriptions.

Typical metrics:

* ROUGE-N
* ROUGE-L

Together, these metrics help assess both:

* the **correctness of the reasoning process**
* the **quality of the natural-language rendering of inferred facts**

---

## Citation

If you use this benchmark suite in your research, please cite the associated paper.

```bibtex
@inproceedings{softchase2025,
  title     = {Softening the Chase: Exploiting the Power of Large Language Models in Datalog-based Reasoning},
  author    = {Baldazzi, Teodoro and Bellomarini, Luigi and Benedetto, Davide and Brandetti, Matteo and Sallinger, Emanuel and Vlad, Adriano},
  booktitle = {Proceedings of ...},
  year      = {2025}
}
```

If the final venue metadata is available, please replace the placeholder entry above with the camera-ready citation.

---

## License

This benchmark suite is released under the **Creative Commons Attribution-NonCommercial 4.0 International License (CC BY-NC 4.0)**.

You may share and adapt the material for **non-commercial use**, provided that proper attribution is given.

---