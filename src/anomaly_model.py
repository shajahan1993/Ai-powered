"""Isolation Forest anomaly scoring for transactions."""

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest

from src.config import RANDOM_SEED

FEATURE_COLUMNS = ["amount_abs", "customer_amount_zscore", "account_tenure_days", "customer_txn_velocity"]

ISOLATION_FOREST_PARAMS = {
    "n_estimators": 150,
    "contamination": 0.05,
    "random_state": RANDOM_SEED,
}


def build_features(df: pd.DataFrame, accounts: pd.DataFrame) -> pd.DataFrame:
    features = pd.DataFrame(index=df.index)
    features["amount_abs"] = df["amount"].abs()

    cust_mean = df.groupby("customer_id")["amount"].transform("mean")
    cust_std = df.groupby("customer_id")["amount"].transform("std").replace(0, np.nan)
    features["customer_amount_zscore"] = ((df["amount"] - cust_mean) / cust_std).fillna(0)

    acc_open = accounts.set_index("account_id")["open_date"]
    open_dates = df["account_id"].map(acc_open)
    tenure = (df["timestamp"] - open_dates).dt.days
    features["account_tenure_days"] = tenure.fillna(tenure.median()).clip(lower=0)

    features["customer_txn_velocity"] = df.groupby("customer_id")["transaction_id"].transform("count")

    return features.fillna(0)


def score_anomalies(df: pd.DataFrame, accounts: pd.DataFrame) -> pd.Series:
    """Returns a 0-100 anomaly score per row (higher = more anomalous)."""
    features = build_features(df, accounts)

    model = IsolationForest(**ISOLATION_FOREST_PARAMS)
    model.fit(features[FEATURE_COLUMNS])
    raw_scores = model.decision_function(features[FEATURE_COLUMNS])  # higher = more normal

    inverted = -raw_scores  # higher = more anomalous
    min_v, max_v = inverted.min(), inverted.max()
    if max_v - min_v < 1e-9:
        scaled = np.zeros_like(inverted)
    else:
        scaled = (inverted - min_v) / (max_v - min_v) * 100

    return pd.Series(scaled, index=df.index, name="anomaly_score")
