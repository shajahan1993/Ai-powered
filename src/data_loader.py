"""Cached CSV loaders for all datasets."""

import pandas as pd
import streamlit as st

from src.config import DATA_FILES

DATE_COLUMNS = {
    "customers": ["dob", "onboarding_date", "kyc_expiry_date"],
    "accounts": ["open_date"],
    "transactions": ["timestamp"],
    "production_incidents": ["opened_at", "resolved_at"],
    "api_logs": ["timestamp"],
    "application_logs": ["timestamp"],
    "test_cases": ["executed_at"],
}


@st.cache_data(show_spinner=False)
def load_dataset(name: str) -> pd.DataFrame:
    path = DATA_FILES[name]
    df = pd.read_csv(path)
    for col in DATE_COLUMNS.get(name, []):
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
    return df


@st.cache_data(show_spinner=False)
def load_all() -> dict:
    return {name: load_dataset(name) for name in DATA_FILES}


@st.cache_data(show_spinner=False)
def dataset_counts() -> dict:
    return {name: len(load_dataset(name)) for name in DATA_FILES}
