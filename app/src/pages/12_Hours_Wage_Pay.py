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
st.header('Track Work Hours and Pay')

# You can access the session state to make a more customized/personalized app experience
st.write(f"### Hi, {st.session_state['first_name']}.")


with st.echo(code_location='above'):
    try:
        API_URL = "http://web-api:4000/clubs_api/clubs"
        response = requests.get(API_URL)
        if response.status_code == 200:
            data = response.json()
            
            #convert to pandas dataframe
            df = pd.DataFrame(data)
            
            #display table
            st.subheader("All Clubs")
            st.dataframe(df, use_container_width=True)
            
            #shows the total number of clubs
            st.info(f"Total Clubs: {len(df)}")
            
        else:
            st.error(f"Failed to fetch data: HTTP {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        st.error(f"Error connecting to API: {str(e)}")
        st.info("Please ensure the API server is running on http://web-api:4000")
    except Exception as e:
        st.error(f"Error creating histogram: {str(e)}")