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


#change all of these to be appropriate for the student

#page shows student schedule, and there's gpa under each class
if st.button('Schedule', 
             type='primary',
             use_container_width=True):
  st.switch_page('pages/01_World_Bank_Viz.py')

#page shows instrument rentals info and instrument vacancy
if st.button('Instrument Rentals', 
             type='primary',
             use_container_width=True):
  st.switch_page('pages/02_Map_Demo.py')

#page shows classroom booking info and classroom vacancy
if st.button('Classroom Bookings', 
             type='primary',
             use_container_width=True):
  st.switch_page('pages/02_Map_Demo.py')  

#page shows advisor meetings
if st.button('Advisor Meetings', 
             type='primary',
             use_container_width=True):
  st.switch_page('pages/02_Map_Demo.py')  

#page shows clubs info
if st.button('Clubs', 
             type='primary',
             use_container_width=True):
  st.switch_page('pages/02_Map_Demo.py')    