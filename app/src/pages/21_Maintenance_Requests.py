import streamlit as st
import requests
from streamlit_extras.app_logo import add_logo
from modules.nav import SideBarLinks

# Initialize sidebar
SideBarLinks()

st.title("Submit a Maintenance Request")

# API endpoint
API_URL = "http://web-api:4000/Maintenance-Requests"

# Create a form for NGO details
with st.form("submit_maintenance_request_form"):
    st.subheader("Maintenance Information")

    # Required fields
    address = st.text_input("Maintenace Location Address *")
    problemType = st.text_input("Briefly Describe Maintenance Issue *")
    studentId = st.number_input("Student ID *")

    # Form submission button
    submitted = st.form_submit_button("Submit Maintenance Request")

    if submitted:
        # Validate required fields
        if not all([address, problemType, studentId]):
            st.error("Please fill in all required fields marked with *")
        else:
            # Prepare the data for API
            maintenance_req_data = {
                "Address": address,
                "Problem Type": problemType,
                "Student ID": int(studentId),
            }

            try:
                # Send POST request to API
                response = requests.post(API_URL, json=maintenance_req_data)

                if response.status_code == 201:
                    st.success("Maintenance request submitted successfully!")
                    # Clear the form
                    st.rerun()
                else:
                    st.error(
                        f"Failed to submit request: {response.json().get('error', 'Unknown error')}"
                    )

            except requests.exceptions.RequestException as e:
                st.error(f"Error connecting to the API: {str(e)}")
                st.info("Please ensure the API server is running")

# Add a button to return to the NGO Directory
if st.button("Return to Student Home"):
    st.switch_page("pages/05_Student_Home.py")