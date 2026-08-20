"""Dark blue enterprise theme + scrolling marquee banner, shared across pages."""

import streamlit as st

MARQUEE_TEXT = "AI Powered Banking Risk Application"

_CSS = f"""
<style>
:root {{
    --navy-950: #050b18;
    --navy-900: #0a1630;
    --navy-800: #0f2247;
    --navy-700: #16305e;
    --accent: #3b82f6;
    --accent-soft: #60a5fa;
    --text-light: #e2e8f0;
}}

.stApp {{
    background-color: var(--navy-950);
    color: var(--text-light);
}}

section[data-testid="stSidebar"] {{
    background-color: var(--navy-900);
    border-right: 1px solid var(--navy-700);
}}

[data-testid="stMetric"] {{
    background-color: var(--navy-900);
    border: 1px solid var(--navy-700);
    border-radius: 10px;
    padding: 14px 16px;
}}

.marquee-wrap {{
    width: 100%;
    overflow: hidden;
    background: linear-gradient(90deg, var(--navy-900), var(--navy-800), var(--navy-900));
    border-bottom: 2px solid var(--accent);
    padding: 10px 0;
    margin-bottom: 18px;
    box-shadow: 0 2px 12px rgba(59, 130, 246, 0.25);
}}

.marquee-track {{
    display: inline-block;
    white-space: nowrap;
    padding-left: 100%;
    animation: marquee-scroll 18s linear infinite;
    font-size: 1.05rem;
    font-weight: 700;
    letter-spacing: 0.06em;
    color: var(--accent-soft);
    text-transform: uppercase;
}}

@keyframes marquee-scroll {{
    0%   {{ transform: translateX(0); }}
    100% {{ transform: translateX(-100%); }}
}}

h1, h2, h3 {{
    color: var(--text-light);
}}

.risk-badge {{
    display: inline-block;
    padding: 3px 10px;
    border-radius: 999px;
    font-weight: 700;
    font-size: 0.8rem;
}}
.risk-low {{ background: #14532d; color: #86efac; }}
.risk-medium {{ background: #78350f; color: #fcd34d; }}
.risk-high {{ background: #7c2d12; color: #fdba74; }}
.risk-critical {{ background: #7f1d1d; color: #fca5a5; }}

.explain-card {{
    background: var(--navy-900);
    border: 1px solid var(--navy-700);
    border-radius: 10px;
    padding: 16px 18px;
    margin-top: 8px;
}}
</style>
"""


def apply_theme():
    st.markdown(_CSS, unsafe_allow_html=True)


def render_marquee(text: str = MARQUEE_TEXT):
    st.markdown(
        f"""
        <div class="marquee-wrap">
            <div class="marquee-track">{text} &nbsp;&nbsp;&bull;&nbsp;&nbsp; {text} &nbsp;&nbsp;&bull;&nbsp;&nbsp; {text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
