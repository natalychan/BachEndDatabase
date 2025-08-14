import logging
logger = logging.getLogger(__name__)
import pandas as pd
import streamlit as st
from streamlit_extras.app_logo import add_logo
from modules.nav import SideBarLinks
import requests

# Call the SideBarLinks from the nav module in the modules directory
SideBarLinks()

st.title(f"Welcome System Admin, {st.session_state['first_name']}.")
st.write('')
st.write('')
st.write('### What would you like to do?')

try:
    # Filters
    col1, col2 = st.columns(2)
    with col1:
        college_filter = st.text_input("Filter by College (optional)")
    with col2:
        year_filter = st.text_input("Filter by Year (optional)")
    
    # Build API URL with filters
    API_URL = "http://web-api:4000/api/students"
    params = {}
    if college_filter:
        params['college'] = college_filter
    if year_filter:
        params['year'] = year_filter
    
    response = requests.get(API_URL, params=params)
    
    if response.status_code == 200:
        data = response.json()
        
        if data:
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True)
            st.info(f"Total Students: {len(df)}")
        else:
            st.warning("No students found")
    else:
        st.error(f"Failed to fetch data: HTTP {response.status_code}")

    # Create student
    st.subheader("Create Student")
    user_id = st.number_input("User ID", min_value=1, step=1)
    year = st.text_input("Year")
    housing_status = st.text_input("Housing Status")
    race = st.text_input("Race")
    income = st.text_input("Income")
    origin = st.text_input("Origin")
    college = st.text_input("College")
    advisor = st.text_input("Advisor")
    
    if st.button("Create Student"):
        if user_id:
            student_data = {
                "userId": user_id,
                "year": year,
                "housingStatus": housing_status,
                "race": race,
                "income": income,
                "origin": origin,
                "college": college,
                "advisor": advisor
            }
            create_response = requests.post(API_URL, json=student_data)
            if create_response.status_code == 201:
                st.success("Student created successfully")
                st.rerun()
            else:
                st.error(f"Failed to create student: HTTP {create_response.status_code}")
        else:
            st.warning("Please enter a user ID")

    # Update student
    st.subheader("Update Student")
    update_user_id = st.number_input("User ID to Update", min_value=1, step=1)
    update_year = st.text_input("New Year")
    update_housing = st.text_input("New Housing Status")
    update_race = st.text_input("New Race")
    update_income = st.text_input("New Income")
    update_origin = st.text_input("New Origin")
    update_college = st.text_input("New College")
    update_advisor = st.text_input("New Advisor")
    
    if st.button("Update Student"):
        if update_user_id:
            update_data = {}
            if update_year: update_data['year'] = update_year
            if update_housing: update_data['housingStatus'] = update_housing
            if update_race: update_data['race'] = update_race
            if update_income: update_data['income'] = update_income
            if update_origin: update_data['origin'] = update_origin
            if update_college: update_data['college'] = update_college
            if update_advisor: update_data['advisor'] = update_advisor
            
            if update_data:
                update_response = requests.patch(f"{API_URL}/{update_user_id}", json=update_data)
                if update_response.status_code == 200:
                    st.success("Student updated successfully")
                    st.rerun()
                else:
                    st.error(f"Failed to update student: HTTP {update_response.status_code}")
            else:
                st.warning("No fields to update")
        else:
            st.warning("Please enter a user ID")

except Exception as e:
    st.error(f"Error: {str(e)}")