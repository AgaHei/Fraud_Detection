"""
Real-Time Fraud Predictor

Polls the mock transaction API, predicts fraud using the trained model,
stores results in PostgreSQL, and sends notifications for detected fraud.

Run from project root:
    python src/real_time_predictor.py

Requirements:
    - Mock API must be running (python src/mock_transaction_api.py)
    - Neon PostgreSQL database configured in .env
    - Trained model at models/fraud_detection_pipeline.joblib
"""

import requests
import pandas as pd
import joblib
import time
import psycopg2
from datetime import datetime
import logging
import sys
import os
import warnings

# Suppress sklearn version warnings
warnings.filterwarnings('ignore', category=UserWarning, module='sklearn')

# Add config to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.config import (
    DB_CONFIG, 
    MODEL_CONFIG, 
    API_CONFIG, 
    FRAUD_THRESHOLD,
    LOGGING_CONFIG
)

# ─────────────────────────────────────────────────────────────
# Setup Logging  
# ─────────────────────────────────────────────────────────────

# Configure logging with UTF-8 encoding for better Windows compatibility
logging.basicConfig(
    level=LOGGING_CONFIG['level'],
    format=LOGGING_CONFIG['format'],
    handlers=[
        logging.FileHandler(LOGGING_CONFIG['log_file'], encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────
# Load Trained Model
# ─────────────────────────────────────────────────────────────

logger.info("="*60)
logger.info("LOADING TRAINED MODEL")
logger.info("="*60)

try:
    model_path = MODEL_CONFIG['model_path']
    if not os.path.exists(model_path):
        logger.error(f"Model not found at {model_path}")
        logger.error("Please train the model first using notebook 02_model_training.ipynb")
        sys.exit(1)
    
    pipeline = joblib.load(model_path)
    logger.info(f"[SUCCESS] Model loaded successfully from {model_path}")
    logger.info(f"   Fraud threshold: {FRAUD_THRESHOLD}")
except Exception as e:
    logger.error(f"Failed to load model: {e}")
    sys.exit(1)

# ─────────────────────────────────────────────────────────────
# Database Connection
# ─────────────────────────────────────────────────────────────

def get_db_connection():
    """Create PostgreSQL connection with proper SSL handling"""
    try:
        conn_string = DB_CONFIG['connection_string']
        if 'sslmode' not in conn_string:
            conn_string += '?sslmode=require'
        
        conn = psycopg2.connect(
            conn_string,
            connect_timeout=10,
            application_name='fraud_predictor'
        )
        return conn
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return None

# Test connection
logger.info("\nTesting database connection...")
test_conn = get_db_connection()
if test_conn:
    logger.info("[SUCCESS] Database connection successful")
    
    # Create table if it doesn't exist
    try:
        cursor = test_conn.cursor()
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS fraud_transactions (
            transaction_id VARCHAR(255) PRIMARY KEY,
            timestamp TIMESTAMP NOT NULL,
            amount DECIMAL(10, 2) NOT NULL,
            category VARCHAR(100),
            merchant VARCHAR(255),
            gender VARCHAR(10),
            city_pop INTEGER,
            lat DECIMAL(10, 6),
            long DECIMAL(10, 6),
            fraud_probability DECIMAL(5, 4) NOT NULL,
            predicted_fraud BOOLEAN NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        cursor.execute(create_table_sql)
        test_conn.commit()
        cursor.close()
        logger.info("[SUCCESS] Table fraud_transactions is ready")
    except Exception as e:
        logger.warning(f"Could not create/verify table: {e}")
    
    test_conn.close()
else:
    logger.error("❌ Database connection failed. Check your .env file")
    sys.exit(1)

# ─────────────────────────────────────────────────────────────
# Feature Engineering (same as notebook!)
# ─────────────────────────────────────────────────────────────

def engineer_features(transaction_dict):
    """
    Engineer features from raw transaction data.
    Must match exactly the features used during model training!
    
    Returns: pandas DataFrame with engineered features
    """
    # Convert to DataFrame (pipeline expects DataFrame input)
    df = pd.DataFrame([transaction_dict])
    
    # Parse timestamp
    df['trans_date_trans_time'] = pd.to_datetime(df['trans_date_trans_time'])
    
    # Extract temporal features
    df['hour'] = df['trans_date_trans_time'].dt.hour
    df['day_of_week'] = df['trans_date_trans_time'].dt.dayofweek
    df['is_night'] = ((df['hour'] >= 22) | (df['hour'] <= 6)).astype(int)
    df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
    
    # Select only the features the model expects
    feature_columns = [
        'amt',
        'hour', 
        'day_of_week',
        'city_pop',
        'is_night',
        'is_weekend',
        'category',
        'gender'
    ]
    
    return df[feature_columns]

# ─────────────────────────────────────────────────────────────
# Store Prediction in Database
# ─────────────────────────────────────────────────────────────

def store_prediction(transaction, fraud_prob, predicted_fraud):
    """Store transaction and prediction in PostgreSQL"""
    try:
        conn = get_db_connection()
        if not conn:
            logger.error("Could not store prediction - no database connection")
            return False
        
        cursor = conn.cursor()
        
        insert_query = """
        INSERT INTO fraud_transactions 
        (transaction_id, timestamp, amount, category, merchant, gender, 
         city_pop, lat, long, fraud_probability, predicted_fraud)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (transaction_id) DO NOTHING
        """
        
        cursor.execute(insert_query, (
            transaction['trans_num'],
            transaction['trans_date_trans_time'],
            float(transaction['amt']),
            transaction['category'],
            transaction['merchant'],
            transaction['gender'],
            int(transaction['city_pop']),
            float(transaction['lat']),
            float(transaction['long']),
            float(fraud_prob),
            bool(predicted_fraud)
        ))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to store prediction: {e}")
        return False

# ─────────────────────────────────────────────────────────────
# Send Fraud Notification
# ─────────────────────────────────────────────────────────────

def send_notification(transaction, fraud_prob):
    """
    Send fraud alert notification.
    For now: logs to console (implement email/Slack later)
    """
    logger.warning("="*60)
    logger.warning("🚨 FRAUD ALERT 🚨")
    logger.warning("="*60)
    logger.warning(f"Transaction ID: {transaction['trans_num']}")
    logger.warning(f"Amount: ${transaction['amt']:.2f}")
    logger.warning(f"Category: {transaction['category']}")
    logger.warning(f"Merchant: {transaction['merchant']}")
    logger.warning(f"Fraud Probability: {fraud_prob:.2%}")
    logger.warning(f"Timestamp: {transaction['trans_date_trans_time']}")
    logger.warning("="*60)
    
    # TODO: Implement actual email/Slack notification
    # from notification import send_email_alert
    # send_email_alert(transaction, fraud_prob)

# ─────────────────────────────────────────────────────────────
# Main Prediction Loop
# ─────────────────────────────────────────────────────────────

def predict_single_transaction():
    """Fetch one transaction, predict, store, notify if fraud"""
    try:
        # Fetch transaction from API
        response = requests.get(API_CONFIG['transaction_endpoint'], timeout=5)
        response.raise_for_status()
        transaction = response.json()
        
        # Engineer features
        features = engineer_features(transaction)
        
        # Predict
        fraud_prob = pipeline.predict_proba(features)[0][1]  # Probability of fraud
        predicted_fraud = fraud_prob >= FRAUD_THRESHOLD
        
        # Log result
        fraud_status = "FRAUD" if predicted_fraud else "LEGITIMATE"
        logger.info(
            f"Transaction {transaction['trans_num'][:8]}... | "
            f"Amount: ${transaction['amt']:.2f} | "
            f"Prob: {fraud_prob:.4f} | "
            f"Prediction: {fraud_status}"
        )
        
        # Store in database
        stored = store_prediction(transaction, fraud_prob, predicted_fraud)
        if stored:
            logger.info("   [OK] Stored in database")
        
        # Send notification if fraud detected
        if predicted_fraud:
            send_notification(transaction, fraud_prob)
        
        return True
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch transaction from API: {e}")
        return False
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        return False

# ─────────────────────────────────────────────────────────────
# Run Continuous Monitoring
# ─────────────────────────────────────────────────────────────

def run_continuous_monitoring():
    """Poll API at regular intervals and predict fraud"""
    logger.info("\n" + "="*60)
    logger.info("[STARTED] REAL-TIME FRAUD DETECTION STARTED")
    logger.info("="*60)
    logger.info(f"Polling interval: {API_CONFIG['poll_interval_seconds']} seconds")
    logger.info(f"API endpoint: {API_CONFIG['transaction_endpoint']}")
    logger.info(f"Fraud threshold: {FRAUD_THRESHOLD}")
    logger.info("Press Ctrl+C to stop")
    logger.info("="*60 + "\n")
    
    transaction_count = 0
    fraud_count = 0
    
    try:
        while True:
            transaction_count += 1
            logger.info(f"\n[Transaction #{transaction_count}]")
            
            success = predict_single_transaction()
            
            if success:
                # Wait before next poll
                time.sleep(API_CONFIG['poll_interval_seconds'])
            else:
                # If failed, wait a bit longer before retry
                logger.warning("Retrying in 10 seconds...")
                time.sleep(10)
                
    except KeyboardInterrupt:
        logger.info("\n\n" + "="*60)
        logger.info("STOPPED BY USER")
        logger.info("="*60)
        logger.info(f"Total transactions processed: {transaction_count}")
        logger.info("="*60)

# ─────────────────────────────────────────────────────────────
# Entry Point
# ─────────────────────────────────────────────────────────────

if __name__ == '__main__':
    run_continuous_monitoring()
