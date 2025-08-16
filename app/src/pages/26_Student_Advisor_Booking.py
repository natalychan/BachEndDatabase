import pandas as pd
import logging
logger = logging.getLogger(__name__)
import streamlit as st
import requests
from streamlit_extras.app_logo import add_logo
from modules.nav import SideBarLinks
from datetime import datetime


# Show appropriate sidebar links for the role of the currently logged in user
SideBarLinks()

# set the header of the page
st.header('Advisor Information')

# You can access the session state to make a more customized/personalized app experience
st.write(f"### Hi, {st.session_state['first_name']}.")


try:
    student_id = st.session_state.get('student_id') 
    if student_id:
        API_URL = f"http://web-api:4000/api/advisors/{student_id}"
        response = requests.get(API_URL)

    if response.status_code == 200:
        data = response.json()
            
        if data:
            df = pd.DataFrame([data])
            df.rename(columns={
                    "advisor_name": "Advisor Name",
                    "emailAddress": "Email Address",
                }, inplace=True)
            cols_to_show = [c for c in ["Advisor Name", "Email Address"] if c in df.columns]
            if cols_to_show:
                st.subheader("Name and Email")
                st.dataframe(df[cols_to_show], use_container_width=True, hide_index=True)
        else:
            st.warning("No info found - API returned empty array")
    else:
        st.error(f"Failed to fetch data: HTTP {response.status_code}")
        st.write(f"Response text: {response.text}")
except Exception as e:
    st.error(f"Error: {str(e)}")




