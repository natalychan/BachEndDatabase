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
    address = st.text_input("Maintenance Location Address *")
    problemType = st.text_input("Briefly Describe Maintenance Issue *")
    studentId = st.number_input("Student ID *", step=1, min_value=1, placeholder="Enter Student ID")

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
                "Student ID": studentId,
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


#view work requests submitted by student
try:
    # Display maintenance requests for current student
    user_id = st.session_state.get('student_id') 
    st.write(f"### My Maintenance Requests - Student ID: {user_id}")
    
    if user_id:
        API_URL = f"http://web-api:4000/api/maintenance-requests/student/{user_id}"
        response = requests.get(API_URL)
        
        if response.status_code == 200:
            data = response.json()
            
            if data:
                df = pd.DataFrame(data)
                
                # Rename columns to capitalize words
                df.rename(columns={
                    'orderId': 'Order ID',
                    'address': 'Address',
                    'problemType': 'Problem Type',
                    'state': 'State',
                    'submitted': 'Submitted',
                    'description': 'Description',
                    'staffId': 'Staff ID',
                    'firstName': 'First Name',
                    'lastName': 'Last Name',
                    'tools': 'Tools'
                }, inplace=True)
                
                st.dataframe(df, use_container_width=True, hide_index=True)
                st.info(f"Total Requests: {len(df)}")
            else:
                st.warning("No maintenance requests found")
        else:
            st.error(f"Failed to fetch data: HTTP {response.status_code}")
    else:
        st.error("User ID not found in session")

except Exception as e:
    st.error(f"Error: {str(e)}")

# Add a button to return to the Student Home
if st.button("Return to Student Home"):
    st.switch_page("pages/20_Student_Home.py")