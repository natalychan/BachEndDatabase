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

# Header for page
st.header("Student Demographics Data")
st.write(f"### Hi, {st.session_state['first_name']}.")

# Fetch the single demographics dataset
try:
    response = requests.get("http://web-api:4000/api/metrics/demographics")
    if response.status_code == 200:
        df = pd.DataFrame(response.json())

        # Expecting columns: type, category, num_students, percentage
        if not {'type', 'category', 'num_students', 'percentage'}.issubset(df.columns):
            st.error("API did not return expected columns.")
        else:
            # Helper to create one pie chart from a subset of the data
            def make_pie_chart(df_subset, title, color_seq=None):
                fig = px.pie(
                    df_subset,
                    names="category",
                    values="num_students",
                    hole=0.4,
                    color_discrete_sequence=color_seq
                )
                fig.update_traces(textinfo='percent+label')
                fig.update_layout(title=title)
                st.plotly_chart(fig, use_container_width=True)
                st.dataframe(df_subset.drop(columns=['type']).rename(columns={'category': 'Category', 'num_students': 'Number of Students', 'percentage': 'Percentage'}))

            # Geographic Origin
            st.subheader("Geographic Origin")
            make_pie_chart(
                df[df["type"] == "origin"],
                "Geographic Origin of Students",
                color_seq=px.colors.sequential.Viridis
            )

            # Housing Status
            st.subheader("Housing Status")
            make_pie_chart(
                df[df["type"] == "housingStatus"],
                "Housing Status of Students",
                color_seq=px.colors.sequential.Viridis
            )

            # Race/Ethnicity
            st.subheader("Race/Ethnicity")
            make_pie_chart(
                df[df["type"] == "race"],
                "Race/Ethnicity of Students",
                color_seq=px.colors.sequential.Viridis
            )

            # Socioeconomic Status (Income Brackets)
            st.subheader("Socioeconomic Status")
            st.write("Distribution of students across family income brackets.")

            make_pie_chart(
                df[df["type"] == "incomeBracket"],
                "Family Income Brackets",
                color_seq=px.colors.sequential.Viridis
            )
    else:
        st.error(f"Failed to fetch data: HTTP {response.status_code}")

except requests.exceptions.RequestException as e:
    st.error(f"Error connecting to API: {str(e)}")
except Exception as e:
    st.error(f"Error creating charts: {str(e)}")