# Enhanced version: much richer company name and description variations

import pandas as pd
import random
import faker

# Initialize Faker and random seed
fake = faker.Faker()
random.seed(42)
faker.Faker.seed(42)

# Constants
num_rows = 10000
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


# Function to generate richer descriptions
def generate_invented_description():
    adjectives = random.sample(instrument_keywords, 2)
    instrument = random.choice(instrument_types)
    if random.random() < 0.3:
        suffix = f"Class {random.choice(['A', 'B', 'C'])}"
        return f"{adjectives[0]} {adjectives[1]} {instrument} {suffix}"
    return f"{adjectives[0]} {adjectives[1]} {instrument}"


# Function to generate realistic security names
def generate_security_name():
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
def create_description_variation(desc):
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

# Generate shared entities for controlled overlap
shared_entities = []
for _ in range(1000):
    name = random.choice(company_names)
    desc = generate_invented_description()
    country = random.choice(countries)
    type_ = random.choice(types)
    shared_entities.append((name, desc, country, type_))

# Table generation with enhanced variations
def generate_enhanced_table(prefix, id_length, shared_entities, total_rows):
    data = []
    max_shared = min(len(shared_entities), int(total_rows * 0.3))
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

# Generate ISIN table as example
isin_df_rich = generate_enhanced_table('ISIN', 12, shared_entities, num_rows)

# Save for download
isin_df_rich.to_csv('ISIN.csv', index=False)
