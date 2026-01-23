#!/usr/bin/env python3
"""
Generate a synthetic instruments table with configurable parameters.

Examples:
  python generate_instruments.py --rows 5000 --output ISIN.csv
  ./generate_instruments.py -r 20000 -o data/ISIN.csv --prefix ISIN --id-length 12
  python generate_instruments.py --rows 15000 --shared-frac 0.25 --seed 42
"""

import argparse
import random
import pandas as pd
import faker
from typing import List, Tuple

# ----------------------------
# Defaults (overridable via CLI)
# ----------------------------
DEFAULT_ROWS = 100
DEFAULT_OUTPUT = "../dataset/100/ISIN.csv"
DEFAULT_PREFIX = "ISIN"
DEFAULT_ID_LENGTH = 12
DEFAULT_SHARED_FRAC = 0.30  # up to 30% overlap by default
DEFAULT_SEED = 42

# Initialize Faker (locale can be customized later if desired)
fake = faker.Faker()

# Static vocabularies
countries = ['US', 'GB', 'JP', 'DE', 'FR', 'CN', 'CA', 'AU', 'CH', 'IT']
types = ['stock', 'bond', 'etf', 'derivative', 'mutual_fund']
company_names = list({fake.company() for _ in range(200)})

instrument_keywords = [
    # Existing keywords (kept)
    'Growth', 'Income', 'Balanced', 'Technology', 'Global', 'Emerging Markets',
    'Short-Term', 'Long-Term', 'High-Yield', 'Blue Chip', 'Value', 'Dividend',
    'Sustainable', 'Green', 'Infrastructure', 'Healthcare', 'Consumer Goods',
    'Energy', 'Financials', 'Real Estate', 'Private Equity', 'Hedge Fund',
    'Strategic', 'International', 'Ethical', 'Diversified', 'Dynamic',
    # New additions
    'Alternative', 'Thematic', 'Quantitative', 'Volatility', 'Commodities',
    'Multi-Asset', 'Tactical', 'Active', 'Passive', 'Alpha', 'Beta',
    'Defensive', 'Opportunistic', 'Unconstrained', 'Risk-Managed',
    'Inflation-Protected', 'ESG', 'Shariah-Compliant', 'Frontier Markets',
    'Fixed Income', 'Currency', 'Infrastructure Equity', 'Digital Assets'
]

instrument_types = [
    # Existing types (kept)
    'Equity Fund', 'Bond Fund', 'ETF', 'Index Fund', 'Trust', 'Preferred Shares',
    'Corporate Bond', 'Government Bond', 'Convertible Bond', 'REIT', 'Money Market',
    # New additions
    'Credit Fund', 'Commodities Fund', 'Private Debt Fund', 'Infrastructure Fund',
    'Multi-Strategy Fund', 'Absolute Return Fund', 'Fund of Funds', 'Currency Fund',
    'Leveraged ETF', 'Inverse ETF', 'Target Date Fund', 'ESG Fund', 'Islamic Fund',
    'Stable Value Fund', 'Opportunity Fund', 'Distressed Debt Fund', 'Microcap Fund',
    'Small Cap Fund', 'Mid Cap Fund', 'Large Cap Fund', 'Dividend Income Fund',
    'TIPS Fund', 'Global Macro Fund', 'Long/Short Equity Fund', 'Real Asset Fund'
]

def init_seeds(seed: int) -> None:
    random.seed(seed)
    faker.Faker.seed(seed)

# Function to generate richer descriptions
def generate_invented_description() -> str:
    adjectives = random.sample(instrument_keywords, 2)
    instrument = random.choice(instrument_types)
    if random.random() < 0.3:
        suffix = f"Class {random.choice(['A', 'B', 'C'])}"
        return f"{adjectives[0]} {adjectives[1]} {instrument} {suffix}"
    return f"{adjectives[0]} {adjectives[1]} {instrument}"

# Function to generate realistic security names
def generate_security_name() -> str:
    issuer = random.choice(company_names)
    instrument = random.choice([
        'Common Stock', 'Preferred Stock', 'Corporate Bond',
        'Convertible Bond', 'Government Bond', 'ETF',
        'Index Fund', 'Mutual Fund', 'Real Estate Trust', 'Money Market Fund'
    ])
    modifiers = ['', 'Class A', 'Class B', 'Series C', 'Dividend', 'Growth', 'Income', 'USD', 'EUR']
    modifier = random.choice(modifiers)
    parts = [issuer, instrument]
    if modifier:
        parts.append(modifier)
    return ' '.join(parts).strip()

# Description variation function with multiple options
def create_description_variation(desc: str) -> str:
    desc_variants = {
        'Equity Fund': [
            'Equity Portfolio', 'Equity Investment Vehicle', 'Shareholder Fund',
            'Stock Investment Fund', 'Equity Securities Fund', 'Listed Equity Fund'
        ],
        'Bond Fund': [
            'Fixed Income Fund', 'Bond Investment Vehicle', 'Debt Securities Fund',
            'Income Securities Fund', 'Credit Securities Fund', 'Yield Bond Fund'
        ],
        'Preferred Shares': [
            'Preference Shares', 'Priority Stock', 'Preferred Stock',
            'Senior Equity', 'Preferred Equity', 'Hybrid Equity Shares'
        ],
        'Government Bond': [
            'Sovereign Bond', 'Public Sector Bond', 'Treasury Securities',
            'National Debt Instrument', 'Public Bond', 'Government Debt Note'
        ],
        'Corporate Bond': [
            'Company Debt', 'Corporate Securities', 'Private Bond',
            'Business Debt Securities', 'Enterprise Bond', 'Issuer Bond'
        ],
        'ETF': [
            'Exchange-Traded Product', 'Market ETF', 'Listed ETF',
            'Passive Investment Vehicle', 'Exchange-Listed Fund', 'ETF Security'
        ],
        'Index Fund': [
            'Benchmark Fund', 'Passive Equity', 'Market-Tracking Fund',
            'Index Tracking Fund', 'Indexed Portfolio', 'Rule-Based Fund'
        ],
        'Convertible Bond': [
            'Hybrid Security', 'Debt-Equity Convertible',
            'Convertible Debt Instrument', 'Hybrid Bond', 'Convertible Securities'
        ],
        'REIT': [
            'Property Trust', 'Real Estate Investment Trust', 'Income Property Fund',
            'Commercial Property Trust', 'REIT Portfolio', 'Real Estate Securities'
        ],
        'Money Market': [
            'Liquidity Fund', 'Cash Management Fund',
            'Short-Term Debt Fund', 'Capital Preservation Fund', 'Cash Equivalent Fund'
        ],
        # Optional additions for broader coverage:
        'Credit Fund': [
            'Debt Opportunity Fund', 'Credit Strategy Fund', 'Private Credit Portfolio'
        ],
        'Commodities Fund': [
            'Resource Investment Fund', 'Hard Asset Fund', 'Commodity Exposure Fund'
        ],
        'Infrastructure Fund': [
            'Public Works Investment Fund', 'Essential Services Fund', 'Infrastructure Assets Trust'
        ],
        'Hedge Fund': [
            'Absolute Return Fund', 'Multi-Strategy Hedge Fund', 'Alpha-Seeking Fund'
        ]
    }

    for key, vals in desc_variants.items():
        if key in desc:
            desc = desc.replace(key, random.choice(vals))
            break

    modifiers = ['International', 'Strategic', 'Enhanced', 'Aggressive', 'Sustainable', 'Ethical', 'Global', 'Dynamic']
    if random.random() < 0.4:
        desc = f"{random.choice(modifiers)} {desc}"
    if random.random() < 0.15:
        desc = f"{desc} Series {random.choice(['A', 'B', 'C'])}"
    return desc

def build_shared_entities(n: int = 1000) -> List[Tuple[str, str, str, str]]:
    shared = []
    for _ in range(n):
        name = random.choice(company_names)
        desc = generate_invented_description()
        country = random.choice(countries)
        type_ = random.choice(types)
        shared.append((name, desc, country, type_))
    return shared

def generate_enhanced_table(prefix: str,
                            id_length: int,
                            shared_entities: List[Tuple[str, str, str, str]],
                            total_rows: int,
                            shared_frac: float) -> pd.DataFrame:
    data = []
    max_shared = min(len(shared_entities), int(total_rows * max(0.0, min(shared_frac, 1.0))))
    shared_sample = random.sample(shared_entities, max_shared)

    for entity in shared_sample:
        unique_id = prefix + ''.join(random.choices('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=id_length))
        soft_name = generate_security_name()
        soft_desc = create_description_variation(entity[1])
        data.append([unique_id, soft_name, soft_desc, entity[2], entity[3]])

    for _ in range(total_rows - max_shared):
        unique_id = prefix + ''.join(random.choices('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=id_length))
        name = generate_security_name()
        desc = create_description_variation(generate_invented_description())
        data.append([unique_id, name, desc, random.choice(countries), random.choice(types)])

    return pd.DataFrame(data, columns=['id', 'name', 'description', 'country', 'type'])

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a synthetic ISIN-like instruments CSV with rich names/descriptions."
    )
    parser.add_argument("-r", "--rows", type=int, default=DEFAULT_ROWS,
                        help=f"Total number of rows to generate (default: {DEFAULT_ROWS}).")
    parser.add_argument("-o", "--output", type=str, default=DEFAULT_OUTPUT,
                        help=f"Output CSV file path (default: {DEFAULT_OUTPUT}).")
    parser.add_argument("--prefix", type=str, default=DEFAULT_PREFIX,
                        help=f"Identifier prefix (default: {DEFAULT_PREFIX}).")
    parser.add_argument("--id-length", type=int, default=DEFAULT_ID_LENGTH,
                        help=f"Random suffix length for ID after prefix (default: {DEFAULT_ID_LENGTH}).")
    parser.add_argument("--shared-frac", type=float, default=DEFAULT_SHARED_FRAC,
                        help=f"Fraction [0,1] of rows reusing shared entities (default: {DEFAULT_SHARED_FRAC}).")
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED,
                        help=f"Random seed for reproducibility (default: {DEFAULT_SEED}).")
    return parser.parse_args()

def main() -> None:
    args = parse_args()
    init_seeds(args.seed)

    # Prepare shared entities pool (kept at 1000 for variety; independent of --rows)
    shared_entities = build_shared_entities(n=1000)

    df = generate_enhanced_table(
        prefix=args.prefix,
        id_length=args.id_length,
        shared_entities=shared_entities,
        total_rows=args.rows,
        shared_frac=args.shared_frac
    )

    df.to_csv(args.output, index=False)
    print(f"Wrote {len(df):,} rows to {args.output}")

if __name__ == "__main__":
    main()
