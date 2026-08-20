import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
import plotly.express as px
import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

from src.data_loader import load_dataset
from src.risk_scoring import compute_risk
from src.ui.components import RISK_COLORS, RISK_ORDER, explanation_card, kpi_row, plotly_dark_layout
from src.ui.theme import apply_theme, render_marquee

st.set_page_config(page_title="Banking Risk Dashboard", layout="wide")
apply_theme()
render_marquee()

st.title("Banking Risk Dashboard")
st.caption("Risk scores, anomaly signals, and customer/account risk segmentation — with explainable reasoning per transaction.")


@st.cache_data(show_spinner="Scoring transactions (rules + Isolation Forest)...")
def get_scored_transactions() -> pd.DataFrame:
    transactions = load_dataset("transactions")
    customers = load_dataset("customers")
    accounts = load_dataset("accounts")
    return compute_risk(transactions, customers, accounts)


scored = get_scored_transactions()

# ---------------------------------------------------------------------------
# KPI row
# ---------------------------------------------------------------------------
total_txns = len(scored)
high_critical_pct = scored["risk_bucket"].isin(["High Risk", "Critical Risk"]).mean() * 100
avg_score = scored["final_score"].mean()
flagged_customers = scored.loc[scored["risk_bucket"].isin(["High Risk", "Critical Risk"]), "customer_id"].nunique()

kpi_row(
    [
        ("Transactions Scored", f"{total_txns:,}"),
        ("High + Critical Risk", f"{high_critical_pct:.1f}%"),
        ("Average Risk Score", f"{avg_score:.1f}/100"),
        ("Flagged Customers", f"{flagged_customers:,}"),
    ]
)

st.divider()

# ---------------------------------------------------------------------------
# Risk distribution + segmentation
# ---------------------------------------------------------------------------
col1, col2 = st.columns(2)

with col1:
    st.subheader("Risk Distribution")
    dist = scored["risk_bucket"].value_counts().reindex(RISK_ORDER).fillna(0).reset_index()
    dist.columns = ["risk_bucket", "count"]
    fig = px.bar(
        dist,
        x="risk_bucket",
        y="count",
        color="risk_bucket",
        color_discrete_map=RISK_COLORS,
        text="count",
        category_orders={"risk_bucket": RISK_ORDER},
    )
    fig.update_traces(textposition="outside", showlegend=False)
    fig.update_layout(xaxis_title=None, yaxis_title="Transactions")
    plotly_dark_layout(fig)
    st.plotly_chart(fig, width='stretch')

with col2:
    st.subheader("Risk by Customer Segment")
    heat = (
        scored.groupby(["segment", "risk_bucket"]).size().reset_index(name="count")
        .pivot(index="segment", columns="risk_bucket", values="count")
        .reindex(columns=RISK_ORDER)
        .fillna(0)
    )
    fig2 = px.imshow(
        heat,
        text_auto=True,
        color_continuous_scale=["#0a1630", "#256abf", "#9ec5f4", "#cde2fb"],
        aspect="auto",
    )
    fig2.update_layout(xaxis_title=None, yaxis_title=None)
    plotly_dark_layout(fig2)
    st.plotly_chart(fig2, width='stretch')

st.divider()

# ---------------------------------------------------------------------------
# Customer risk segmentation scatter
# ---------------------------------------------------------------------------
st.subheader("Customer Risk Segmentation")
cust_agg = (
    scored.groupby("customer_id")
    .agg(txn_count=("transaction_id", "count"), avg_score=("final_score", "mean"), total_volume=("amount", lambda s: s.abs().sum()))
    .reset_index()
)
cust_agg["dominant_bucket"] = cust_agg["avg_score"].apply(
    lambda s: "Critical Risk" if s > 80 else "High Risk" if s > 60 else "Medium Risk" if s > 30 else "Low Risk"
)
fig3 = px.scatter(
    cust_agg,
    x="txn_count",
    y="avg_score",
    size="total_volume",
    color="dominant_bucket",
    color_discrete_map=RISK_COLORS,
    category_orders={"dominant_bucket": RISK_ORDER},
    hover_data={"customer_id": True, "total_volume": ":,.0f"},
    labels={"txn_count": "Transaction Count", "avg_score": "Average Risk Score"},
)
plotly_dark_layout(fig3, legend_title_text="Risk Bucket")
st.plotly_chart(fig3, width='stretch')

st.divider()

# ---------------------------------------------------------------------------
# Top-risk transactions table with drill-down explanation
# ---------------------------------------------------------------------------
st.subheader("Top-Risk Transactions")

bucket_filter = st.multiselect("Filter by risk bucket", RISK_ORDER, default=["Critical Risk", "High Risk", "Medium Risk"])
top_n = st.slider("Rows to show", min_value=25, max_value=500, value=100, step=25)

table_df = (
    scored[scored["risk_bucket"].isin(bucket_filter)]
    .nlargest(top_n, "final_score")[
        ["transaction_id", "customer_id", "account_id", "amount", "currency", "final_score", "risk_bucket", "recommendation"]
    ]
    .round({"final_score": 1})
)

gb = GridOptionsBuilder.from_dataframe(table_df)
gb.configure_selection(selection_mode="single", use_checkbox=False)
gb.configure_default_column(sortable=True, filter=True, resizable=True)
grid_response = AgGrid(
    table_df,
    gridOptions=gb.build(),
    update_mode=GridUpdateMode.SELECTION_CHANGED,
    theme="alpine-dark",
    fit_columns_on_grid_load=True,
    height=350,
)

selected = grid_response.get("selected_rows")
if selected is not None and len(selected) > 0:
    if isinstance(selected, pd.DataFrame):
        selected_txn_id = selected.iloc[0]["transaction_id"]
    else:
        selected_txn_id = selected[0]["transaction_id"]
    row = scored[scored["transaction_id"] == selected_txn_id].iloc[0]
    st.markdown(f"#### Explanation — {selected_txn_id}")
    explanation_card(row)
else:
    st.caption("Select a row above to see its explainable risk breakdown.")
