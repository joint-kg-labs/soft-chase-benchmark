import pandas as pd
import json
import argparse

"""
python ../../utils/verbalizer_from_glossary.py --input ground_truth/golden_set_fscore.csv --glossary glossary/short_glossary.json --predicate Link --output ground_truth/golden_set_rouge_short.csv

"""

def load_glossary(path):
    with open(path, "r") as f:
        return json.load(f)

def fill_template(template, values):
    """
    Replace arg0, arg1, ..., argN with corresponding values from a list.
    """
    result = template
    for i, val in enumerate(values):
        result = result.replace(f"arg{i}", str(val))
    return result

def verbalize(input_csv, glossary_path, predicate_key, output_path):
    df = pd.read_csv(input_csv)
    glossary = load_glossary(glossary_path)

    try:
        template = glossary["predicate_verbalization"][predicate_key]
    except KeyError:
        raise ValueError(f"Predicate '{predicate_key}' not found in glossary.")

    verbalized = [fill_template(template, row.tolist()) for _, row in df.iterrows()]
    output_df = pd.DataFrame(verbalized, columns=["Verbalized"])
    output_df.to_csv(output_path, index=False)
    print(f"✅ Verbalized rows written to: {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Verbalize CSV rows using a glossary and predicate template.")
    parser.add_argument("--input", required=True, help="Path to input CSV file with arg columns")
    parser.add_argument("--glossary", required=True, help="Path to a glossary JSON file")
    parser.add_argument("--predicate", required=True, help="Predicate name to use from glossary")
    parser.add_argument("--output", required=True, help="Output CSV file to write verbalized rows")

    args = parser.parse_args()

    verbalize(args.input, args.glossary, args.predicate, args.output)
