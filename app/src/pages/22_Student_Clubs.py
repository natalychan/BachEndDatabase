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


with st.echo(code_location='above'):
    try:
        API_URL = "http://web-api:4000/api/clubs"
        response = requests.get(API_URL)
        if response.status_code == 200:
            data = response.json()
            
            #convert to pandas dataframe
            df = pd.DataFrame(data)
            
            #display table
            main_col, right_col = st.columns([3, 1])  # 3:1 rati
            with main_col:
                st.subheader("All Clubs")
                st.write("Here is a list of all clubs available:")
                st.dataframe(df, use_container_width=True)
            with right_col:
                st.subheader("My Clubs")
                try:
                    student_id = st.session_state['student_id']  # must be set at login
                    API_URL = f"http://web-api:4000/api/club_members"
                    
                    response = requests.get(API_URL)
                    if response.status_code == 200:
                        data = response.json()
                        if data:
                            df = pd.DataFrame(data)
                            st.dataframe(df, use_container_width=True)
                        else:
                            st.info("You are not part of any clubs.")
                    else:
                        st.error(f"Failed to fetch data: HTTP {response.status_code}")

                except requests.exceptions.RequestException as e:
                    st.error(f"Error connecting to API: {str(e)}")
                except Exception as e:
                    st.error(f"Error displaying clubs: {str(e)}")

                else:
                    st.error(f"Failed to fetch data: HTTP {response.status_code}")
                    
    except requests.exceptions.RequestException as e:
        st.error(f"Error connecting to API: {str(e)}")
        st.info("Please ensure the API server is running on http://web-api:4000")
    except Exception as e:
        st.error(f"Error creating histogram: {str(e)}")