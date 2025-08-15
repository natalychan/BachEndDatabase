import streamlit as st
from streamlit_extras.app_logo import add_logo
from modules.nav import SideBarLinks

SideBarLinks()

st.write("# About this App")

st.markdown (
    """
    Welcome to the Join U Portal!

    Here you will be able to access all of your role specific tools.
    """
        )
