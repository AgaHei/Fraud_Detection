"""
Mock Transaction API - Simulates Real-Time Payment Stream

This Flask API serves random transactions from the fraud detection test set,
simulating a real-time payment stream that updates every minute.

Run from project root:
    python src/mock_transaction_api.py

Endpoints:
    GET /transaction  → Returns a single random transaction as JSON
    GET /health       → Health check endpoint
"""

from flask import Flask, jsonify
import pandas as pd
import numpy as np
from datetime import datetime
import os

app = Flask(__name__)

# ─────────────────────────────────────────────────────────────
# Configuration (relative to project root)
# ─────────────────────────────────────────────────────────────
DATA_DIR = 'data'
TEST_SET_PATH = os.path.join(DATA_DIR, 'api_test_set.csv')

# ─────────────────────────────────────────────────────────────
# Load Test Set (API Data Source)
# ─────────────────────────────────────────────────────────────

print("="*60)
print("LOADING TEST DATA FOR API SIMULATION")
print("="*60)

if not os.path.exists(TEST_SET_PATH):
    print(f"\n❌ ERROR: {TEST_SET_PATH} not found!")
    print("\nPlease run this first:")
    print("    python src/prepare_api_data.py")
    print("\nThis will create the api_test_set.csv file.")
    test_data = None
else:
    test_data = pd.read_csv(TEST_SET_PATH)
    print(f"\n✅ Loaded {len(test_data):,} transactions for simulation")
    print(f"   Fraud rate: {test_data['is_fraud'].mean()*100:.2f}%")

# ─────────────────────────────────────────────────────────────
# API Endpoints
# ─────────────────────────────────────────────────────────────

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'transactions_available': len(test_data) if test_data is not None else 0
    })

@app.route('/transaction', methods=['GET'])
def get_transaction():
    """
    Returns a single random transaction from the test set.
    Simulates a new payment arriving in real-time.
    """
    if test_data is None:
        return jsonify({
            'error': 'Test data not loaded',
            'message': 'Run prepare_api_data.py first to create api_test_set.csv'
        }), 500
    
    # Pick a random transaction
    random_idx = np.random.randint(0, len(test_data))
    transaction = test_data.iloc[random_idx]
    
    # Convert to dict and handle NaN values
    transaction_dict = transaction.to_dict()
    
    # Replace NaN with None (for JSON serialization)
    for key, value in transaction_dict.items():
        if pd.isna(value):
            transaction_dict[key] = None
    
    # Add current timestamp to simulate "just arrived"
    transaction_dict['api_timestamp'] = datetime.now().isoformat()
    
    return jsonify(transaction_dict)

# ─────────────────────────────────────────────────────────────
# Run Server
# ─────────────────────────────────────────────────────────────

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 MOCK TRANSACTION API STARTED")
    print("="*60)
    print("\nEndpoints:")
    print("  GET http://localhost:5000/transaction  → Get random transaction")
    print("  GET http://localhost:5000/health       → Health check")
    print("\nSimulating real-time payment stream...")
    print("Press Ctrl+C to stop")
    print("="*60 + "\n")
    
    # Run on all interfaces so it's accessible from containers if needed later
    app.run(host='0.0.0.0', port=5000, debug=True)
