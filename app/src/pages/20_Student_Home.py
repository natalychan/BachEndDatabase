import logging
logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout = 'wide')

# Show appropriate sidebar links for the role of the currently logged in user
SideBarLinks()


st.title(f"Welcome Student, {st.session_state['first_name']}.")
st.write('')
st.write('')
st.write('### What would you like to do today?')



#page shows student schedule, and there's gpa under each class
if st.button('View Schedule', 
             type='primary',
             use_container_width=True):
  st.switch_page('pages/19_Student_Schedule.py')

#page shows instrument rentals info and instrument vacancy
if st.button('Rent Instrument', 
             type='primary',
             use_container_width=True):
  st.switch_page('pages/19_Instrument_Rental.py')

#page shows classroom booking info and classroom vacancy
if st.button('Make Classroom Booking', 
             type='primary',
             use_container_width=True):
  st.switch_page('pages/02_Map_Demo.py')  

#page shows advisor meetings
if st.button('View Advisor Meetings', 
             type='primary',
             use_container_width=True):
  st.switch_page('pages/02_Map_Demo.py')  

#page shows clubs info
if st.button('View Clubs', 
             type='primary',
             use_container_width=True):
  st.switch_page('pages/22_Student_Clubs.py')    

#page shows clubs info
if st.button('Submit a Maintenance Request', 
             type='primary',
             use_container_width=True):
  st.switch_page('pages/21_Maintenance_Requests.py')    