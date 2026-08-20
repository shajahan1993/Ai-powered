"""Blends rule-engine points with Isolation Forest anomaly scores into a
final explainable risk score, matching CLAUDE.md's hybrid risk model."""

import pandas as pd

from src.anomaly_model import score_anomalies
from src.config import ANOMALY_WEIGHT_IN_BLEND, RISK_BUCKETS, RULE_WEIGHT_IN_BLEND
from src.rules_engine import apply_rules


def _bucket_for(score: float) -> str:
    for low, high, label in RISK_BUCKETS:
        if low <= score <= high:
            return label
    return "Critical Risk" if score > RISK_BUCKETS[-1][1] else "Low Risk"


def _recommendation_for(row) -> str:
    hits = row["rule_hits"]
    if not hits and row["anomaly_score"] < 50:
        return "No action required; transaction consistent with normal customer behaviour."
    if "kyc_risk" in hits or "closed_or_blocked_account" in hits:
        return "Prioritize manual investigation and validate customer identity and account status before processing."
    if "fraud_signal" in hits:
        return "Hold transaction pending fraud review; verify beneficiary and transaction uniqueness."
    if "governance_violation" in hits:
        return "Route to data-quality/governance queue for correction before settlement."
    if "behavioural_anomaly" in hits or row["anomaly_score"] >= 70:
        return "Flag for behavioural review; confirm activity with customer if pattern persists."
    return "Monitor; no immediate action required."


def compute_risk(transactions: pd.DataFrame, customers: pd.DataFrame, accounts: pd.DataFrame) -> pd.DataFrame:
    """Returns transactions enriched with rule_points, anomaly_score, final_score,
    risk_bucket, reasons, and recommendation columns."""
    df = apply_rules(transactions, customers, accounts)
    df["anomaly_score"] = score_anomalies(df, accounts)

    df["final_score"] = (
        df["rule_points"] * RULE_WEIGHT_IN_BLEND + df["anomaly_score"] * ANOMALY_WEIGHT_IN_BLEND
    ).clip(0, 100)

    df["risk_bucket"] = df["final_score"].apply(_bucket_for)

    df["reasons"] = df.apply(
        lambda r: r["rule_reasons"] + (["Statistically anomalous transaction pattern"] if r["anomaly_score"] >= 70 else []),
        axis=1,
    )
    df["recommendation"] = df.apply(_recommendation_for, axis=1)

    return df
