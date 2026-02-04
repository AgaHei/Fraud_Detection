# Data Directory

This directory should contain the following files for the fraud detection system to work:

## Required Files

### `fraudTest.csv`
- **Description**: Main dataset for fraud detection analysis
- **Size**: ~143 MB (555,719 transactions)
- **Source**: Simulated credit card transactions dataset
- **Columns**: 23 features including transaction details, customer info, and fraud labels
- **Download**: You need to obtain this dataset separately due to GitHub size limits

### `api_test_set.csv`
- **Description**: Subset of data used for API simulation and real-time testing
- **Size**: ~113 MB (444,575 transactions)  
- **Source**: Generated from fraudTest.csv using `src/prepare_api_data.py`
- **Usage**: Used by `src/mock_transaction_api.py` for simulating real-time transactions

## Setup Instructions

1. **Obtain the main dataset**: Place `fraudTest.csv` in this directory
2. **Generate API test data**: Run `python src/prepare_api_data.py` to create `api_test_set.csv`
3. **Verify data structure**: Both files should have the same 23 columns as defined in the notebooks

## Alternative Data Sources

If you don't have access to the original dataset, you can:
- Use any similar credit card transaction dataset with fraud labels
- Modify the column mappings in the source code to match your dataset
- Generate synthetic transaction data for testing purposes

## File Structure Expected

```
data/
├── README.md          # This file
├── fraudTest.csv      # Main dataset (not included due to size)
└── api_test_set.csv   # API test data (generated from fraudTest.csv)
```

## Notes

- These files are excluded from git tracking due to their large size (>100MB GitHub limit)
- The model training notebooks expect the exact column structure from fraudTest.csv
- For production deployment, consider using a database instead of CSV files