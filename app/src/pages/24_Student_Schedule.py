import logging
logger = logging.getLogger(__name__)
import pandas as pd
import streamlit as st
from streamlit_extras.app_logo import add_logo
from modules.nav import SideBarLinks
import requests

# Show appropriate sidebar links for the role of the currently logged in user
SideBarLinks()

# set the header of the page
st.header('Class Schedule')

# You can access the session state to make a more customized/personalized app experience
st.write(f"### Hi, {st.session_state['first_name']}.")


try:
    student_id = st.session_state.get('student_id') 
    st.write(f"### Student ID: {student_id}")

    if student_id:
        API_URL = f"http://web-api:4000/api/students/{student_id}/schedule"
        response = requests.get(API_URL)

        if response.status_code == 200:
            data = response.json()
            
            if data:
                df = pd.DataFrame(data)
                df.rename(columns={
                    "course_id": "Course ID",
                    "course_name": "Course Name",
                    "enrollment" : "Students Enrolled",
                    "roomNumber" : "RoomNumber",
                    "time" : "Time"
                }, inplace=True)
                st.subheader("Student Schedule")
                st.dataframe(df, use_container_width=True)
                st.info(f"Class Schedule: {len(df)}")
            else:
                st.warning("No courses found - API returned empty array")
        else:
            st.error(f"Failed to fetch data: HTTP {response.status_code}")
            st.write(f"Response text: {response.text}")

except Exception as e:
    st.error(f"Error: {str(e)}")