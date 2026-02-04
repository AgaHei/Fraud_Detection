"""
Generate Demo Fraud Detection Report

Standalone script to generate a summary report of ALL transactions
currently in the database. Perfect for demos and testing.

Unlike the Airflow DAG (which queries yesterday's data), this script
summarizes everything in the database to show actual results.

Run from project root:
    python src/generate_demo_report.py

Output:
    - Console report
    - Saved to logs/demo_report_{timestamp}.txt
"""

import psycopg2
from datetime import datetime
import sys
import os

# Add config to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.config import DB_CONFIG, PATHS

# ─────────────────────────────────────────────────────────────
# Query Database
# ─────────────────────────────────────────────────────────────

def query_all_transactions():
    """Query all transactions and fraud predictions from database"""
    try:
        conn = psycopg2.connect(DB_CONFIG['connection_string'])
        cursor = conn.cursor()
        
        # Overall summary
        summary_query = """
        SELECT 
            COUNT(*) as total_transactions,
            SUM(CASE WHEN predicted_fraud THEN 1 ELSE 0 END) as fraud_count,
            SUM(CASE WHEN NOT predicted_fraud THEN 1 ELSE 0 END) as legitimate_count,
            AVG(fraud_probability) as avg_fraud_prob,
            MAX(fraud_probability) as max_fraud_prob,
            MIN(fraud_probability) as min_fraud_prob,
            SUM(amount) as total_amount,
            AVG(amount) as avg_amount,
            SUM(CASE WHEN predicted_fraud THEN amount ELSE 0 END) as fraud_amount,
            MIN(timestamp) as first_transaction,
            MAX(timestamp) as last_transaction
        FROM fraud_transactions
        """
        
        cursor.execute(summary_query)
        summary = cursor.fetchone()
        
        # Category breakdown
        category_query = """
        SELECT 
            category,
            COUNT(*) as count,
            SUM(CASE WHEN predicted_fraud THEN 1 ELSE 0 END) as fraud_count,
            AVG(amount) as avg_amount
        FROM fraud_transactions
        GROUP BY category
        ORDER BY fraud_count DESC, count DESC
        LIMIT 10
        """
        
        cursor.execute(category_query)
        categories = cursor.fetchall()
        
        # High-risk transactions (top fraud probabilities)
        high_risk_query = """
        SELECT 
            transaction_id,
            timestamp,
            amount,
            category,
            fraud_probability,
            predicted_fraud
        FROM fraud_transactions
        ORDER BY fraud_probability DESC
        LIMIT 5
        """
        
        cursor.execute(high_risk_query)
        high_risk = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return {
            'summary': summary,
            'categories': categories,
            'high_risk': high_risk
        }
        
    except Exception as e:
        print(f"❌ Database query error: {e}")
        sys.exit(1)

# ─────────────────────────────────────────────────────────────
# Generate Report
# ─────────────────────────────────────────────────────────────

def generate_report(data):
    """Format and generate the report"""
    
    summary = data['summary']
    
    # Calculate metrics
    total = summary[0] or 0
    fraud_count = summary[1] or 0
    legitimate = summary[2] or 0
    avg_prob = float(summary[3]) if summary[3] else 0.0
    max_prob = float(summary[4]) if summary[4] else 0.0
    min_prob = float(summary[5]) if summary[5] else 0.0
    total_amount = float(summary[6]) if summary[6] else 0.0
    avg_amount = float(summary[7]) if summary[7] else 0.0
    fraud_amount = float(summary[8]) if summary[8] else 0.0
    first_ts = summary[9]
    last_ts = summary[10]
    
    fraud_rate = (fraud_count / total * 100) if total > 0 else 0.0
    
    # Build report
    report = f"""
{'='*70}
                    FRAUD DETECTION DEMO REPORT
{'='*70}
Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

{'─'*70}
OVERVIEW
{'─'*70}
Time Range:                {first_ts} to {last_ts}
Total Transactions:        {total:>10,}
Legitimate:                {legitimate:>10,} ({legitimate/total*100:>5.1f}%)
Fraudulent:                {fraud_count:>10,} ({fraud_rate:>5.2f}%)

{'─'*70}
FINANCIAL IMPACT
{'─'*70}
Total Transaction Volume:  ${total_amount:>13,.2f}
Average Transaction:       ${avg_amount:>13,.2f}
Fraud Amount Detected:     ${fraud_amount:>13,.2f}

{'─'*70}
FRAUD DETECTION PERFORMANCE
{'─'*70}
Average Fraud Probability: {avg_prob:>13.4f}
Maximum Fraud Probability: {max_prob:>13.4f}
Minimum Fraud Probability: {min_prob:>13.4f}

{'─'*70}
TOP CATEGORIES BY FRAUD COUNT
{'─'*70}
{'Category':<25} {'Total':<10} {'Fraud':<10} {'Avg Amount':<15}
{'-'*70}
"""
    
    # Add category breakdown
    for cat in data['categories']:
        category = cat[0] or 'Unknown'
        count = cat[1]
        fraud = cat[2]
        avg_amt = float(cat[3]) if cat[3] else 0.0
        report += f"{category:<25} {count:<10} {fraud:<10} ${avg_amt:>12,.2f}\n"
    
    # Add high-risk transactions
    report += f"""
{'─'*70}
TOP 5 HIGHEST RISK TRANSACTIONS
{'─'*70}
"""
    
    for i, txn in enumerate(data['high_risk'], 1):
        txn_id = txn[0][:16] + "..."
        timestamp = txn[1]
        amount = float(txn[2])
        category = txn[3]
        prob = float(txn[4])
        is_fraud = "🚨 FRAUD" if txn[5] else "✓ Legitimate"
        
        report += f"""
{i}. Transaction: {txn_id}
   Time: {timestamp}  |  Amount: ${amount:,.2f}
   Category: {category}
   Fraud Probability: {prob:.4f}  |  Prediction: {is_fraud}
"""
    
    report += f"""
{'='*70}
END OF REPORT
{'='*70}
"""
    
    return report

# ─────────────────────────────────────────────────────────────
# Save Report
# ─────────────────────────────────────────────────────────────

def save_report(report):
    """Save report to logs directory"""
    os.makedirs(PATHS['logs_dir'], exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = os.path.join(PATHS['logs_dir'], f'demo_report_{timestamp}.txt')
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(report)
    
    return filename

# ─────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────

def main():
    print("\n🔍 Querying database...")
    data = query_all_transactions()
    
    print("📊 Generating report...")
    report = generate_report(data)
    
    print("💾 Saving report...")
    filename = save_report(report)
    
    # Display report
    print(report)
    
    print(f"\n✅ Report saved to: {filename}\n")

if __name__ == '__main__':
    main()
