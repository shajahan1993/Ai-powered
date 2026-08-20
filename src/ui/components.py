"""Shared widgets used across dashboard pages."""

import streamlit as st

_BADGE_CLASS = {
    "Low Risk": "risk-low",
    "Medium Risk": "risk-medium",
    "High Risk": "risk-high",
    "Critical Risk": "risk-critical",
}

# Status palette (validated against the dark navy surface) — risk buckets are an
# ordered status, not an arbitrary categorical, so these are always paired with
# a visible text label rather than relied on as color-alone.
RISK_COLORS = {
    "Low Risk": "#0ca30c",
    "Medium Risk": "#fab219",
    "High Risk": "#ec835a",
    "Critical Risk": "#d03b3b",
}
RISK_ORDER = ["Low Risk", "Medium Risk", "High Risk", "Critical Risk"]

CHART_SURFACE = "#0a1630"
CHART_TEXT = "#e2e8f0"
CHART_GRID = "#16305e"


def plotly_dark_layout(fig, **kwargs):
    fig.update_layout(
        plot_bgcolor=CHART_SURFACE,
        paper_bgcolor=CHART_SURFACE,
        font_color=CHART_TEXT,
        margin=dict(t=40, l=10, r=10, b=10),
        **kwargs,
    )
    fig.update_xaxes(gridcolor=CHART_GRID, zerolinecolor=CHART_GRID)
    fig.update_yaxes(gridcolor=CHART_GRID, zerolinecolor=CHART_GRID)
    return fig


def risk_badge_html(bucket: str) -> str:
    cls = _BADGE_CLASS.get(bucket, "risk-low")
    return f'<span class="risk-badge {cls}">{bucket}</span>'


def kpi_row(items: list[tuple[str, str]]):
    """items: list of (label, value) pairs rendered as st.metric tiles."""
    cols = st.columns(len(items))
    for col, (label, value) in zip(cols, items):
        col.metric(label, value)


def explanation_card(row):
    reasons = row.get("reasons", [])
    reasons_html = "".join(f"<li>{r}</li>" for r in reasons) if reasons else "<li>No rule violations detected</li>"
    st.markdown(
        f"""
        <div class="explain-card">
            <div>{risk_badge_html(row['risk_bucket'])} &nbsp; <b>Final Score: {row['final_score']:.1f}/100</b></div>
            <p style="margin-top:10px;margin-bottom:4px;"><b>Reasons</b></p>
            <ul style="margin-top:0;">{reasons_html}</ul>
            <p style="margin-bottom:4px;"><b>Rule points:</b> {row['rule_points']:.0f} &nbsp;|&nbsp;
               <b>Anomaly score:</b> {row['anomaly_score']:.1f}</p>
            <p style="margin-bottom:0;"><b>Recommendation:</b> {row['recommendation']}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
