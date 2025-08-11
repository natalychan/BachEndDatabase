import logging
logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout = 'wide')

# Call the SideBarLinks from the nav module in the modules directory
SideBarLinks()


st.title(f"Welcome President, {st.session_state['first_name']}.")
st.write('')
st.write('')
st.write('### What would you like to do today?')

if st.button('View Student Performance Data Visualization', 
             type='primary',
             use_container_width=True):
  st.switch_page('pages/01_Student_Performance.py')


if st.button('View Demographic Data Visualization', 
             type='primary',
             use_container_width=True):
  st.switch_page('pages/01_World_Bank_Viz.py')


