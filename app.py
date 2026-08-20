import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import streamlit as st

from src.config import DATASET_SIZES
from src.data_loader import dataset_counts
from src.ui.components import kpi_row
from src.ui.theme import apply_theme, render_marquee

st.set_page_config(
    page_title="AI Powered Banking Risk Application",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_theme()
render_marquee()

st.title("AI Powered Banking Risk & Incident Monitoring")
st.caption(
    "Explainable AI insights for fraud risk, operational failures, SLA breaches, "
    "data-quality issues, and governance — with human-in-the-loop review."
)

st.subheader("Dataset Overview")
counts = dataset_counts()
kpi_row(
    [
        ("Customers", f"{counts['customers']:,}"),
        ("Accounts", f"{counts['accounts']:,}"),
        ("Transactions", f"{counts['transactions']:,}"),
        ("Production Incidents", f"{counts['production_incidents']:,}"),
    ]
)
kpi_row(
    [
        ("API Logs", f"{counts['api_logs']:,}"),
        ("Application Logs", f"{counts['application_logs']:,}"),
        ("Test Cases", f"{counts['test_cases']:,}"),
        ("Reference Records", f"{counts['reference_data']:,}"),
    ]
)

st.divider()
st.markdown(
    """
    ### Workflow
    Banking Data → Data Validation → Feature Engineering → Rule Engine + AI Anomaly Detection
    → Risk Scoring → Incident Intelligence → AI Insights → Recommendations → Human Review → Final Decision

    **AI Detects and Recommends. Human Reviews. Human Makes Final Banking Decision.**
    """
)

st.info("Use the sidebar to navigate to the **Banking Risk Dashboard**.", icon="ℹ️")
