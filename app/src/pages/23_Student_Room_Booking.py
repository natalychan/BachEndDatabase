import streamlit as st
import requests
from streamlit_extras.app_logo import add_logo
from modules.nav import SideBarLinks
from datetime import datetime

# Show appropriate sidebar links for the role of the currently logged in user
SideBarLinks()

# set the header of the page
st.header('Room Availability & Reservations')

# You can access the session state to make a more customized/personalized app experience
st.write(f"### Hi, {st.session_state['first_name']}.")


try:
    API_URL = f"http://web-api:4000/api/students/{student_id}/schedule"
    response = requests.get(API_URL)

    if response.status_code == 200:
        data = response.json()
        st.json(data)
            
        if data:
            df = pd.DataFrame(data)
            st.subheader("Student Schedule")
            st.dataframe(df, use_container_width=True)
            st.info(f"Class Schedule: {len(df)}")
        else:
            st.warning("No courses found - API returned empty array")
    else:
        st.error(f"Failed to fetch data: HTTP {response.status_code}")
        st.write(f"Response text: {response.text}")
except Exception as e:
    st.error(f"Error: {str(e)}")







# Create a form for NGO details
with st.form("instrument_rental_form"):
    st.subheader("Instrument Rental")

    # Required fields
    studentId = st.number_input("Student ID *", step=1, min_value=1, placeholder="Enter Student ID")
    instrumentId = st.number_input("Instrument ID *", step=1, min_value=1, placeholder="Enter Instrument ID")
    startDate = st.date_input("Date of Rental *")

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