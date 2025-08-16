import logging
logger = logging.getLogger(__name__)
import pandas as pd
import streamlit as st
from streamlit_extras.app_logo import add_logo
from modules.nav import SideBarLinks
import requests

# Call the SideBarLinks from the nav module in the modules directory
SideBarLinks()

# set the header of the page
st.header('Maintenance Requests')

# You can access the session state to make a more customized/personalized app experience
st.write(f"### Hi, {st.session_state['first_name']}.")

st.write("Here you can view and manage maintenance requests.")

try:
   # Display maintenance requests
    user_id = st.session_state.get('user_id')
    st.write(f"Debug: Looking for requests for user_id: {user_id}")  
    API_URL = f"http://web-api:4000/api/maintenance-requests/get/{user_id}"
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

    # Update request form
    st.subheader("Update Request")
    request_id = st.number_input("Order ID", min_value=1, step=1)
    address = st.text_input("Address")
    problem_type = st.text_input("Problem Type")
    description = st.text_area("Description")
    
    if st.button("Update Request"):
        update_data = {}
        if address: update_data['address'] = address
        if problem_type: update_data['problemType'] = problem_type
        if description: update_data['description'] = description
        
        if update_data:
            update_response = requests.patch(f"http://web-api:4000/api/maintenance-requests/update/{request_id}", json=update_data)
            if update_response.status_code == 200:
                st.success("Request updated successfully")
                st.rerun()
            else:
                st.error(f"Failed to update: HTTP {update_response.status_code}")
        else:
            st.warning("No fields to update")

    # Delete request
    st.subheader("Delete Request")
    delete_id = st.number_input("Order ID to Delete", min_value=1, step=1)
    
    if st.button("Delete Request"):
        delete_response = requests.delete(f"http://web-api:4000/api/maintenance-requests/update/{request_id}", json=update_data)
        if delete_response.status_code == 204:
            st.success("Request deleted successfully")
            st.rerun()
        else:
            st.error(f"Failed to delete: HTTP {delete_response.status_code}")

    # Attach tool to request
    st.subheader("Attach Tool")
    st.write("!Make sure the tool to be attched actually exists in tools table!")
    attach_request_id = st.number_input("Order ID for Tool", min_value=1, step=1)
    tool_name = st.text_input("Tool Name")
    
    if st.button("Attach Tool"):
        if tool_name:
            tool_data = {"tool": tool_name}
            attach_response = requests.post(f"http://web-api:4000/api/maintenance-requests/{attach_request_id}/post/tools", json=tool_data)
            if attach_response.status_code == 201:
                st.success("Tool attached successfully")
                st.rerun()
            else:
                st.error(f"Failed to attach tool: HTTP {attach_response.status_code}")
        else:
            st.warning("Please enter a tool name")

    # Detach tool from request
    st.subheader("Detach Tool")
    detach_request_id = st.number_input("Order ID for Detach", min_value=1, step=1)
    detach_tool_name = st.text_input("Tool Name to Detach")
    
    if st.button("Detach Tool"):
        if detach_tool_name:
            detach_response = requests.delete(f"http://web-api:4000/api/maintenance-requests/{detach_request_id}/delete/tools/{detach_tool_name}")
            if detach_response.status_code == 204:
                st.success("Tool detached successfully")
                st.rerun()
            else:
                st.error(f"Failed to detach tool: HTTP {detach_response.status_code}")
        else:
            st.warning("Please enter a tool name")

except Exception as e:
    st.error(f"Error: {str(e)}")