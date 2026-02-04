"""
Configuration File - Fraud Detection Project

Centralizes all configuration settings:
- Database connection
- Model parameters
- API settings
- Notification settings

Usage:
    from config.config import DB_CONFIG, MODEL_CONFIG, FRAUD_THRESHOLD
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file (for sensitive data)
load_dotenv()

# ─────────────────────────────────────────────────────────────
# DATABASE CONFIGURATION
# ─────────────────────────────────────────────────────────────

DB_CONFIG = {
    'connection_string': os.getenv('NEON_CONNECTION_STRING'),
    # Example: postgresql://user:pass@host/dbname?sslmode=require
    
    'table_name': 'fraud_transactions',
}

# ─────────────────────────────────────────────────────────────
# MODEL CONFIGURATION
# ─────────────────────────────────────────────────────────────

MODEL_CONFIG = {
    'model_path': 'models/fraud_detection_pipeline.joblib',
    'fraud_threshold': 0.4,  # Probability threshold for fraud detection
}

# Quick access to threshold (used frequently)
FRAUD_THRESHOLD = MODEL_CONFIG['fraud_threshold']

# ─────────────────────────────────────────────────────────────
# API CONFIGURATION
# ─────────────────────────────────────────────────────────────

API_CONFIG = {
    'host': 'localhost',
    'port': 5000,
    'transaction_endpoint': 'http://localhost:5000/transaction',
    'poll_interval_seconds': 60,  # How often to check for new transactions
}

# ─────────────────────────────────────────────────────────────
# NOTIFICATION CONFIGURATION
# ─────────────────────────────────────────────────────────────

NOTIFICATION_CONFIG = {
    'method': 'email',  # Options: 'email', 'slack', 'log'
    
    # Email settings (if method='email')
    'smtp_server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
    'smtp_port': int(os.getenv('SMTP_PORT', 587)),
    'sender_email': os.getenv('SENDER_EMAIL'),
    'sender_password': os.getenv('SENDER_PASSWORD'),
    'recipient_email': os.getenv('RECIPIENT_EMAIL'),
    
    # Slack settings (if method='slack')
    'slack_webhook_url': os.getenv('SLACK_WEBHOOK_URL'),
}

# ─────────────────────────────────────────────────────────────
# PATHS
# ─────────────────────────────────────────────────────────────

PATHS = {
    'data_dir': 'data',
    'models_dir': 'models',
    'logs_dir': 'logs',
}

# ─────────────────────────────────────────────────────────────
# LOGGING CONFIGURATION
# ─────────────────────────────────────────────────────────────

LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'log_file': 'logs/fraud_detection.log',
}
