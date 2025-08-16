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
st.header('Student Clubs and Organizations')

# You can access the session state to make a more customized/personalized app experience
st.write(f"### Hi, {st.session_state['first_name']}.")

main_col, right_col = st.columns([3, 1]) 

with main_col:
    try:
        API_URL = "http://web-api:4000/api/clubs"
        response = requests.get(API_URL)
        if response.status_code == 200:
            data = response.json()
            if data: 
                df = pd.DataFrame(data)
                st.subheader("All Clubs")
                st.write("Here is a list of all clubs available:")
                categories = ['All'] + sorted(df['category'].unique())
                selected_category = st.selectbox("Filter by category:", categories)

                if selected_category != 'All':
                    filtered_df = df[df['category'] == selected_category]
                else:
                    filtered_df = df

                st.write(f"Showing {len(filtered_df)} clubs:")
                st.dataframe(df[['name','location','description']], use_container_width=True, hide_index=True)
            else: 
                st.info("No clubs data available.")
        else:
            st.error(f"Failed to fetch data: HTTP {response.status_code}")
    except requests.exceptions.RequestException as e:
        st.error(f"Error connecting to API: {str(e)}")
    except Exception as e:
        st.error(f"Error displaying clubs: {str(e)}")



with right_col:
    student_id = st.session_state.get('student_id') 
    if student_id:
        API_URL = f"http://web-api:4000/api/club_members/{student_id}"

    response = requests.get(API_URL)

    if response.status_code == 200:
        data = response.json()
        if data:
            df = pd.DataFrame(data)
            st.subheader("Current Membership")
            st.dataframe(df, use_container_width=True, hide_index=True)
            st.write("You are currently a member of the following clubs:")
            st.write(f"Total Clubs: {len(df)}")
            st.write("If you wish to leave a club, please contact the club president or advisor.")
        else:
            st.info("You are not part of any clubs.")
    else:
        st.error(f"Failed to fetch data: HTTP {response.status_code}")
