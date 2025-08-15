import logging
logger = logging.getLogger(__name__)

import pandas as pd
import streamlit as st
from streamlit_extras.app_logo import add_logo
import plotly.express as px
from modules.nav import SideBarLinks
import requests

# Sidebar navigation
SideBarLinks()

# Page Header
st.title("💰 President's Budget Dashboard")
st.write(f"### Welcome back, {st.session_state['first_name']}.")

st.info("This dashboard provides a comprehensive view of revenue, expenses, and net balance for all colleges.")

# --- Fetch Budget Data ---
try:
    budget_resp = requests.get("http://web-api:4000/api/metrics/president/budget")
    if budget_resp.status_code != 200:
        st.error(f"Failed to fetch budget data. HTTP {budget_resp.status_code}")
    else:
        df = pd.DataFrame(budget_resp.json())

        # Expected columns check
        expected_cols = {"college", "total_expenses", "total_revenue", "net_balance"}
        if not expected_cols.issubset(df.columns):
            st.error(f"Unexpected columns in API response. Expected: {expected_cols}")
        else:
            # --- Summary KPIs ---
            total_rev = df["total_revenue"].sum()
            total_exp = df["total_expenses"].sum()
            total_net = total_rev - total_exp

            kpi_cols = st.columns(3)
            kpi_cols[0].metric("📈 Total Revenue", f"${total_rev:,.2f}")
            kpi_cols[1].metric("📉 Total Expenses", f"${total_exp:,.2f}")
            kpi_cols[2].metric("💵 Net Balance", f"${total_net:,.2f}")

            # --- Revenue vs Expenses by College ---
            st.subheader("Revenue vs Expenses by College")
            fig_bar = px.bar(
                df,
                x="college",
                y=["total_revenue", "total_expenses"],
                barmode="group",
                title="Revenue & Expenses by College",
                labels={"value": "Amount (USD)", "variable": "Category"},
                text_auto=True
            )
            st.plotly_chart(fig_bar, use_container_width=True)

            # --- Net Balance by College ---
            st.subheader("Net Balance by College")
            fig_net = px.bar(
                df,
                x="college",
                y="net_balance",
                title="Net Balance (Revenue - Expenses)",
                labels={"net_balance": "Net Balance (USD)", "college": "College"},
                text_auto=True,
                color="net_balance",
                color_continuous_scale=px.colors.sequential.Viridis
            )
            st.plotly_chart(fig_net, use_container_width=True)

            # --- Revenue Distribution ---
            st.subheader("Revenue Distribution Across Colleges")
            fig_pie = px.pie(
                df,
                names="college",
                values="total_revenue",
                title="Share of Total Revenue by College",
                hole=0.4,
                color_discrete_sequence=px.colors.sequential.Viridis
            )
            fig_pie.update_traces(textinfo="percent+label")
            st.plotly_chart(fig_pie, use_container_width=True)

            # --- Full Data Table ---
            st.subheader("Detailed Budget Data")
            st.dataframe(df.style.format({
                "total_revenue": "${:,.2f}",
                "total_expenses": "${:,.2f}",
                "net_balance": "${:,.2f}"
            }))

except requests.exceptions.RequestException as e:
    st.error(f"Error connecting to API: {str(e)}")
except Exception as e:
    st.error(f"Error processing data: {str(e)}")