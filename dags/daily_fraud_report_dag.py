"""
Daily Fraud Report DAG

Airflow DAG that runs every morning to generate a summary report
of all transactions and fraud detections from the previous day.

Schedule: Daily at 15:30 (3:30 PM) - Demo time
Owner: Fraud Detection Team

Tasks:
1. Query yesterday's transactions from PostgreSQL
2. Generate summary statistics
3. Send report via email/log

Setup:
    - Place this file in your Airflow dags/ folder
    - Ensure Airflow has access to your .env configuration
    - Set up email notifications in Airflow config (optional)
"""

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from datetime import datetime, timedelta
import psycopg2
import logging
import os
import sys
from airflow.utils import timezone
import pytz

# Database configuration - use environment variable
DB_CONFIG = {
    'connection_string': os.getenv('NEON_CONNECTION_STRING', 'postgresql://user:password@localhost:5432/database')
}

# ─────────────────────────────────────────────────────────────
# DAG Configuration
# ─────────────────────────────────────────────────────────────

default_args = {
    'owner': 'fraud-detection-team',
    'depends_on_past': False,
    'email_on_failure': False,  # Set to True and configure email in Airflow
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'daily_fraud_report',
    default_args=default_args,
    description='Generate daily fraud detection summary report',
    schedule_interval='0 16 * * *',  # Every day at 16:00 (4:00 PM) Paris time
    start_date=datetime(2026, 2, 4, 16, 0, 0, tzinfo=pytz.timezone('Europe/Paris')),  # Start from yesterday so today runs
    catchup=False,  # Don't backfill historical runs
    tags=['fraud-detection', 'daily', 'reporting'],
)

# ─────────────────────────────────────────────────────────────
# Task Functions
# ─────────────────────────────────────────────────────────────

def query_yesterday_transactions(**context):
    """
    Query all transactions from yesterday.
    Stores results in XCom for downstream tasks.
    """
    logger = logging.getLogger(__name__)
    
    try:
        # Calculate yesterday's date range
        execution_date = context['execution_date']
        yesterday = execution_date - timedelta(days=1)
        yesterday_start = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
        yesterday_end = yesterday.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        logger.info(f"Querying transactions from {yesterday_start} to {yesterday_end}")
        
        # Connect to database
        conn = psycopg2.connect(DB_CONFIG['connection_string'])
        cursor = conn.cursor()
        
        # Query yesterday's transactions
        query = """
        SELECT 
            COUNT(*) as total_transactions,
            SUM(CASE WHEN predicted_fraud THEN 1 ELSE 0 END) as fraud_count,
            SUM(CASE WHEN NOT predicted_fraud THEN 1 ELSE 0 END) as legitimate_count,
            AVG(fraud_probability) as avg_fraud_prob,
            MAX(fraud_probability) as max_fraud_prob,
            SUM(amount) as total_amount,
            AVG(amount) as avg_amount,
            SUM(CASE WHEN predicted_fraud THEN amount ELSE 0 END) as fraud_amount
        FROM fraud_transactions
        WHERE timestamp >= %s AND timestamp <= %s
        """
        
        cursor.execute(query, (yesterday_start, yesterday_end))
        result = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        # Package results
        report_data = {
            'date': yesterday.strftime('%Y-%m-%d'),
            'total_transactions': result[0] or 0,
            'fraud_count': result[1] or 0,
            'legitimate_count': result[2] or 0,
            'avg_fraud_prob': float(result[3]) if result[3] else 0.0,
            'max_fraud_prob': float(result[4]) if result[4] else 0.0,
            'total_amount': float(result[5]) if result[5] else 0.0,
            'avg_amount': float(result[6]) if result[6] else 0.0,
            'fraud_amount': float(result[7]) if result[7] else 0.0,
        }
        
        logger.info(f"Query complete: {report_data['total_transactions']} transactions found")
        
        # Push to XCom for next task
        return report_data
        
    except Exception as e:
        logger.error(f"Error querying transactions: {e}")
        raise

def generate_report(**context):
    """
    Generate formatted report from query results.
    """
    logger = logging.getLogger(__name__)
    
    # Pull data from previous task
    ti = context['ti']
    report_data = ti.xcom_pull(task_ids='query_transactions')
    
    if not report_data:
        logger.warning("No data received from query task")
        return
    
    # Calculate derived metrics
    fraud_rate = (report_data['fraud_count'] / report_data['total_transactions'] * 100) \
                 if report_data['total_transactions'] > 0 else 0
    
    # Format report
    report = f"""
    ============================================================
    DAILY FRAUD DETECTION REPORT
    ============================================================
    Date: {report_data['date']}
    Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    
    TRANSACTION SUMMARY:
    ────────────────────────────────────────────────────────────
    Total Transactions:        {report_data['total_transactions']:>10,}
    Legitimate:                {report_data['legitimate_count']:>10,}
    Fraudulent:                {report_data['fraud_count']:>10,}
    Fraud Rate:                {fraud_rate:>9.2f}%
    
    FINANCIAL IMPACT:
    ────────────────────────────────────────────────────────────
    Total Transaction Volume:  ${report_data['total_amount']:>10,.2f}
    Average Transaction:       ${report_data['avg_amount']:>10,.2f}
    Fraud Amount Prevented:    ${report_data['fraud_amount']:>10,.2f}
    
    FRAUD DETECTION METRICS:
    ────────────────────────────────────────────────────────────
    Avg Fraud Probability:     {report_data['avg_fraud_prob']:>9.4f}
    Max Fraud Probability:     {report_data['max_fraud_prob']:>9.4f}
    
    ============================================================
    """
    
    logger.info(report)
    
    # TODO: Send via email
    # send_email(report)
    
    # Store report for access
    context['ti'].xcom_push(key='report_text', value=report)
    
    return report

def send_notification(**context):
    """
    Send report notification.
    Currently logs to Airflow; extend to email/Slack.
    """
    logger = logging.getLogger(__name__)
    
    ti = context['ti']
    report_data = ti.xcom_pull(task_ids='query_transactions')
    
    if report_data and report_data['fraud_count'] > 0:
        logger.warning(
            f"⚠️ ALERT: {report_data['fraud_count']} fraudulent transactions detected yesterday!"
        )
    else:
        logger.info("✅ No fraud detected yesterday")
    
    # TODO: Implement actual notification
    # send_slack_notification(report_data)
    # send_email_notification(report_data)

# ─────────────────────────────────────────────────────────────
# Define Tasks
# ─────────────────────────────────────────────────────────────

query_task = PythonOperator(
    task_id='query_transactions',
    python_callable=query_yesterday_transactions,
    dag=dag,
)

generate_report_task = PythonOperator(
    task_id='generate_report',
    python_callable=generate_report,
    dag=dag,
)

notify_task = PythonOperator(
    task_id='send_notification',
    python_callable=send_notification,
    dag=dag,
)

# ─────────────────────────────────────────────────────────────
# Task Dependencies
# ─────────────────────────────────────────────────────────────

query_task >> generate_report_task >> notify_task
