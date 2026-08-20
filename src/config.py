"""Central paths, seeds, and risk-model configuration."""

from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data" / "raw"

RANDOM_SEED = 42

DATASET_SIZES = {
    "customers": 10_000,
    "accounts": 15_000,
    "transactions": 25_000,
    "production_incidents": 10_000,
    "api_logs": 15_000,
    "application_logs": 20_000,
    "test_cases": 5_000,
}

DATA_FILES = {
    "customers": DATA_DIR / "customers.csv",
    "accounts": DATA_DIR / "accounts.csv",
    "transactions": DATA_DIR / "transactions.csv",
    "production_incidents": DATA_DIR / "production_incidents.csv",
    "api_logs": DATA_DIR / "api_logs.csv",
    "application_logs": DATA_DIR / "application_logs.csv",
    "test_cases": DATA_DIR / "test_cases.csv",
    "reference_data": DATA_DIR / "reference_data.csv",
}

# Rule-engine weights (sum to 100), matching CLAUDE.md's Risk Scoring Framework.
RULE_WEIGHTS = {
    "kyc_risk": 20,
    "closed_or_blocked_account": 20,
    "high_amount": 15,
    "behavioural_anomaly": 15,
    "fraud_signal": 15,
    "governance_violation": 15,
}

# Final score blend: rule engine vs. Isolation Forest anomaly score.
RULE_WEIGHT_IN_BLEND = 0.7
ANOMALY_WEIGHT_IN_BLEND = 0.3

RISK_BUCKETS = [
    (0, 30, "Low Risk"),
    (31, 60, "Medium Risk"),
    (61, 80, "High Risk"),
    (81, 100, "Critical Risk"),
]

HIGH_AMOUNT_PERCENTILE = 0.97
VALID_CURRENCIES = {"INR", "USD", "EUR", "GBP"}
