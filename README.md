# 🛡️ Automatic Fraud Detection System

A comprehensive real-time fraud detection system built with machine learning, featuring transaction monitoring, risk assessment, and automated alerting capabilities.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-1.7+-orange.svg)](https://scikit-learn.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13+-blue.svg)](https://postgresql.org)
[![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)](https://flask.palletsprojects.com)


## 🎯 Project Overview

This fraud detection system analyzes financial transactions in real-time to identify potentially fraudulent activities. The system combines advanced machine learning techniques with comprehensive feature engineering to achieve high accuracy while minimizing false positives.

### Key Capabilities:
- **Real-time Transaction Monitoring**: Continuous analysis of incoming transactions
- **Advanced Feature Engineering**: Customer-specific behavioral analysis and anomaly detection
- **Risk Scoring**: Probabilistic fraud assessment with configurable thresholds
- **Database Integration**: Persistent storage of predictions and transaction history
- **Automated Reporting**: Comprehensive fraud analytics and reporting
- **API Integration**: RESTful API for transaction processing

## ✨ Features

### 🔍 **Data Analysis & Engineering**
- **Comprehensive EDA**: In-depth exploratory data analysis with interactive visualizations
- **Customer-Specific Features**: Behavioral pattern analysis per customer
- **Geographic Analysis**: Distance-based fraud detection using Haversine calculations
- **Temporal Patterns**: Time-based fraud indicators and cyclical encoding
- **Amount Analysis**: Transaction value patterns and anomaly detection

### 🤖 **Machine Learning Pipeline**
- **Feature Selection**: Multi-criteria feature ranking (F-score, mutual information, correlation)
- **Model Training**: Random Forest classifier with hyperparameter optimization
- **Cross-Validation**: Robust model evaluation with stratified sampling
- **Imbalanced Data Handling**: Techniques for dealing with rare fraud cases

### 🔄 **Real-Time Processing**
- **Live Monitoring**: Continuous transaction analysis with configurable polling intervals
- **Risk Assessment**: Real-time fraud probability scoring
- **Database Logging**: Persistent storage of all predictions and outcomes
- **Alert System**: Automated notifications for high-risk transactions

### 📊 **Reporting & Analytics**
- **Performance Metrics**: Comprehensive model performance tracking
- **Fraud Statistics**: Detailed analytics on detected fraud patterns
- **Historical Analysis**: Trend analysis and pattern identification
- **Custom Reports**: Automated report generation with key insights

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Mock API      │    │   Real-time      │    │   PostgreSQL    │
│   (Flask)       │◄──►│   Predictor      │◄──►│   Database      │
│                 │    │   (ML Pipeline)  │    │   (Neon)        │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                        │                        │
         │                        │                        │
         ▼                        ▼                        ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Test Data     │    │   Trained Model  │    │   Reports &     │
│   Generation    │    │   (Joblib)       │    │   Analytics     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### Components:
1. **Data Pipeline**: ETL processes for feature engineering and model training
2. **ML Pipeline**: Trained Random Forest model with preprocessing pipeline
3. **API Layer**: Mock transaction API for testing and simulation
4. **Prediction Engine**: Real-time fraud detection with configurable thresholds
5. **Database Layer**: PostgreSQL for persistent storage and analytics
6. **Reporting Layer**: Automated report generation and performance monitoring



## 📁 Project Structure

```
   Project Automatic Fraud Detection/
   ├──📁 notebooks/
   │   ├── 📊 01_EDA_for_fraud_detection.ipynb    # Exploratory Data Analysis
   │   ├── 🔧 02_Feature_Engineering.ipynb        # Feature Engineering & Model Training
   ├── 📋 README.md                          # This file
   ├── 📦 requirements.txt                   # Python dependencies
   ├── 🔒 .env                              # Environment variables (create this)
   ├── 🔒 .gitignore                        # Git ignore rules
   │
   ├── 📁 config/
   │   ├── __init__.py
   │   └── config.py                        # Configuration settings
   │
   ├── 📁 src/
   │   ├── mock_transaction_api.py          # Mock API for testing
   │   ├── real_time_predictor.py           # Main fraud detection engine
   │   ├── prepare_api_data.py              # Data preparation utilities
   │   └── generate_demo_report.py          # Reporting system
   │
   ├── 📁 models/
   │   └── fraud_detection_pipeline.joblib   # Trained ML model (generated)
   │
   ── 📁 data/
   │   ├── fraudTest.csv                    # Main dataset
   │   └── api_test_set.csv                 # API simulation data (generated)
   │
   └── 📁 logs/
    ├── api.log                          # API logs
    ├── predictor.log                    # Prediction logs
    └── demo_report_*.txt                # Generated reports
```



## 📈 Model Performance

### Key Metrics
- **Accuracy**: ~99.5% (typical for highly imbalanced dataset)
- **Precision**: ~85% (fraud predictions that are actually fraud)
- **Recall**: ~78% (actual fraud cases detected)
- **F1-Score**: ~81% (balanced precision/recall metric)
- **AUC-ROC**: ~0.92 (excellent discrimination ability)


### Class Imbalance Handling
- **Original Distribution**: 99.61% legitimate, 0.39% fraud
- **Techniques Used**: 
  - Stratified sampling for train/test splits
  - Class weight balancing in Random Forest
  - Precision-recall optimization
  - Custom threshold tuning (0.4 instead of 0.5)

## 🛠️ Technologies Used

### Core Technologies
- **Python 3.8+**: Primary programming language
- **Scikit-Learn**: Machine learning framework
- **Pandas**: Data manipulation and analysis
- **NumPy**: Numerical computing

### Web & API
- **Flask**: Web framework for mock API
- **Requests**: HTTP client for API interactions

### Database
- **PostgreSQL**: Primary database (Neon.tech)
- **psycopg2**: PostgreSQL adapter for Python

### Visualization & Analysis
- **Matplotlib**: Static plotting library
- **Seaborn**: Statistical data visualization
- **Plotly**: Interactive visualizations
- **Jupyter**: Interactive development environment

### DevOps & Utilities
- **python-dotenv**: Environment variable management
- **joblib**: Model serialization
- **logging**: Application logging

## 📝 Development Notes

### Key Design Decisions

1. **Customer-Specific Features**: Instead of global statistics, we calculate behavioral patterns per customer, dramatically improving fraud detection accuracy.

2. **Real-time Architecture**: Polling-based system for simplicity and reliability, easily scalable to streaming architectures.

3. **Configurable Thresholds**: Fraud threshold (0.4) tuned for business requirements balancing false positives vs detection rate.

4. **Comprehensive Logging**: All transactions and predictions logged for audit trails and model improvement.

### Performance Considerations

- **Database Connection Pooling**: Efficient database connections for high-throughput scenarios
- **Model Caching**: Trained model loaded once and reused for all predictions
- **Batch Processing**: Future enhancement for processing multiple transactions simultaneously

### Security Features

- **Environment Variables**: Sensitive credentials stored securely
- **Database Security**: Parameterized queries preventing SQL injection
- **Audit Trail**: Complete transaction history with timestamps

## 🔮 Future Enhancements

### Near-term (Next 3-6 months)
- [ ] **Streaming Architecture**: Apache Kafka integration for real-time data streams
- [ ] **Model Retraining**: Automated periodic model updates with new data
- [ ] **Web Dashboard**: Real-time fraud monitoring dashboard
- [ ] **Alert System**: Email/SMS notifications for high-risk transactions
- [ ] **A/B Testing**: Multiple model comparison framework

### Medium-term (6-12 months)
- [ ] **Deep Learning Models**: Neural network architectures for complex pattern detection
- [ ] **Ensemble Methods**: Combining multiple algorithms for improved accuracy
- [ ] **Feature Store**: Centralized feature management and versioning
- [ ] **Model Explainability**: SHAP/LIME integration for prediction explanations
- [ ] **Mobile API**: Mobile app integration for fraud notifications

### Long-term (12+ months)
- [ ] **Graph Neural Networks**: Network analysis for fraud ring detection
- [ ] **Reinforcement Learning**: Adaptive thresholds based on feedback
- [ ] **Multi-modal Analysis**: Image and text data integration
- [ ] **Federated Learning**: Privacy-preserving collaborative model training
- [ ] **Cloud Deployment**: AWS/GCP production deployment with auto-scaling

### Technical Debt & Improvements
- [ ] **Unit Testing**: Comprehensive test suite with pytest
- [ ] **CI/CD Pipeline**: Automated testing and deployment
- [ ] **API Rate Limiting**: Production-ready API with rate limiting
- [ ] **Configuration Management**: Advanced configuration with Hydra
- [ ] **Monitoring & Observability**: Prometheus/Grafana integration




## 👤 Author

**Agnès Heijligers** - for Jedha AI Architect Certification  
Exam Date: March 17th, 2026

---

## 📄 License

This project is for educational purposes of Data Science and Engineering Lead Bootcamp at Jedha in Paris (AI Architect certification).

---

## 🙏 Acknowledgments

- Jedha Bootcamp for the project requirements
- Neon for free PostgreSQL hosting
- Claude (Anthropic) for development assistance


## 🎯 Project Status

**Current Version**: 1.0.0
**Status**: Production Ready (with monitoring)
**Last Updated**: February 2026

---

**Key Focus:** Data pipeline and MLOps infrastructure (not just the ML model)