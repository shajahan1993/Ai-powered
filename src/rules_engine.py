"""Rule-based checks for banking transactions.

Each rule returns per-transaction points and a human-readable reason. Points
are additive up to the weight in src.config.RULE_WEIGHTS. Pure pandas/numpy —
no Streamlit dependency, so it can be unit-tested or reused by other pages.
"""

import numpy as np
import pandas as pd

from src.config import HIGH_AMOUNT_PERCENTILE, RULE_WEIGHTS, VALID_CURRENCIES


def _enrich(transactions: pd.DataFrame, customers: pd.DataFrame, accounts: pd.DataFrame) -> pd.DataFrame:
    customers_dedup = customers.drop_duplicates(subset="customer_id", keep="first")
    df = transactions.merge(
        customers_dedup[["customer_id", "kyc_status", "kyc_expiry_date", "risk_flag", "segment"]],
        on="customer_id",
        how="left",
        suffixes=("", "_cust"),
    )
    df = df.merge(
        accounts[["account_id", "status"]].rename(columns={"status": "account_status"}),
        on="account_id",
        how="left",
    )
    return df


def apply_rules(transactions: pd.DataFrame, customers: pd.DataFrame, accounts: pd.DataFrame) -> pd.DataFrame:
    """Returns the input transactions with rule_points, rule_reasons, rule_hits columns added."""
    df = _enrich(transactions, customers, accounts)
    n = len(df)

    # Points are tracked per rule-category so multiple sub-rules firing within
    # the same category (e.g. two governance violations) don't exceed that
    # category's configured weight.
    category_points = {key: np.zeros(n) for key in RULE_WEIGHTS}
    reasons = [[] for _ in range(n)]
    hits = [[] for _ in range(n)]

    def add(mask, weight_key, reason_text):
        w = RULE_WEIGHTS[weight_key]
        idx = np.where(mask.fillna(False).to_numpy())[0]
        category_points[weight_key][idx] = w
        for i in idx:
            reasons[i].append(reason_text)
            hits[i].append(weight_key)

    # KYC risk
    add(df["kyc_status"].isin(["rejected", "expired"]), "kyc_risk", "Rejected/expired KYC")
    add(df["kyc_status"].isna(), "kyc_risk", "Customer record not found for KYC check")

    # Closed / blocked / dormant account
    add(df["account_status"].isin(["closed", "blocked"]), "closed_or_blocked_account", "Transaction on closed/blocked account")
    add(df["account_status"] == "dormant", "closed_or_blocked_account", "Transaction on dormant account")

    # High transaction amount (percentile-based, computed on positive amounts only)
    positive_amounts = df.loc[df["amount"] > 0, "amount"]
    threshold = positive_amounts.quantile(HIGH_AMOUNT_PERCENTILE) if len(positive_amounts) else np.inf
    add(df["amount"] > threshold, "high_amount", f"High-value transaction (> {threshold:,.0f})")

    # Behavioural anomaly: customer transacting far more frequently than their own norm
    txn_counts = df.groupby("customer_id")["transaction_id"].transform("count")
    freq_threshold = txn_counts.quantile(0.98)
    add(txn_counts > freq_threshold, "behavioural_anomaly", "Unusually high transaction frequency for this customer")

    # Fraud signals: duplicate transaction id, missing/invalid beneficiary, negative amount
    dup_mask = df["transaction_id"].duplicated(keep=False)
    add(dup_mask, "fraud_signal", "Duplicate transaction ID")
    add(df["beneficiary_id"].isna() | (df["beneficiary_id"].astype(str).str.strip() == ""), "fraud_signal", "Missing/invalid beneficiary")
    add(df["amount"] < 0, "fraud_signal", "Negative transaction amount")

    # Governance / data-quality violations
    add(~df["currency"].isin(VALID_CURRENCIES), "governance_violation", "Invalid currency code")
    add(df["timestamp"] > pd.Timestamp.now(), "governance_violation", "Future-dated transaction")
    add(df["customer_id"].isna() | (df["customer_id"].astype(str).str.strip() == ""), "governance_violation", "Missing customer ID")

    total_points = sum(category_points.values())
    df["rule_points"] = np.clip(total_points, 0, 100)
    df["rule_reasons"] = reasons
    df["rule_hits"] = hits
    return df
