import logging
logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout = 'wide')

# Show appropriate sidebar links for the role of the currently logged in user
SideBarLinks()


st.title(f"Welcome Maintenance/IT Worker, {st.session_state['first_name']}.")
st.write('')
st.write('')
st.write('### What would you like to do today?')


if st.button('Daily Maintenance Tasks', 
             type='primary',
             use_container_width=True):
  st.switch_page('pages/11_Maintenance_Worker_Home.py')

if st.button('Track Work Hours and Pay', 
             type='primary',
             use_container_width=True):
  st.switch_page('pages/12_Hours_Wage_Pay.py')

if st.button("System Admin Privileges",
             type='primary',
             use_container_width=True):
  st.switch_page('pages/13_System_Admin_Privileges.py')