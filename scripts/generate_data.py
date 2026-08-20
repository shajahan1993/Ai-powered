"""Generates synthetic banking + operational datasets into data/raw/.

Idempotent (fixed seed). Intentionally injects the anomaly scenarios listed
in CLAUDE.md so the risk engine and dashboards have real signal to detect.
Run: python scripts/generate_data.py
"""

import sys
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
from faker import Faker

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.config import DATA_DIR, DATASET_SIZES, RANDOM_SEED  # noqa: E402

rng = np.random.default_rng(RANDOM_SEED)
fake = Faker()
Faker.seed(RANDOM_SEED)

NOW = datetime(2026, 8, 20)


def _dates_between(start_days_ago, end_days_ago, n):
    start = NOW - timedelta(days=start_days_ago)
    end = NOW - timedelta(days=end_days_ago)
    span = (end - start).total_seconds()
    offsets = rng.uniform(0, span, size=n)
    return [start + timedelta(seconds=float(s)) for s in offsets]


def generate_customers(n):
    kyc_status = rng.choice(
        ["verified", "pending", "rejected", "expired"],
        size=n,
        p=[0.82, 0.08, 0.05, 0.05],
    )
    segment = rng.choice(["retail", "premium", "sme", "corporate"], size=n, p=[0.55, 0.2, 0.18, 0.07])
    customer_ids = [f"CUST{100000 + i}" for i in range(n)]

    onboarding_dates = _dates_between(3650, 1, n)
    # Inject: ~0.5% future onboarding dates
    future_idx = rng.choice(n, size=max(1, int(n * 0.005)), replace=False)
    for i in future_idx:
        onboarding_dates[i] = NOW + timedelta(days=int(rng.integers(1, 90)))

    df = pd.DataFrame(
        {
            "customer_id": customer_ids,
            "name": [fake.name() for _ in range(n)],
            "dob": [fake.date_of_birth(minimum_age=18, maximum_age=85) for _ in range(n)],
            "onboarding_date": onboarding_dates,
            "kyc_status": kyc_status,
            "kyc_expiry_date": [
                d + timedelta(days=int(rng.integers(-200, 900))) for d in onboarding_dates
            ],
            "risk_flag": rng.choice(["none", "watchlist", "pep"], size=n, p=[0.94, 0.05, 0.01]),
            "segment": segment,
        }
    )

    # Inject: ~0.3% duplicate customer records (same customer_id appears twice with drift)
    dup_idx = rng.choice(n, size=max(1, int(n * 0.003)), replace=False)
    dup_rows = df.iloc[dup_idx].copy()
    df = pd.concat([df, dup_rows], ignore_index=True)

    return df


def generate_accounts(n, customer_ids):
    status = rng.choice(
        ["active", "closed", "dormant", "blocked"],
        size=n,
        p=[0.78, 0.1, 0.08, 0.04],
    )
    account_type = rng.choice(["savings", "current", "loan", "nri"], size=n, p=[0.55, 0.3, 0.1, 0.05])
    open_dates = _dates_between(3650, 5, n)

    # Most accounts map to a real customer; inject ~1% invalid customer references.
    owners = rng.choice(customer_ids, size=n)
    invalid_idx = rng.choice(n, size=max(1, int(n * 0.01)), replace=False)
    for i in invalid_idx:
        owners[i] = f"CUST{999000 + int(rng.integers(0, 999))}"  # not present in customers table

    df = pd.DataFrame(
        {
            "account_id": [f"ACC{200000 + i}" for i in range(n)],
            "customer_id": owners,
            "account_type": account_type,
            "status": status,
            "open_date": open_dates,
            "balance": np.round(rng.gamma(shape=2.0, scale=45000, size=n), 2),
        }
    )
    return df


def generate_transactions(n, accounts_df, customers_df):
    acc_ids = accounts_df["account_id"].values
    acc_lookup = accounts_df.set_index("account_id")[["customer_id", "status"]]

    chosen_accounts = rng.choice(acc_ids, size=n)
    amounts = np.round(rng.lognormal(mean=8.5, sigma=1.1, size=n), 2)  # ~ realistic skew, INR-scale

    # Inject: ~1% very high-value outliers
    hi_idx = rng.choice(n, size=max(1, int(n * 0.01)), replace=False)
    amounts[hi_idx] = np.round(rng.uniform(500_000, 2_000_000, size=len(hi_idx)), 2)

    # Inject: ~0.3% negative amounts (data-quality issue)
    neg_idx = rng.choice(n, size=max(1, int(n * 0.003)), replace=False)
    amounts[neg_idx] = -np.abs(amounts[neg_idx])

    currencies = rng.choice(["INR", "USD", "EUR", "GBP"], size=n, p=[0.85, 0.08, 0.04, 0.03])
    # Inject: ~0.5% invalid currency codes
    bad_ccy_idx = rng.choice(n, size=max(1, int(n * 0.005)), replace=False)
    currencies = currencies.astype(object)
    for i in bad_ccy_idx:
        currencies[i] = rng.choice(["XXX", "ZZZ", "N/A"])

    timestamps = _dates_between(365, 0, n)
    # Inject: ~0.5% future-dated transactions
    future_idx = rng.choice(n, size=max(1, int(n * 0.005)), replace=False)
    for i in future_idx:
        timestamps[i] = NOW + timedelta(days=int(rng.integers(1, 30)))

    customer_ids_for_txn = acc_lookup.loc[chosen_accounts, "customer_id"].values

    channel = rng.choice(["mobile", "web", "branch", "atm", "api"], size=n, p=[0.4, 0.25, 0.15, 0.1, 0.1])
    beneficiary_ids = [f"BENE{int(b)}" for b in rng.integers(1, 50000, size=n)]
    # Inject: ~0.4% invalid/missing beneficiary
    bad_bene_idx = rng.choice(n, size=max(1, int(n * 0.004)), replace=False)
    for i in bad_bene_idx:
        beneficiary_ids[i] = ""

    txn_ids = [f"TXN{300000 + i}" for i in range(n)]

    df = pd.DataFrame(
        {
            "transaction_id": txn_ids,
            "account_id": chosen_accounts,
            "customer_id": customer_ids_for_txn,
            "amount": amounts,
            "currency": currencies,
            "timestamp": timestamps,
            "beneficiary_id": beneficiary_ids,
            "channel": channel,
        }
    )

    # Inject: ~0.5% duplicate transaction_ids (same id reused on a different row)
    dup_idx = rng.choice(n, size=max(1, int(n * 0.005)), replace=False)
    dup_rows = df.iloc[dup_idx].copy()
    df = pd.concat([df, dup_rows], ignore_index=True)

    # Bias a slice of transactions onto closed/dormant/blocked accounts to create
    # realistic "closed account activity" risk cases beyond what random draw gives.
    risky_status_accounts = accounts_df[accounts_df["status"].isin(["closed", "dormant", "blocked"])]
    if len(risky_status_accounts) > 0:
        boost_n = max(1, int(len(df) * 0.02))
        boost_idx = rng.choice(len(df), size=boost_n, replace=False)
        boost_accounts = rng.choice(risky_status_accounts["account_id"].values, size=boost_n)
        df.loc[boost_idx, "account_id"] = boost_accounts
        df.loc[boost_idx, "customer_id"] = acc_lookup.loc[boost_accounts, "customer_id"].values

    return df.reset_index(drop=True)


def generate_production_incidents(n):
    severity = rng.choice(["SEV1", "SEV2", "SEV3", "SEV4"], size=n, p=[0.05, 0.15, 0.4, 0.4])
    services = rng.choice(
        ["payments-api", "core-banking", "kyc-service", "notification-svc", "auth-service", "ledger-svc"],
        size=n,
    )
    opened = _dates_between(365, 0, n)

    sla_target_hours = {"SEV1": 2, "SEV2": 8, "SEV3": 24, "SEV4": 72}
    resolved = []
    sla_breached = []
    for i in range(n):
        target = sla_target_hours[severity[i]]
        # ~30% breach their SLA target
        breach = rng.random() < 0.3
        actual_hours = rng.uniform(target * 1.2, target * 3) if breach else rng.uniform(0.2, target * 0.9)
        resolved.append(opened[i] + timedelta(hours=float(actual_hours)))
        sla_breached.append(breach)

    df = pd.DataFrame(
        {
            "incident_id": [f"INC{400000 + i}" for i in range(n)],
            "service": services,
            "severity": severity,
            "opened_at": opened,
            "resolved_at": resolved,
            "sla_breached": sla_breached,
            "rca_present": rng.choice([True, False], size=n, p=[0.75, 0.25]),
            "owner_team": rng.choice(["platform", "payments", "core-banking", "security", "sre"], size=n),
        }
    )
    return df


def generate_api_logs(n, incident_ids):
    endpoints = rng.choice(
        ["/api/transfer", "/api/balance", "/api/kyc/verify", "/api/login", "/api/statement", "/api/beneficiary"],
        size=n,
    )
    status_pool = [200, 201, 400, 401, 429, 500, 502, 503, 504]
    status_probs = [0.82, 0.03, 0.03, 0.02, 0.02, 0.03, 0.02, 0.02, 0.01]
    status_codes = rng.choice(status_pool, size=n, p=status_probs)

    response_time = rng.gamma(shape=2.0, scale=150, size=n)
    # Inject: slow API tail (>3000ms)
    slow_idx = rng.choice(n, size=max(1, int(n * 0.02)), replace=False)
    response_time[slow_idx] = rng.uniform(3000, 9000, size=len(slow_idx))

    timestamps = _dates_between(180, 0, n)

    linked_incident = np.full(n, "", dtype=object)
    failure_mask = np.isin(status_codes, [500, 502, 503, 504])
    failure_idx = np.where(failure_mask)[0]
    # Only ~60% of failures get correctly linked to an incident (rest = missing linkage anomaly)
    link_idx = rng.choice(failure_idx, size=int(len(failure_idx) * 0.6), replace=False) if len(failure_idx) else []
    if len(link_idx):
        linked_incident[link_idx] = rng.choice(incident_ids, size=len(link_idx))

    df = pd.DataFrame(
        {
            "request_id": [f"REQ{500000 + i}" for i in range(n)],
            "endpoint": endpoints,
            "response_time_ms": np.round(response_time, 1),
            "status_code": status_codes,
            "timestamp": timestamps,
            "linked_incident_id": linked_incident,
        }
    )
    return df


def generate_application_logs(n, services):
    level = rng.choice(["INFO", "WARN", "ERROR"], size=n, p=[0.75, 0.17, 0.08])
    message_codes = {
        "INFO": ["APP_START", "REQUEST_OK", "CACHE_HIT"],
        "WARN": ["RETRY_ATTEMPT", "CACHE_MISS", "SLOW_QUERY"],
        "ERROR": ["DB_CONN_FAILURE", "AUTH_FAILURE", "NPE", "TIMEOUT", "UPSTREAM_TIMEOUT"],
    }
    codes = [rng.choice(message_codes[lvl]) for lvl in level]
    timestamps = _dates_between(180, 0, n)

    df = pd.DataFrame(
        {
            "log_id": [f"LOG{600000 + i}" for i in range(n)],
            "service": rng.choice(services, size=n),
            "level": level,
            "message_code": codes,
            "timestamp": timestamps,
        }
    )
    return df


def generate_test_cases(n):
    status = rng.choice(["pass", "fail", "blocked"], size=n, p=[0.78, 0.15, 0.07])
    failure_reasons = {
        "fail": ["assertion_failure", "timeout", "data_mismatch", "environment_unavailable", "auth_failure"],
        "blocked": ["environment_unavailable", "dependency_not_ready"],
        "pass": [""],
    }
    reasons = [rng.choice(failure_reasons[s]) for s in status]
    executed = _dates_between(90, 0, n)

    df = pd.DataFrame(
        {
            "test_id": [f"TC{700000 + i}" for i in range(n)],
            "suite": rng.choice(["regression", "smoke", "integration", "performance", "security"], size=n),
            "status": status,
            "failure_reason": reasons,
            "executed_at": executed,
        }
    )
    return df


def generate_reference_data():
    rows = []
    for ccy in ["INR", "USD", "EUR", "GBP"]:
        rows.append({"category": "valid_currency", "value": ccy})
    for st in ["active", "closed", "dormant", "blocked"]:
        rows.append({"category": "valid_account_status", "value": st})
    for code in [200, 201, 400, 401, 429, 500, 502, 503, 504]:
        rows.append({"category": "valid_http_status", "value": str(code)})
    for kyc in ["verified", "pending", "rejected", "expired"]:
        rows.append({"category": "valid_kyc_status", "value": kyc})
    return pd.DataFrame(rows)


def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    customers = generate_customers(DATASET_SIZES["customers"])
    customers.to_csv(DATA_DIR / "customers.csv", index=False)

    accounts = generate_accounts(DATASET_SIZES["accounts"], customers["customer_id"].unique())
    accounts.to_csv(DATA_DIR / "accounts.csv", index=False)

    transactions = generate_transactions(DATASET_SIZES["transactions"], accounts, customers)
    transactions.to_csv(DATA_DIR / "transactions.csv", index=False)

    incidents = generate_production_incidents(DATASET_SIZES["production_incidents"])
    incidents.to_csv(DATA_DIR / "production_incidents.csv", index=False)

    services = incidents["service"].unique()
    api_logs = generate_api_logs(DATASET_SIZES["api_logs"], incidents["incident_id"].values)
    api_logs.to_csv(DATA_DIR / "api_logs.csv", index=False)

    app_logs = generate_application_logs(DATASET_SIZES["application_logs"], services)
    app_logs.to_csv(DATA_DIR / "application_logs.csv", index=False)

    test_cases = generate_test_cases(DATASET_SIZES["test_cases"])
    test_cases.to_csv(DATA_DIR / "test_cases.csv", index=False)

    reference = generate_reference_data()
    reference.to_csv(DATA_DIR / "reference_data.csv", index=False)

    print("Generated datasets into", DATA_DIR)
    for name, df in [
        ("customers", customers),
        ("accounts", accounts),
        ("transactions", transactions),
        ("production_incidents", incidents),
        ("api_logs", api_logs),
        ("application_logs", app_logs),
        ("test_cases", test_cases),
        ("reference_data", reference),
    ]:
        print(f"  {name}: {len(df)} rows")


if __name__ == "__main__":
    main()
