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
st.header('Work Hours')

# You can access the session state to make a more customized/personalized app experience
st.write(f"### Hi, {st.session_state['first_name']}, nice work!")



try:
    user_id = st.session_state.get('user_id')
    st.write(f"### Work Hours for User ID: {user_id}")
    
    if user_id:
        API_URL = f"http://web-api:4000/api/maintenance-staffs/{user_id}/hours"
        response = requests.get(API_URL)
        
        if response.status_code == 200:
            data = response.json()
            
            if data and data.get('entries'):
                df = pd.DataFrame(data['entries'])

                # Rename columns to capitalize words
                df.rename(columns={
                    'orderId': 'Order ID',
                    'workHours': 'Work Hours',
                    'problemType': 'Problem Type',
                    'state': 'State',
                    'submitted': 'Submitted'
                }, inplace=True)

                st.dataframe(df, use_container_width=True, hide_index=True)
                st.info(f"Total Work Entries: {len(df)}")
            else:
                st.warning("No work hours found")
        else:
            st.error(f"Failed to fetch data: HTTP {response.status_code}")
    else:
        st.error("User ID not found in session")

except Exception as e:
    st.error(f"Error: {str(e)}")