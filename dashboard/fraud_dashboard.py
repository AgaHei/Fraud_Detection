"""
Fraud Detection Dashboard - Streamlit App

OPTIONAL: Visual dashboard for demo video (makes it more impressive!)

Run:
    pip install streamlit
    streamlit run src/fraud_dashboard.py

This creates a real-time dashboard showing:
- Live transaction stream
- Fraud detection statistics
- Recent alerts
- Performance metrics
"""

import streamlit as st
import pandas as pd
import psycopg2
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.config import DB_CONFIG

# ─────────────────────────────────────────────────────────────
# Page Config
# ─────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Fraud Detection Dashboard",
    page_icon="🚨",
    layout="wide"
)

# ─────────────────────────────────────────────────────────────
# Database Connection
# ─────────────────────────────────────────────────────────────

def get_connection():
    """Create a fresh database connection with proper SSL handling"""
    try:
        # Add SSL configuration for Neon/PostgreSQL
        conn_string = DB_CONFIG['connection_string']
        if 'sslmode' not in conn_string:
            conn_string += '?sslmode=require'
        
        conn = psycopg2.connect(
            conn_string,
            connect_timeout=10,
            application_name='fraud_dashboard'
        )
        return conn
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return None

def execute_query(query, params=None):
    """Execute query with proper connection handling"""
    conn = None
    try:
        conn = get_connection()
        if not conn:
            return None
        
        df = pd.read_sql(query, conn, params=params)
        return df
    except Exception as e:
        st.error(f"Query execution failed: {e}")
        return None
    finally:
        if conn:
            conn.close()

# ─────────────────────────────────────────────────────────────
# Data Loading Functions
# ─────────────────────────────────────────────────────────────

def load_summary_stats():
    """Load overall statistics"""
    query = """
    SELECT 
        COUNT(*) as total,
        SUM(CASE WHEN predicted_fraud THEN 1 ELSE 0 END) as fraud_count,
        AVG(fraud_probability) as avg_prob,
        MAX(fraud_probability) as max_prob,
        SUM(amount) as total_amount
    FROM fraud_transactions
    """
    df = execute_query(query)
    return df.iloc[0] if df is not None and len(df) > 0 else None

def load_recent_transactions(limit=10):
    """Load most recent transactions"""
    query = f"""
    SELECT 
        transaction_id,
        timestamp,
        amount,
        category,
        fraud_probability,
        predicted_fraud
    FROM fraud_transactions
    ORDER BY timestamp DESC
    LIMIT {limit}
    """
    return execute_query(query)

def load_fraud_over_time():
    """Load fraud detection over time"""
    query = """
    SELECT 
        DATE(timestamp) as date,
        COUNT(*) as total,
        SUM(CASE WHEN predicted_fraud THEN 1 ELSE 0 END) as fraud_count
    FROM fraud_transactions
    GROUP BY DATE(timestamp)
    ORDER BY DATE(timestamp)
    """
    return execute_query(query)

def load_category_distribution():
    """Load fraud by category"""
    query = """
    SELECT 
        category,
        COUNT(*) as total,
        SUM(CASE WHEN predicted_fraud THEN 1 ELSE 0 END) as fraud_count
    FROM fraud_transactions
    GROUP BY category
    ORDER BY fraud_count DESC
    LIMIT 10
    """
    return execute_query(query)

# ─────────────────────────────────────────────────────────────
# Dashboard Layout
# ─────────────────────────────────────────────────────────────

st.title("🚨 Real-Time Fraud Detection Dashboard")
st.markdown("---")

# Auto-refresh
if st.button("🔄 Refresh Data"):
    st.rerun()

# ─────────────────────────────────────────────────────────────
# KPI Metrics
# ─────────────────────────────────────────────────────────────

stats = load_summary_stats()

if stats is not None:
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="Total Transactions",
            value=f"{int(stats['total']):,}"
        )

    with col2:
        fraud_count = int(stats['fraud_count'])
        fraud_rate = (fraud_count / stats['total'] * 100) if stats['total'] > 0 else 0
        st.metric(
            label="Fraud Detected",
            value=f"{fraud_count}",
            delta=f"{fraud_rate:.2f}% rate"
        )

    with col3:
        st.metric(
            label="Total Volume",
            value=f"${float(stats['total_amount']):,.2f}"
        )

    with col4:
        st.metric(
            label="Max Fraud Probability",
            value=f"{float(stats['max_prob']):.4f}"
        )
else:
    st.warning("⚠️ Unable to load summary statistics. Check database connection.")

st.markdown("---")

# ─────────────────────────────────────────────────────────────
# Charts
# ─────────────────────────────────────────────────────────────

col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Fraud by Category")
    category_df = load_category_distribution()
    
    if category_df is not None and not category_df.empty:
        fig = px.bar(
            category_df,
            x='category',
            y=['total', 'fraud_count'],
            title="Transaction vs Fraud Count by Category",
            labels={'value': 'Count', 'variable': 'Type'},
            barmode='group'
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data yet")

with col2:
    st.subheader("📈 Fraud Detection Over Time")
    time_df = load_fraud_over_time()
    
    if not time_df.empty:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=time_df['date'],
            y=time_df['fraud_count'],
            mode='lines+markers',
            name='Fraud Count',
            line=dict(color='red', width=2)
        ))
        fig.update_layout(
            title="Daily Fraud Detections",
            xaxis_title="Date",
            yaxis_title="Fraud Count"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No temporal data yet")

st.markdown("---")

# ─────────────────────────────────────────────────────────────
# Recent Transactions Table
# ─────────────────────────────────────────────────────────────

st.subheader("🔍 Recent Transactions")

recent = load_recent_transactions(20)

if not recent.empty:
    # Color code fraud
    def highlight_fraud(row):
        if row['predicted_fraud']:
            return ['background-color: #ffcccc'] * len(row)
        return [''] * len(row)
    
    # Format display
    display_df = recent.copy()
    display_df['fraud_probability'] = display_df['fraud_probability'].round(4)
    display_df['amount'] = display_df['amount'].apply(lambda x: f"${x:,.2f}")
    display_df['transaction_id'] = display_df['transaction_id'].str[:16] + "..."
    
    st.dataframe(
        display_df.style.apply(highlight_fraud, axis=1),
        use_container_width=True,
        height=400
    )
else:
    st.info("No transactions yet. Start the real-time predictor!")

# ─────────────────────────────────────────────────────────────
# Fraud Alerts
# ─────────────────────────────────────────────────────────────

st.markdown("---")
st.subheader("🚨 Recent Fraud Alerts")

fraud_alerts = recent[recent['predicted_fraud'] == True]

if not fraud_alerts.empty:
    for _, alert in fraud_alerts.head(5).iterrows():
        with st.expander(f"⚠️ Alert: {alert['transaction_id'][:16]}... - ${alert['amount']}"):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Time:** {alert['timestamp']}")
                st.write(f"**Category:** {alert['category']}")
            with col2:
                st.write(f"**Fraud Probability:** {alert['fraud_probability']:.4f}")
                st.write(f"**Status:** 🚨 FRAUD DETECTED")
else:
    st.success("✅ No fraud detected in recent transactions")

# ─────────────────────────────────────────────────────────────
# Footer
# ─────────────────────────────────────────────────────────────

st.markdown("---")
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Fraud Detection System v1.0")
