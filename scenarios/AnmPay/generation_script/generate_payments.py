import argparse
import csv
import random
import re
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

"""
python generate_payments.py --names-csv base_names.csv --reasons-csv base_reasons.csv --out-dir ../dataset  --num-payments 10000
"""


# ———————— Seed for reproducibility ————————
SEED = 42
random.seed(SEED)
np.random.seed(SEED)


# ------------------------------
# Helper Functions
# ------------------------------

def random_iban():
    """Generate a pseudo-IBAN: 2-letter country + 20 digits."""
    country = random.choice(['DE', 'FR', 'ES', 'IT', 'NL', 'BE', 'LU', 'AT', 'PT', 'GR'])
    digits = ''.join(random.choices('0123456789', k=20))
    return f"{country}{digits}"


def random_bic_9():
    """Generate a 9-character alphanumeric BIC code."""
    return ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=9))


import random
import re
import unicodedata

def name_variations_for(name: str) -> list:
    """
    Produce plausible real-world variations of a base name:
     - case variants
     - initial-style
     - reversed order
     - concatenated (no space)
     - diacritic-stripped
     - apostrophe/hyphen variants
     - simple typos (adjacent-key swaps)
     - common nicknames for a handful of popular names
    """
    variations = set()

    # normalize whitespace
    name = re.sub(r'\s+', ' ', name).strip()

    # 1) Basic case variants
    variations.update({
        name,
        name.lower(),
        name.upper(),
        name.title(),
    })

    # 2) Strip diacritics
    no_diac = unicodedata.normalize('NFKD', name)
    no_diac = ''.join(c for c in no_diac if not unicodedata.combining(c))
    if no_diac != name:
        variations.add(no_diac)

    parts = name.split(' ')
    # 3) If we have at least first & last
    if len(parts) >= 2:
        first, last = parts[0], parts[-1]

        # initials
        variations.add(f"{first[0]}. {last}")
        variations.add(f"{first[0]}.{last}")
        variations.add(f"{first[0]} {last[0]}.")
        variations.add(f"{first[0]}{last[0]}")

        # reversed
        variations.add(f"{last}, {first}")
        variations.add(f"{last} {first}")

        # concatenated
        variations.add(f"{first}{last}")

        # hyphen / underscore instead of space
        variations.add(f"{first}-{last}")
        variations.add(f"{first}_{last}")

        # drop middle parts entirely
        if len(parts) > 2:
            variations.add(f"{first} {parts[-1]}")

        # simple typos in last name (one adjacent swap)
        if len(last) > 3:
            lst = list(last)
            i = random.randint(0, len(lst) - 2)
            lst[i], lst[i+1] = lst[i+1], lst[i]
            variations.add(f"{first} {''.join(lst)}")

        # common nickname substitutions
        nick_map = {
            'William': ['Will', 'Bill'],
            'Robert': ['Rob', 'Bob'],
            'Elizabeth': ['Liz', 'Beth'],
            'Katherine': ['Kate', 'Katie'],
            'Michael': ['Mike'],
            'Jennifer': ['Jen'],
        }
        for formal, nicks in nick_map.items():
            if first.lower() == formal.lower():
                for nick in nicks:
                    variations.add(f"{nick} {last}")

    else:
        # single-token name variants
        single = parts[0]
        # apostrophe removal
        if "'" in single:
            variations.add(single.replace("'", ""))
        # hyphen removal
        if '-' in single:
            variations.add(single.replace('-', ''))
        # simple typo swap
        if len(single) > 3:
            s = list(single)
            i = random.randint(0, len(s) - 2)
            s[i], s[i+1] = s[i+1], s[i]
            variations.add(''.join(s))

    # 4) final cleanup: strip and remove empties
    return sorted(v for v in variations if v and len(v) <= len(name) + 5)



def payment_reason_variations(reason: str, max_swaps: int = 2) -> list:
    """
    Given a base reason, produce plausible variants:
      - case changes (lower, upper, title, swapcase)
      - common abbreviations
      - vowel‐drops (per-word and whole)
      - swapped characters (up to max_swaps independent swaps)
      - punctuation variants (dots, hyphens, underscores)
    """
    vars_ = set()

    # 1) Base case variants
    vars_.update({
        reason,
        reason.lower(),
        reason.upper(),
        reason.title(),
        reason.swapcase()
    })

    # 2) Whole‐phrase vowel drop
    no_vowels_full = re.sub(r'[aeiouAEIOU]', '', reason)
    vars_.add(no_vowels_full)

    # 3) Per‐word vowel drop
    words = reason.split()
    vw_dropped = []
    for w in words:
        w_nv = re.sub(r'[aeiouAEIOU]', '', w)
        vw_dropped.append(w_nv)
    vars_.add(' '.join(vw_dropped))

    # 4) Abbreviations map
    abbr = {
        'payment': ['pymt', 'paymt', 'pay.'],
        'invoice': ['inv', 'inv.', 'invc'],
        'subscription': ['subscr', 'sub.', 'subs'],
        'reimbursement': ['reimb', 'reimb.'],
        'premium': ['prem', 'prem.'],
        'installment': ['inst', 'inst.'],
        'installment': ['inst', 'inst.'],
        'reimbursement': ['reimb', 'reimb.'],
        'transfer': ['xfer'],
        'fee': ['f', 'fe']
    }
    for i, w in enumerate(words):
        key = w.lower().rstrip('.,-')
        if key in abbr:
            for a in abbr[key]:
                v = words.copy()
                v[i] = a
                vars_.add(' '.join(v))

    # 5) Punctuation variants: swap spaces ↔ dot, hyphen, underscore
    for v in list(vars_):
        vars_.add(v.replace(' ', '-'))
        vars_.add(v.replace(' ', '_'))

    # 6) Character swaps (up to max_swaps random adjacent swaps)
    def random_swaps(s, n):
        s = list(s)
        for _ in range(n):
            if len(s) < 2: break
            i = random.randint(0, len(s)-2)
            s[i], s[i+1] = s[i+1], s[i]
        return ''.join(s)

    for v in list(vars_):
        for swaps in range(1, max_swaps+1):
            vars_.add(random_swaps(v, swaps))

    # 7) Trim and dedupe
    return sorted({v.strip() for v in vars_ if v.strip()})



# ------------------------------
# I/O & Generation Methods
# ------------------------------

def load_list_from_csv(path: str, column: str) -> list:
    """Load a single-column CSV into a Python list."""
    df = pd.read_csv(path, dtype=str)
    if column not in df.columns:
        raise ValueError(f"Column '{column}' not found in {path}")
    return df[column].dropna().astype(str).tolist()


def generate_accounts(names: list) -> pd.DataFrame:
    """Generate accounts DataFrame with IBAN and BIC for each name."""
    accounts = []
    for name in names:
        accounts.append({
            'iban': random_iban(),
            'account_holder_name': name,
            'bic_code': random_bic_9()
        })
    return pd.DataFrame(accounts)


def generate_payments(
    base_names: list,
    name_variations: dict,
    bic_lookup: dict,
    reasons: list,
    num_payments: int,
    start_date: datetime
) -> pd.DataFrame:
    """Generate a payments DataFrame of size num_payments."""
    payments = []
    for pid in range(1, num_payments + 1):
        origin_base = random.choice(base_names)
        benef_base = random.choice(base_names)

        payments.append({
            'payment_id': pid,
            'bic_origin': bic_lookup[origin_base],
            'bic_beneficiary': bic_lookup[benef_base],
            'originator_name': random.choice(name_variations[origin_base]),
            'beneficiary_name': random.choice(name_variations[benef_base]),
            'payment_reason': random.choice(reasons),
            'amount_usd': round(random.uniform(5.0, 50000.0), 2),
            'payment_date': start_date + timedelta(days=random.randint(0, 365))
        })
    return pd.DataFrame(payments)


def save_dataframe(df: pd.DataFrame, path: str):
    """Save DataFrame to CSV with quoted fields."""
    df.to_csv(
        path,
        index=False,
        encoding='utf-8',
        quoting=csv.QUOTE_ALL,
        quotechar='"'
    )


# ------------------------------
# Main
# ------------------------------

def main():
    p = argparse.ArgumentParser(description="Generate synthetic accounts & payments.")
    p.add_argument('--names-csv',   required=True, help="CSV file with column 'name'")
    p.add_argument('--reasons-csv', required=True, help="CSV file with column 'reason'")
    p.add_argument('--out-dir',     default='./dataset', help="Output directory")
    p.add_argument('--num-payments',type=int, default=10000, help="Number of payments to generate")
    args = p.parse_args()

    # Load base data
    base_names   = load_list_from_csv(args.names_csv,   'name')
    base_reasons = load_list_from_csv(args.reasons_csv, 'reason')

    # Expand payment reasons with variations
    all_reasons = []
    for r in base_reasons:
        all_reasons.append(r)
        all_reasons.extend(payment_reason_variations(r))
    all_reasons = list(dict.fromkeys(all_reasons))

    # Build accounts
    accounts_df = generate_accounts(base_names)
    bic_lookup  = dict(zip(accounts_df['account_holder_name'], accounts_df['bic_code']))

    # Precompute name variations
    name_variations = {n: name_variations_for(n) for n in base_names}

    # Generate payments
    start_date   = datetime.now() - timedelta(days=365)
    payments_df  = generate_payments(
        base_names,
        name_variations,
        bic_lookup,
        all_reasons,
        args.num_payments,
        start_date
    )

    # Save outputs
    accounts_path = f"{args.out_dir}/accounts.csv"
    payments_path = f"{args.out_dir}/payments.csv"
    save_dataframe(accounts_df, accounts_path)
    save_dataframe(payments_df, payments_path)

    print(f"Saved {len(accounts_df)} accounts to {accounts_path}")
    print(f"Saved {len(payments_df)} payments to {payments_path}")


if __name__ == '__main__':
    main()

