import logging
logger = logging.getLogger(__name__)

import os
import requests
import pandas as pd
import plotly.express as px
import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout="wide")

# Sidebar
SideBarLinks()

API_BASE = os.getenv("API_BASE", "http://api:4000/api").rstrip("/")
TIMEOUT = int(os.getenv("API_TIMEOUT", "8"))

def _get(path: str, params=None):
    """Simple GET wrapper with base + timeout + raise_for_status."""
    url = f"{API_BASE}{path if path.startswith('/') else '/' + path}"
    try:
        r = requests.get(url, params=params or {}, timeout=TIMEOUT)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.error(f"Failed to fetch {url}: {e}")
        return []

# =====================
# Top row: headline metrics + spending trend
# =====================
st.title("💰 President Budget Dashboard")
st.write(f"### Welcome back, {st.session_state.get('first_name', 'President')}.")

# --- Budget Summary ---
summary = _get("/metrics/president/budget/summary")
df_summary = pd.DataFrame(summary)

if not df_summary.empty:
    st.subheader("Budget Overview by College")
    for col in ["totalBudget", "totalDonations", "budgetUsed", "remaining"]:
        if col in df_summary.columns:
            df_summary[col] = pd.to_numeric(df_summary[col], errors="coerce").fillna(0).map("${:,.0f}".format)
    st.dataframe(df_summary, use_container_width=True)
else:
    st.info("No budget summary data available.")

# --- Spending Trend ---
st.subheader("Spending Trend Across Colleges")
trend = _get("/metrics/president/budget/spending-trend")
df_trend = pd.DataFrame(trend)

if not df_trend.empty:
    df_trend["period"] = pd.to_datetime(df_trend["period"], errors="coerce")
    df_trend["spending"] = pd.to_numeric(df_trend["spending"], errors="coerce").fillna(0)
    fig_trend = px.line(
        df_trend.sort_values("period"),
        x="period",
        y="spending",
        color="collegeName",
        markers=True,
        labels={"period": "Date", "spending": "Spending ($)", "college": "College"},
        title="Spending Trend by College"
    )
    st.plotly_chart(fig_trend, use_container_width=True)
else:
    st.info("No spending trend data available.")

# =====================
# Middle: course-level breakdown + recent donations
# =====================
left_mid, right_mid = st.columns([1.4, 0.6], gap="large")

with left_mid:
    st.subheader("Course-Level Financial Breakdown")
    breakdown = _get("/metrics/president/budget/by-course")
    df_break = pd.DataFrame(breakdown)

    if not df_break.empty:
        rename_map = {
            "college": "College",
            "courseName": "Course",
            "total": "Total",
            "allocated": "Allocated",
            "donations": "Donations",
            "used": "Used",
            "usedPct": "Used %"
        }
        df_break = df_break.rename(columns=rename_map)
        for col in ["Total", "Allocated", "Donations", "Used", "Used %"]:
            if col in df_break.columns:
                df_break[col] = pd.to_numeric(df_break[col], errors="coerce").fillna(0)
        df_break = df_break.sort_values(["College", "Used %"], ascending=[True, False])
        st.dataframe(df_break, use_container_width=True)
    else:
        st.info("No course-level data available.")

with right_mid:
    st.subheader("Recent Donations")
    donations = _get("/metrics/president/budget/donations", params={"limit": 100})
    df_don = pd.DataFrame(donations)

    if not df_don.empty:
        df_don["date"] = pd.to_datetime(df_don["date"], errors="coerce")
        df_don["amount"] = pd.to_numeric(df_don["amount"], errors="coerce").fillna(0)
        df_don = df_don.rename(columns={
            "donor": "Donor",
            "courseName": "Course",
            "date": "Date",
            "amount": "Amount",
            "college": "College"
        })
        st.dataframe(df_don.sort_values("Date", ascending=False), use_container_width=True)
    else:
        st.info("No recent donations available.")

# =====================
# Bottom: donations by course bar chart
# =====================
st.subheader("Donations by Course")
donations_by_course = _get("/metrics/president/budget/donations-by-course")
df_dbc = pd.DataFrame(donations_by_course)

if not df_dbc.empty:
    df_dbc = df_dbc.rename(columns={"courseName": "Course", "donations": "Donations", "college": "College"})
    df_dbc["Donations"] = pd.to_numeric(df_dbc["Donations"], errors="coerce").fillna(0)
    fig_dbc = px.bar(
        df_dbc,
        x="Course",
        y="Donations",
        color="College",
        labels={"Course": "Course", "Donations": "Donations ($)"},
        title="Donations by Course and College"
    )
    st.plotly_chart(fig_dbc, use_container_width=True)
else:
    st.info("No donation data available for chart.")
