import logging
logger = logging.getLogger(__name__)

import os
import requests
import pandas as pd
import numpy as np
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

# --- REQUIRE: dean_id in session ---
if "dean_id" not in st.session_state:
    st.error("No dean_id in session. Set st.session_state['dean_id'] at login.")
    st.stop()

DEAN_ID = int(st.session_state["dean_id"])
first_name = st.session_state.get("first_name", "Colleague")
st.title(f"Dean Budget — Welcome {first_name}")

# Resolve dean's college once and cache into session
@st.cache_data(ttl=300, show_spinner=False)
def get_dean_college(_id: int):
    try:
        return (_get(f"/metrics/deans/{_id}/college") or {}).get("collegeName")
    except Exception:
        return None

if not st.session_state.get("college"):
    st.session_state["college"] = get_dean_college(DEAN_ID)

college = st.session_state.get("college")
if not college:
    st.warning("Could not determine your college yet. Data may appear empty.")

# =====================
# Top row: headline metrics + spending trend
# =====================
left_top, right_top = st.columns([1, 1], gap="large")

with left_top:
    st.header("Budget Overview")
    try:
        summary = _get(f"/metrics/deans/{DEAN_ID}/budget/summary") or {}
    except Exception as e:
        st.warning(f"Unable to load budget summary — {e}")
        summary = {}

    totalBudget   = float(summary.get("totalBudget") or 0)
    totalDon      = float(summary.get("totalDonations") or 0)
    used          = float(summary.get("budgetUsed") or 0)
    remaining     = float(summary.get("remaining") or (totalBudget + totalDon - used))

    k1, k2 = st.columns(2)
    with k1:
        st.metric("Total Budget", f"${totalBudget:,.0f}")
        st.metric("Budget Used", f"${used:,.0f}")
    with k2:
        st.metric("Total Donations", f"${totalDon:,.0f}")
        st.metric("Remaining", f"${remaining:,.0f}")

with right_top:
    st.header("Spending Over Time")
    try:
        rows = _get(f"/metrics/deans/{DEAN_ID}/budget/spending-trend")
        df_trend = pd.DataFrame(rows)
        if not df_trend.empty:
            # Convert period to datetime for nicer plotting & range widgets
            df_trend["period"] = pd.to_datetime(df_trend["period"], errors="coerce")
            df_trend["spending"] = pd.to_numeric(df_trend.get("spending", 0), errors="coerce").fillna(0)
            df_trend = df_trend.dropna(subset=["period"]).sort_values("period")
        else:
            df_trend = pd.DataFrame(columns=["period", "spending"]).astype({"period": "datetime64[ns]"})
    except Exception as e:
        st.caption(f"Using empty data — {e}")
        df_trend = pd.DataFrame(columns=["period", "spending"]).astype({"period": "datetime64[ns]"})

    if df_trend.empty:
        st.info("No spending recorded yet.")
    else:
        # Optional date filter
        min_d, max_d = df_trend["period"].min(), df_trend["period"].max()
        dr = st.date_input(
            "Filter range",
            value=(min_d.date(), max_d.date()),
            min_value=min_d.date(),
            max_value=max_d.date(),
            key="budget_trend_range",
        )
        if isinstance(dr, tuple) and len(dr) == 2:
            start, end = pd.to_datetime(dr[0]), pd.to_datetime(dr[1])
            show = df_trend[(df_trend["period"] >= start) & (df_trend["period"] <= end)]
        else:
            show = df_trend

        fig = px.line(
            show,
            x="period",
            y="spending",
            markers=True,
            labels={"period": "Date", "spending": "Spending ($)"},
        )
        fig.update_layout(margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

# =====================
# Middle: Course financial breakdown + recent donations
# =====================
left_mid, right_mid = st.columns([1.4, 0.6], gap="large")

with left_mid:
    st.subheader("Course Financial Breakdown")
    try:
        rows = _get(f"/metrics/deans/{DEAN_ID}/budget/by-course")
        df = pd.DataFrame(rows)
        if df.empty:
            df_show = pd.DataFrame(columns=["Dept", "Total", "Allocated", "Donations", "Used", "Used %"])                 .astype({"Used %": float})
        else:
            rename = {
                "courseName": "Dept",
                "total": "Total",
                "allocated": "Allocated",
                "donations": "Donations",
                "used": "Used",
                "usedPct": "Used %",
            }
            df_show = df.rename(columns=rename)[list(rename.values())]
            for c in ["Total", "Allocated", "Donations", "Used", "Used %"]:
                df_show[c] = pd.to_numeric(df_show[c], errors="coerce").fillna(0)
            # Default sort by Used % desc
            df_show = df_show.sort_values(["Used %", "Dept"], ascending=[False, True])
    except Exception as e:
        st.warning(f"Could not load breakdown — {e}")
        df_show = pd.DataFrame(columns=["Dept", "Total", "Allocated", "Donations", "Used", "Used %"])             .astype({"Used %": float})

    # A small pager / head limit to keep table readable
    topn = st.slider("Rows to display", 5, max(5, len(df_show)), min(12, max(5, len(df_show))), key="rows_to_display") if not df_show.empty else 0
    st.dataframe(
        (df_show.head(topn) if topn else df_show),
        use_container_width=True,
        hide_index=True,
    )

with right_mid:
    st.subheader("Recent Donations")
    try:
        rows = _get(f"/metrics/deans/{DEAN_ID}/budget/donations", params={"limit": 100})
        dons = pd.DataFrame(rows)
        if not dons.empty and "date" in dons.columns:
            dons["date"] = pd.to_datetime(dons["date"], errors="coerce")
            # Date filter UI (range)
            min_d, max_d = dons["date"].min(), dons["date"].max()
            if pd.notnull(min_d) and pd.notnull(max_d):
                rng = st.date_input(
                    "Date range",
                    value=(min_d.date(), max_d.date()),
                    min_value=min_d.date(),
                    max_value=max_d.date(),
                    key="don_date_range",
                )
                if isinstance(rng, tuple) and len(rng) == 2:
                    s, e = pd.to_datetime(rng[0]), pd.to_datetime(rng[1])
                    dons = dons[(dons["date"] >= s) & (dons["date"] <= e)]
        show = dons.rename(columns={"donor": "Donor", "amount": "Amount", "date": "Date", "courseName": "Dept"})
        for c in ["Amount"]:
            if c in show.columns:
                show[c] = pd.to_numeric(show[c], errors="coerce").fillna(0)
        st.dataframe(show, use_container_width=True, hide_index=True)
    except Exception as e:
        st.caption(f"No donations to show — {e}")

# =====================
# Bottom: Donations by Course bar
# =====================
st.subheader("Donations by Course")
try:
    rows = _get(f"/metrics/deans/{DEAN_ID}/budget/donations-by-course")
    d2 = pd.DataFrame(rows)
    if d2.empty:
        d2 = pd.DataFrame({"courseName": [], "donations": []})
    d2 = d2.rename(columns={"courseName": "Dept", "donations": "Donations"})
    d2["Donations"] = pd.to_numeric(d2["Donations"], errors="coerce").fillna(0)
    fig = px.bar(d2, x="Dept", y="Donations", labels={"Dept": "Course", "Donations": "Donations ($)"})
    st.plotly_chart(fig, use_container_width=True)
except Exception as e:
    st.caption(f"Unable to load donations by course — {e}")
