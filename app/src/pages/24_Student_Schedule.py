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

# get the student's courses
with st.echo(code_location='above'):
    try:
        student_id = st.session_state.get('student_id') 

        if student_id:
            API_URL = f"http://web-api:4000/api/students/{student_id}/schedule" 
            #f strings when you need to replace

            response = requests.get(API_URL)
            
            if response.status_code == 200:
                data = response.json()
            
                #convert to pandas dataframe
                df = pd.DataFrame(data)
            
                #display table
                st.subheader("Student Schedule")
                st.dataframe(df, use_container_width=True)
            
                #shows the total number of clubs
                st.info(f"Class Schedule: {len(df)}")
            
            else:
                st.error(f"Failed to fetch data: HTTP {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        st.error(f"Error connecting to API: {str(e)}")
        st.info("Please ensure the API server is running on http://web-api:4000")


        
