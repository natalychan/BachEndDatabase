# Idea borrowed from https://github.com/fsmosca/sample-streamlit-authenticator

# This file has function to add certain functionality to the left side bar of the app

import streamlit as st


#### ------------------------ General ------------------------
def HomeNav():
    st.sidebar.page_link("Home.py", label="Home", icon="🏠")


def AboutPageNav():
    st.sidebar.page_link("pages/30_About.py", label="About", icon="🧠")


#### ------------------------ President ------------------------
def PresidentHomeNav():
    st.sidebar.page_link(
        "pages/00_President_Home.py", label="President Home", icon="👤"
    )

#### ------------------------ Dean ------------------------
def DeanHomeNav():
    st.sidebar.page_link(
        "pages/30_Dean_Home.py", label="Dean Home", icon="📈"
    )

def DeanBudgetNav():
    st.sidebar.page_link(
        "pages/30_Dean_Home.py", label="Dean - Budget Overview", icon="📈"
    )

def DeanStudentsNav():
    st.sidebar.page_link(
        "pages/30_Dean_Home.py", label="Dean - Student Overview", icon="📈"
    )

def DeanCoursesNav():
    st.sidebar.page_link(
        "pages/30_Dean_Home.py", label="Dean - Courses Overview", icon="📈"
    )

def DeanAlumniNav():
    st.sidebar.page_link(
        "pages/30_Dean_Home.py", label="Dean - Alumni Overview", icon="📈"
    )


#### ------------------------ System Admin Role (maintenance) ------------------------
def MaintenancePageNav():
    st.sidebar.page_link("pages/10_Maintenance_Worker_Home.py", label="System Admin", icon="🖥️")
    st.sidebar.page_link(
        "pages/21_ML_Model_Mgmt.py", label="ML Model Management", icon="🏢"
    )

    
## ------------------------ Student ------------------------
def StudentHomeNav():
    st.sidebar.page_link(
        "pages/20_Student_Home.py", label="Student Home", icon="👤"
    )

def StudentScheduleNav():
    st.sidebar.page_link(
        "pages/24_Student_Schedule.py", label="Schedule", icon="📅"
    )

def InstrumentNav():
    st.sidebar.page_link(
        "pages/23_Instrument_Rental.py", label="Instruments", icon="🎷"
    )    

def StudentMaintenanceRequestNav():
    st.sidebar.page_link(
        "pages/21_Maintenance_Requests.py", label="Maintenance Request", icon="🔨"
    ) 

def ClubNav():
    st.sidebar.page_link(
        "pages/22_Student_clubs.py", label="Clubs", icon="🎉"
    ) 

#### ------------------------ Examples from Mark Fontenote ------------------------
def WorldBankVizNav():
    st.sidebar.page_link(
        "pages/01_World_Bank_Viz.py", label="World Bank Visualization", icon="🏦"
    )

def MapDemoNav():
    st.sidebar.page_link("pages/02_Map_Demo.py", label="Map Demonstration", icon="🗺️")

def ApiTestNav():
    st.sidebar.page_link("pages/12_API_Test.py", label="Test the API", icon="🛜")

def ClassificationNav():
    st.sidebar.page_link(
        "pages/13_Classification.py", label="Classification Demo", icon="🌺"
    )

# --------------------------------Links Function -----------------------------------------------
def SideBarLinks(show_home=False):
    """
    This function handles adding links to the sidebar of the app based upon the logged-in user's role, which was put in the streamlit session_state object when logging in.
    """

    # add a logo to the sidebar always
    st.sidebar.image("assets/logo.png", width=150)

    # If there is no logged in user, redirect to the Home (Landing) page
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
        st.switch_page("Home.py")

    if show_home:
        # Show the Home page link (the landing page)
        HomeNav()

    # Show the other page navigators depending on the users' role.
    if st.session_state["authenticated"]:

        # Show World Bank Link and Map Demo Link if the user is a political strategy advisor role.
        if st.session_state["role"] == "president":
            PresidentHomeNav()

        # If the user role is a dean, show the dean homepage
        if st.session_state["role"] == "dean":
            DeanHomeNav()
            DeanBudgetNav()
            DeanCoursesNav()
            DeanStudentsNav()
            DeanAlumniNav()

        # If the user is an administrator, give them access to the administrator pages
        if st.session_state["role"] == "maintenance worker":
            MaintenancePageNav()

        # If the user is an administrator, give them access to the administrator pages
        if st.session_state["role"] == "student":
            StudentHomeNav()
            StudentScheduleNav()
            InstrumentNav()
            StudentMaintenanceRequestNav()
            ClubNav()

    # Always show the About page at the bottom of the list of links
    AboutPageNav()

    if st.session_state["authenticated"]:
        # Always show a logout button if there is a logged in user
        if st.sidebar.button("Logout"):
            del st.session_state["role"]
            del st.session_state["authenticated"]
            st.switch_page("Home.py")
