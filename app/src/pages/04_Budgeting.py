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
    r = requests.get(url, params=params or {}, timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()

# =====================
# Top row: headline metrics + spending trend
# =====================
st.title("💰 President Budget Dashboard")
st.write(f"### Welcome back, {st.session_state['first_name']}.")


try:
    summary = _get("/metrics/president/budget")  # Returns list of dicts per college
    df_summary = pd.DataFrame(summary)
except Exception as e:
    st.error(f"Unable to load budget summary — {e}")
    df_summary = pd.DataFrame()

if not df_summary.empty:
    st.subheader("Budget Overview by College")
    # Format numbers
    for col in ["totalBudget", "totalDonations", "budgetUsed", "remaining"]:
        if col in df_summary.columns:
            df_summary[col] = pd.to_numeric(df_summary[col], errors="coerce").fillna(0).map("${:,.0f}".format)
    st.dataframe(df_summary, use_container_width=True)
else:
    st.info("No budget summary data available.")

# Spending trend
st.subheader("Spending Trend Across Colleges")
try:
    trend = _get("/metrics/president/budget/spending-trend")  # Expecting: [{college, period, spending}]
    df_trend = pd.DataFrame(trend)
    if not df_trend.empty:
        df_trend["period"] = pd.to_datetime(df_trend["period"], errors="coerce")
        df_trend["spending"] = pd.to_numeric(df_trend["spending"], errors="coerce").fillna(0)
        fig_trend = px.line(
            df_trend.sort_values("period"),
            x="period",
            y="spending",
            color="college",
            markers=True,
            labels={"period": "Date", "spending": "Spending ($)", "college": "College"},
            title="Spending Trend by College"
        )
        st.plotly_chart(fig_trend, use_container_width=True)
    else:
        st.info("No spending trend data available.")
except Exception as e:
    st.warning(f"Unable to load spending trend: {e}")

# =====================
# Middle: course-level breakdown + recent donations
# =====================
left_mid, right_mid = st.columns([1.4, 0.6], gap="large")

with left_mid:
    st.subheader("Course-Level Financial Breakdown")
    try:
        breakdown = _get("/metrics/president/budget/by-course")  # Expecting all courses across colleges
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
    except Exception as e:
        st.warning(f"Unable to load course breakdown: {e}")

with right_mid:
    st.subheader("Recent Donations")
    try:
        donations = _get("/metrics/president/budget/donations", params={"limit": 100})
        df_don = pd.DataFrame(donations)
        if not df_don.empty:
            df_don["date"] = pd.to_datetime(df_don["date"], errors="coerce")
            df_don["amount"] = pd.to_numeric(df_don["amount"], errors="coerce").fillna(0)
            df_don = df_don.rename(columns={"donor": "Donor", "courseName": "Course", "date": "Date", "amount": "Amount", "college": "College"})
            st.dataframe(df_don.sort_values("Date", ascending=False), use_container_width=True)
        else:
            st.info("No recent donations available.")
    except Exception as e:
        st.warning(f"Unable to load donations: {e}")

# =====================
# Bottom: donations by course bar chart
# =====================
st.subheader("Donations by Course")
try:
    donations_by_course = _get("/metrics/president/budget/donations-by-course")  # Expecting all courses
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
except Exception as e:
    st.warning(f"Unable to load donations by course: {e}")