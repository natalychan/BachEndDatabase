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

API_BASE = "http://localhost:5000/api"

st.title("📊 Enrollment & Teacher Metrics")
st.write(f"### Hi, {st.session_state['first_name']}.")

# Student–Teacher Ratio
st.subheader("Student–Teacher Ratio by College")
ratio_resp = requests.get(f"{API_BASE}/colleges/metrics/student-teacher-ratio")
if ratio_resp.status_code == 200:
    ratio_df = pd.DataFrame(ratio_resp.json())
    st.dataframe(ratio_df)

    fig_ratio = px.bar(
        ratio_df,
        x="college",
        y="student_teacher_ratio",
        text="student_teacher_ratio",
        title="Student–Teacher Ratio by College",
        labels={"college": "College", "student_teacher_ratio": "Ratio"},
    )
    fig_ratio.update_traces(texttemplate='%{text}', textposition='outside')
    st.plotly_chart(fig_ratio)

# Vacant Courses
st.subheader("Vacant Courses")
vacancy_resp = requests.get(f"{API_BASE}/courses/vacancies")
if vacancy_resp.status_code == 200:
    vacancy_df = pd.DataFrame(vacancy_resp.json())
    vacant_only = vacancy_df[vacancy_df["is_vacant"] == 1]
    st.dataframe(vacant_only)