import streamlit as st
import requests
from streamlit_extras.app_logo import add_logo
from modules.nav import SideBarLinks

# Initialize sidebar
SideBarLinks()

st.title("Submit a Maintenance Request")

# Create new maintenance request
try:
    st.write("### Submit New Maintenance Request")
    
    user_id = st.session_state.get('student_id')
    
    if user_id:
        with st.form("maintenance_request_form"):
            address = st.text_input("Address", placeholder="Enter the address where maintenance is needed")
            problem_type = st.selectbox("Problem Type", 
                                      ["Plumbing", "Electrical", "HVAC", "Carpentry", "Painting", "Other"])
            description = st.text_area("Description", 
                                     placeholder="Describe the maintenance issue in detail")
            
            submitted = st.form_submit_button("Submit Request")
            
            if submitted:
                if address and problem_type and description:
                    request_data = {
                        'address': address,
                        'problemType': problem_type,
                        'description': description,
                        'studentId': user_id
                    }
                    
                    API_URL = "http://web-api:4000/api/maintenance-requests"
                    response = requests.post(API_URL, json=request_data)
                    
                    if response.status_code == 201:
                        data = response.json()
                        st.success(f"Maintenance request submitted successfully! Order ID: {data['orderId']}")
                        st.rerun()  # Refresh to show new request in list
                    else:
                        st.error(f"Failed to submit request: HTTP {response.status_code}")
                else:
                    st.error("Please fill in all required fields")
    else:
        st.error("User ID not found in session")

except Exception as e:
    st.error(f"Error: {str(e)}")


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