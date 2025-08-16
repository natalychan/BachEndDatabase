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
TIMEOUT  = int(os.getenv("API_TIMEOUT", "8"))


if "dean_id" not in st.session_state:
    st.error("No dean_id in session. Set st.session_state['dean_id'] at login.")
    st.stop()

DEAN_ID = int(st.session_state["dean_id"])
st.title("Alumni Job Placement")
st.caption("As a dean, review alumni placement to evaluate how well courses prepare students for the future.")

@st.cache_data(ttl=60, show_spinner=False)
def _get(path, params=None):
    url = f"{API_BASE}{path}"
    r = requests.get(url, params=params or {}, timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()

@st.cache_data(ttl=120, show_spinner=False)
def get_dean_college(dean_id: int) -> str | None:
    try:
        data = _get(f"/metrics/deans/{dean_id}/college")
        return (data or {}).get("collegeName")
    except Exception:
        return None

if not st.session_state.get("college"):
    st.session_state["college"] = get_dean_college(DEAN_ID)

college = st.session_state.get("college")
if not college:
    st.warning("Could not determine your college yet. Data may appear empty.")

# Top: headline KPIs ---------------------------------------------------------
k1, k2, k3 = st.columns(3)
try:
    summary = _get(f"/metrics/deans/{DEAN_ID}/alumni/placement/summary")
except Exception as e:
    st.caption(f"Using empty summary — {e}")
    summary = {"totalAlumni": 0, "placed": 0, "placementRate": 0.0}

total = int(summary.get("totalAlumni") or 0)
placed = int(summary.get("placed") or 0)
rate   = float(summary.get("placementRate") or 0.0)

with k1: st.metric("Placement Rate", f"{rate:.1f}%")
with k2: st.metric("Placed Alumni", f"{placed:,}")
with k3: st.metric("Total Alumni", f"{total:,}")

st.divider()

# Middle: By Course + Trend ---------------------------------------------
left, right = st.columns([1.4, 1.0], gap="large")

with left:
    st.subheader("Placement by Course")
    try:
        rows = _get(f"/metrics/deans/{DEAN_ID}/alumni/placement/by-course")
        df = pd.DataFrame(rows)
    except Exception as e:
        st.caption(f"Using empty data — {e}")
        df = pd.DataFrame(columns=["courseName","alumniCount","placed","placementRate","avgGpa"])

    if df.empty:
        st.info("No alumni placement data yet.")
    else:
        rename = {
            "courseName": "Course",
            "alumniCount": "Alumni",
            "placed": "Placed",
            "placementRate": "Placement %",
            "avgGpa": "Avg GPA",
        }
        df_show = df.rename(columns=rename)
        df_show["Placement %"] = pd.to_numeric(df_show["Placement %"], errors="coerce").fillna(0.0)
        df_show["Alumni"] = pd.to_numeric(df_show["Alumni"], errors="coerce").fillna(0).astype(int)
        df_show["Placed"] = pd.to_numeric(df_show["Placed"], errors="coerce").fillna(0).astype(int)
        st.dataframe(
            df_show.sort_values(["Placement %","Alumni"], ascending=[False, False]).reset_index(drop=True),
            use_container_width=True,
            hide_index=True,
        )

        fig = px.bar(
            df_show.sort_values("Placement %", ascending=False),
            x="Course", y="Placement %",
            hover_data=["Alumni","Placed","Avg GPA"],
        )
        fig.update_layout(margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("Placement Trend (by Student Year)")
    try:
        rows = _get(f"/metrics/deans/{DEAN_ID}/alumni/placement/by-year")
        dtrend = pd.DataFrame(rows)
        if not dtrend.empty:
            dtrend["year"] = pd.to_numeric(dtrend["year"], errors="coerce")
            dtrend["placementRate"] = pd.to_numeric(dtrend["placementRate"], errors="coerce")
            dtrend = dtrend.dropna(subset=["year"]).sort_values("year")
    except Exception as e:
        st.caption(f"Using empty trend — {e}")
        dtrend = pd.DataFrame(columns=["year","placementRate"])

    if not dtrend.empty:
        fig2 = px.line(dtrend, x="year", y="placementRate", markers=True,
                       labels={"year":"Student Year","placementRate":"Placement %"})
        fig2.update_layout(margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("No trend data yet.")

st.divider()

# Bottom: Highlights ---------------------------------------------------------
c1, c2 = st.columns(2, gap="large")
if 'df' in locals() and not df.empty:
    top = df.sort_values(["placementRate","alumniCount"], ascending=[False, False]).head(5)
    low = df.sort_values(["placementRate","alumniCount"], ascending=[True, False]).head(5)

    with c1:
        st.subheader("Top Course (Placement)")
        st.table(top[["courseName","placementRate","alumniCount","placed"]].rename(columns={
            "courseName":"Course","placementRate":"Placement %","alumniCount":"Alumni","placed":"Placed"
        }))

    with c2:
        st.subheader("Needs Attention")
        st.table(low[["courseName","placementRate","alumniCount","placed"]].rename(columns={
            "courseName":"Course","placementRate":"Placement %","alumniCount":"Alumni","placed":"Placed"
        }))
else:
    st.caption("No Course highlights to show.")
