import streamlit as st
import requests
import pandas as pd
from streamlit_extras.app_logo import add_logo
from modules.nav import SideBarLinks
from datetime import datetime, date, timedelta

# Initialize sidebar
SideBarLinks()

st.title("Instrument Rentals")
try:
    API_URL_viewing = "http://api:4000/api/instruments"
    response = requests.get(API_URL_viewing, timeout=10)

    if response.status_code == 200:
        data = response.json()
        if data:
            df = pd.DataFrame(data)
            df.rename(columns={"instrumentId": "Instrument ID"}, inplace=True)
            if "isAvailable" in df.columns:
                df = df.drop(columns=["isAvailable"])
            st.subheader("Available Instruments for Rental")
            st.dataframe(df, use_container_width=True, hide_index=True)
            st.info(f"Total Available Instruments: {len(df)}")
        else:
            st.warning("No instruments found — API returned an empty list.")
    else:
        st.error(f"Failed to fetch instruments: {getattr(response, 'text', 'Unknown error')} (status={response.status_code})")

except requests.exceptions.RequestException as e:
    st.error(f"Error connecting to the API: {e}")
    st.info("Please ensure the API server is running")
# API endpoint
API_URL = "http://api:4000/api/rentals"

# Create a form for NGO details
with st.form("instrument_rental_form"):
    st.subheader("Instrument Rental")
    studentId = st.session_state.get("student_id")  # Pre-fill from session state
    # Required fields
    # studentId = st.number_input("Student ID *", step=1, min_value=1, placeholder="Enter Student ID")
    instrumentId = st.number_input("Instrument ID *", step=1, min_value=1, placeholder="Enter Instrument ID")
    startDate = st.date_input("Date of Rental *")

    # Form submission button
    submitted = st.form_submit_button("Submit Instrument Rental Request")

    if submitted:
        # Validate required fields
        if not all([startDate, instrumentId]):
            st.error("Please fill in all required fields marked with *")
        else:

            returnDate = startDate + timedelta(days=30)
            # Prepare the data for API
            rental_data = {
                "studentId": int(studentId),       # was studentID
                "instrumentId": int(instrumentId), # was instrumentID
                "startDate": startDate.strftime("%Y-%m-%d"),
                "returnDate": returnDate.strftime("%Y-%m-%d"),
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
                        f"Failed to submit request: {response.text}"
                    )

            except requests.exceptions.RequestException as e:
                st.error(f"Error connecting to the API: {str(e)}")
                st.info("Please ensure the API server is running")

# Add a button to return to the NGO Directory
if st.button("Return to Student Home"):
    st.switch_page("pages/20_Student_Home.py")



