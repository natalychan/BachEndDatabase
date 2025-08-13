import streamlit as st
import requests
from streamlit_extras.app_logo import add_logo
from modules.nav import SideBarLinks
from datetime import datetime

# Initialize sidebar
SideBarLinks()

st.title("Instrument Rentals")

# API endpoint
API_URL = "http://web-api:4000/rentals"

# Create a form for NGO details
with st.form("instrument_rental_form"):
    st.subheader("Instrument Rental")

    # Required fields
    studentId = st.text_input("Student ID *")
    instrumentId = st.text_input("Instrument ID *")
    startDate = st.number_input("Date of Rental *")

    # Form submission button
    submitted = st.form_submit_button("Submit Instrument Rental Request")

    if submitted:
        # Validate required fields
        if not all([startDate, instrumentId, studentId]):
            st.error("Please fill in all required fields marked with *")
        elif studentId < 0: # Assuming studentId should be a positive integer
            st.error("Student ID must be a positive integer")
        else:
            # Prepare the data for API
            rental_data = {
                "Student ID": int(studentId),
                "Instrument ID": int(instrumentId),
                "Start Date": datetime(startDate),
            }

            try:
                # Send POST request to API
                response = requests.post(API_URL, json=rental_data)

                if response.status_code == 201:
                    st.success("Instrument Rental submitted successfully!")
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
    st.switch_page("pages/20_Student_Home.py")