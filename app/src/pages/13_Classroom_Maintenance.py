import logging
logger = logging.getLogger(__name__)
import pandas as pd
import streamlit as st
from streamlit_extras.app_logo import add_logo
from modules.nav import SideBarLinks
import requests

# Call the SideBarLinks from the nav module in the modules directory
SideBarLinks()

# set the header of the page
st.header('Classroom Maintenance')

# You can access the session state to make a more customized/personalized app experience
st.write(f"### Hi, {st.session_state['first_name']}, these classrooms are due for maintenance!")


with st.echo(code_location='above'):
    try:
        API_URL = "http://web-api:4000/api/classrooms"
        response = requests.get(API_URL)
        
        if response.status_code == 200:
            data = response.json()
            
            if data:
                df = pd.DataFrame(data)
                st.dataframe(df, use_container_width=True)
                st.info(f"Classrooms Needing Maintenance: {len(df)}")
            else:
                st.warning("No classrooms need maintenance")
        else:
            st.error(f"Failed to fetch data: HTTP {response.status_code}")

    except Exception as e:
        st.error(f"Error: {str(e)}")