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

st.title("📊 Enrollment & Teacher Metrics")
st.write(f"### Hi, {st.session_state['first_name']}.")

# Student–Teacher Ratio
st.subheader("Student–Teacher Ratio by College")
try:
    ratio_resp = requests.get(f"http://web-api:4000/api/metrics/student-teacher-ratio")
    ratio_resp.raise_for_status()
# ratio_resp = requests.get(f"http://web-api:4000/api/metrics/student-teacher-ratio")
    if ratio_resp.status_code == 200:
        ratio_df = pd.DataFrame(ratio_resp.json())
        st.dataframe(ratio_df.rename(columns={'college': 'College', 'num_professors':'Number of Professors', 'num_students':'Number of Students', 'student_teacher_ratio':'Student-Teacher Ratio'}), hide_index=True)

        fig_ratio = px.bar(
            ratio_df,
            x="college",
            y="student_teacher_ratio",
            text="student_teacher_ratio",
            title="Student–Teacher Ratio by College",
            labels={"college": "College", "student_teacher_ratio": "Ratio"},
        )
        fig_ratio.update_traces(texttemplate='%{text}', textposition='outside')
        st.plotly_chart(fig_ratio, use_container_width=True)
except requests.RequestException as e:
    st.error(f"Error fetching student-teacher ratio data: {e}")

# Vacant Courses
st.subheader("Vacant Courses")
try:
    vacancy_resp = requests.get(f"http://web-api:4000/api/metrics/courses/vacancies")
    vacancy_resp.raise_for_status()
    if vacancy_resp.status_code == 200:
        vacancy_df = pd.DataFrame(vacancy_resp.json())
        vacant_only = vacancy_df[vacancy_df["is_vacant"] == 1]
        df_sub = vacant_only[['course_id', 'course_name', 'enrollment', 'time']]
        st.dataframe(df_sub.rename(columns={
            'course_id': 'Course ID', 'course_name': 'Course Name', 'enrollment': 'Enrollment', 'time': 'Time'})
                     , use_container_width=True,
                      hide_index=True)
except requests.RequestException as e:
    st.error(f"Error fetching vacant courses data: {e}")