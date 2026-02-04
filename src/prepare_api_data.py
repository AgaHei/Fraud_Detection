"""
Prepare API Test Set

Splits the fraud detection dataset into:
- Training data (for model building) → already done in notebook
- Test data (for API simulation) → this script creates it

The test set becomes the "production simulation" data that the API serves.

Run from project root:
    python src/prepare_api_data.py
"""

import pandas as pd
from sklearn.model_selection import train_test_split
import os

# ─────────────────────────────────────────────────────────────
# Paths (relative to project root)
# ─────────────────────────────────────────────────────────────
DATA_DIR = 'data'
INPUT_FILE = os.path.join(DATA_DIR, 'fraudTest.csv')
OUTPUT_FILE = os.path.join(DATA_DIR, 'api_test_set.csv')

# ─────────────────────────────────────────────────────────────
# Load and Split Data
# ─────────────────────────────────────────────────────────────

print("="*60)
print("PREPARING API TEST SET")
print("="*60)

print(f"\nLoading {INPUT_FILE}...")
if not os.path.exists(INPUT_FILE):
    print(f"ERROR: {INPUT_FILE} not found!")
    print("Make sure you're running from project root and fraudTest.csv is in data/")
    exit(1)

df = pd.read_csv(INPUT_FILE)

print(f"Total transactions: {len(df):,}")
print(f"Fraud rate: {df['is_fraud'].mean()*100:.2f}%")

# Split: 80% for API, 20% reserve (in case you need more data later)
# We use stratify to maintain fraud ratio
api_data, _ = train_test_split(
    df,
    test_size=0.2,
    random_state=42,
    stratify=df['is_fraud']
)

print(f"\nAPI simulation set: {len(api_data):,} transactions")
print(f"Fraud rate in API set: {api_data['is_fraud'].mean()*100:.2f}%")

# Save for API to use
api_data.to_csv(OUTPUT_FILE, index=False)

print(f"\n✅ API test set saved to: {OUTPUT_FILE}")
print("   The Flask API will serve random transactions from this file")
print("\n" + "="*60)
