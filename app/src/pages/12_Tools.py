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
st.header('Tools')

# You can access the session state to make a more customized/personalized app experience
st.write(f"### Hi, {st.session_state['first_name']}, here's your tools inventory.")


try:
    # Display tools
    API_URL = "http://web-api:4000/api/tools"
    response = requests.get(API_URL)
    
    if response.status_code == 200:
        data = response.json()
        
        if data:
            df = pd.DataFrame(data)

            # Rename columns to capitalize words
            df.rename(columns={
                    'productName': 'Product Name',
                'amount': 'Amount'
                }, inplace=True)
            
            st.dataframe(df, use_container_width=True, hide_index=True)
            st.info(f"Total Tools: {len(df)}")
        else:
            st.warning("No tools found")
    else:
        st.error(f"Failed to fetch data: HTTP {response.status_code}")

    # Create new tool
    st.subheader("Create Tool")
    product_name = st.text_input("Product Name")
    amount = st.number_input("Amount", min_value=0, step=1)
    
    if st.button("Create Tool"):
        if product_name:
            tool_data = {"productName": product_name, "amount": amount}
            create_response = requests.post(API_URL, json=tool_data)
            if create_response.status_code == 201:
                st.success("Tool created successfully")
                st.rerun()
            else:
                st.error(f"Failed to create tool: HTTP {create_response.status_code}")
        else:
            st.warning("Please enter a product name")

    # Update tool
    st.subheader("Update Tool")
    update_product_name = st.text_input("Product Name to Update")
    new_amount = st.number_input("New Amount", min_value=0, step=1)
    
    if st.button("Update Tool"):
        if update_product_name:
            update_data = {"amount": new_amount}
            update_response = requests.put(f"{API_URL}/{update_product_name}", json=update_data)
            if update_response.status_code == 200:
                st.success("Tool updated successfully")
                st.rerun()
            else:
                st.error(f"Failed to update tool: HTTP {update_response.status_code}")
        else:
            st.warning("Please enter a product name")

    # Delete tool
    st.subheader("Delete Tool")
    delete_product_name = st.text_input("Product Name to Delete")
    
    if st.button("Delete Tool"):
        if delete_product_name:
            delete_response = requests.delete(f"{API_URL}/{delete_product_name}")
            if delete_response.status_code == 204:
                st.success("Tool deleted successfully")
                st.rerun()
            else:
                st.error(f"Failed to delete tool: HTTP {delete_response.status_code}")
        else:
            st.warning("Please enter a product name")

except Exception as e:
    st.error(f"Error: {str(e)}")