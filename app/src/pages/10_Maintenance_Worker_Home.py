import logging
logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout = 'wide')

# Show appropriate sidebar links for the role of the currently logged in user
SideBarLinks()


st.title(f"Welcome Maintenance/System Admin, {st.session_state['first_name']}.")
st.write('')
st.write('')
st.write('### What would you like to do today?')


if st.button('View Maintenance Requests', 
             type='primary',
             use_container_width=True):
  st.switch_page('pages/11_Maintenance_Requests.py')

if st.button('View Tools', 
             type='primary',
             use_container_width=True):
  st.switch_page('pages/12_Tools.py')

if st.button('View Classroom Maintenance', 
             type='primary',
             use_container_width=True):
  st.switch_page('pages/13_Classroom_Maintenance.py')

if st.button('View Work Hours', 
             type='primary',
             use_container_width=True):
  st.switch_page('pages/14_Work_Hours.py')

if st.button("System Admin Page",
             type='primary',
             use_container_width=True):
  st.switch_page('pages/15_System_Admin.py')