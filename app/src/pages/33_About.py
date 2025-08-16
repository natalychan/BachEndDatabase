import streamlit as st
from streamlit_extras.app_logo import add_logo
from modules.nav import SideBarLinks
import os

SideBarLinks(show_home=True)

st.write("About")

here = os.path.dirname(__file__)

st.image("assets/JoinUPresident.png", width=500)

st.write("- University President")

st.write("")
st.write("")
st.write("")
st.write("")



st.markdown (
    """
    Welcome to the Join U Portal!

    Here you will be able to access all of your role specific tools.
    """
        )
