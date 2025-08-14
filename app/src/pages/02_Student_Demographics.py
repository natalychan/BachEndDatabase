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

# Page title
st.header("Student Demographics Data")
st.write(f"### Hi, {st.session_state['first_name']}.")

# Helper to fetch and display a pie chart
def create_pie_chart(api_url, category_col, title, color_seq=None):
    try:
        response = requests.get(api_url)
        if response.status_code == 200:
            data = response.json()
            df = pd.DataFrame(data)

            # Ensure counts
            if 'count' not in df.columns:
                df['count'] = 1
                df = df.groupby(category_col).size().reset_index(name='count')

            # Pie chart (donut style)
            fig = px.pie(
                df,
                names=category_col,
                values='count',
                hole=0.4,  # donut
                color_discrete_sequence=color_seq
            )
            fig.update_traces(textinfo='percent+label')
            fig.update_layout(title=title)

            st.plotly_chart(fig, use_container_width=True)
            st.subheader(f"{title} Data")
            st.dataframe(df)

        else:
            st.error(f"Failed to fetch data: HTTP {response.status_code}")
    except requests.exceptions.RequestException as e:
        st.error(f"Error connecting to API: {str(e)}")
    except Exception as e:
        st.error(f"Error creating pie chart: {str(e)}")

# Geographic origin
st.subheader("Geographic Origin")
st.write("Proportion of students from in-state vs. out-of-state.")
with st.echo(code_location='above'):
    create_pie_chart(
        "http://web-api:4000/api/metrics/demographics",
        category_col="origin",
        title="Geographic Origin of Students",
        color_seq=px.colors.sequential.Viridis
    )

# Race/Ethnicity
st.subheader("Race/Ethnicity")
st.write("Distribution of students by race and ethnicity.")
with st.echo(code_location='above'):
    create_pie_chart(
        "http://web-api:4000/api/students/race_ethnicity",
        category_col="race",
        title="Race/Ethnicity of Students",
        color_seq=px.colors.qualitative.Set3
    )

# Socioeconomic Status
st.subheader("Socioeconomic Status")
st.write("Distribution of students across family income brackets.")
with st.echo(code_location='above'):
    create_pie_chart(
        "http://web-api:4000/api/students/income_brackets",
        category_col="income_bracket",
        title="Family Income Brackets",
        color_seq=px.colors.sequential.Plasma
    )

# Housing Status
st.subheader("Housing Status")
st.write("Proportion of students living on-campus, off-campus, or other.")
with st.echo(code_location='above'):
    create_pie_chart(
        "http://web-api:4000/api/students/housing_status",
        category_col="housing_status",
        title="Housing Status of Students",
        color_seq=px.colors.qualitative.Pastel
    )