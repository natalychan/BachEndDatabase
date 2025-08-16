import logging
logger = logging.getLogger(__name__)

import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date

from streamlit_extras.app_logo import add_logo
from modules.nav import SideBarLinks

# Sidebar links
SideBarLinks()

# Header & greeting
st.header("Room Availability & Reservations")
st.write(f"### Hi, {st.session_state['first_name']}.")

# -------------------------------
# Availability (read-only)
# -------------------------------
try:
    API_URL_viewing = "http://api:4000/api/classrooms"
    response = requests.get(API_URL_viewing, timeout=10)

    if response.status_code == 200:
        data = response.json()
        if data:
            df = pd.DataFrame(data)
            df.rename(columns={"roomNumber": "Room Number"}, inplace=True)
            if "lastMaintained" in df.columns:
                df = df.drop(columns=["lastMaintained"])
            st.subheader("Available Classrooms for Booking")
            st.dataframe(df, use_container_width=True, hide_index=True)
            st.info(f"Total Available Classrooms: {len(df)}")
        else:
            st.warning("No classrooms found — API returned an empty list.")
    else:
        st.error(f"Failed to fetch classrooms: {getattr(response, 'text', 'Unknown error')} (status={response.status_code})")

except requests.exceptions.RequestException as e:
    st.error(f"Error connecting to the API: {e}")
    st.info("Please ensure the API server is running")

# -------------------------------
# Booking Form
# -------------------------------
with st.form("Classroom Booking Form"):
    st.subheader("Classroom Booking")

    API_URL = "http://api:4000/api/reserves"

    # Required fields

    roomNumber = st.number_input("Room Number *", step=1, min_value=1, placeholder="Enter Room Number")
    startTime = st.time_input("Reservation Start Time *")
    endTime = st.time_input("Reservation End Time *")

    submitted = st.form_submit_button("Classroom Booking Request")
    studentID = st.session_state.get("student_id")  # Pre-fill from session state
    if submitted:
        # Validate
        if not all([startTime, roomNumber, studentID]):
            st.error("Please fill in all required fields marked with *")
        elif startTime >= endTime:
            st.error("Start time must be before end time")
        else:
            # Prepare payload — keys must match backend: startTime / endTime (camelCase)
            start_dt = datetime.combine(date.today(), startTime)
            end_dt = datetime.combine(date.today(), endTime)
            rental_data = {
                "studentID": int(studentID),
                "roomNumber": int(roomNumber),
                "startTime": start_dt.isoformat(),
                "endTime": end_dt.isoformat(),
            }

            try:
                response = requests.post(API_URL, json=rental_data, timeout=10)

                if response.status_code == 201:
                    st.success("Classroom booking submitted successfully!")
                    st.rerun()
                else:
                    # Do not parse JSON on failure; show raw text & status
                    st.error(f"Failed to submit request: please check your inputs. Remember that the room must exist.")

            except requests.exceptions.RequestException as e:
                st.error(f"Error connecting to the API: {e}")
                st.info("Please ensure the API server is running")

# Navigation
if st.button("Return to Student Home"):
    st.switch_page("pages/20_Student_Home.py")
