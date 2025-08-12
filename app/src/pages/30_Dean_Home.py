import logging
logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks

import pandas as pd
from streamlit_extras.app_logo import add_logo
import matplotlib.pyplot as plt
import numpy as np
import plotly.express as px
import requests

st.set_page_config(layout = 'wide')

# Show appropriate sidebar links for the role of the currently logged in user
SideBarLinks()


st.title(f"Welcome Dean, {st.session_state['first_name']}.")
#st.write('')
#st.write('')
#st.write('### What would you like to do today?')

#change all of these to be appropriate for the dean
#if st.button('View Demographic Data Visualization', 
#             type='primary',
#             use_container_width=True):
#  st.switch_page('pages/01_World_Bank_Viz.py')

#if st.button('View Student Performance Data Visualization', 
#             type='primary',
#             use_container_width=True):
#  st.switch_page('pages/02_Map_Demo.py')


# set the header of the page
st.header('Dean Overview')

# the with statment shows the code for this block above it 
#with st.echo(code_location='above'):
#    arr = np.random.normal(1, 1, size=100)
#    test_plot, ax = plt.subplots()
#    ax.hist(arr, bins=20)
#    st.pyplot(test_plot)

left_top, right_top = st.columns(2, gap="large")
left_bottom, right_bottom = st.columns(2, gap="large")


with right_top:
    API_URL = "http://api:4000/api/colleges/averages/gpa"
    #with st.echo(code_location='above'):
    try:
        response = requests.get(API_URL)
        if response.status_code == 200:
            data = response.json()
                
            #convert to pandas dataframe
            df = pd.DataFrame(data)
                
            #extract GPA values
            gpa_values = [row['average_gpa'] for row in data]
                
            #histogram!
            fig, ax = plt.subplots()
            ax.hist(gpa_values, bins=20, color="#75CEEF", edgecolor='black', alpha=0.7)
            
            #labels & title
            ax.set_xlabel('Average GPA')
            ax.set_ylabel('Number of Colleges')
            ax.set_title('Distribution of Average GPA by College')
                
            st.pyplot(fig)
                
        else:
            st.error(f"Failed to fetch data: HTTP {response.status_code}")
                
    except requests.exceptions.RequestException as e:
        st.error(f"Error connecting to API: {str(e)}")
        st.info("Please ensure the API server is running on http://api:4000")
    except Exception as e:
        st.error(f"Error creating histogram: {str(e)}")

with left_top:
    API_URL = "http://api:4000/api/colleges/averages/gpa"
    #with st.echo(code_location='above'):
    try:
        response = requests.get(API_URL)
        if response.status_code == 200:
            data = response.json()
                
            #convert to pandas dataframe
            df = pd.DataFrame(data)
                
            #extract GPA values
            gpa_values = [row['average_gpa'] for row in data]
                
            #histogram!
            fig, ax = plt.subplots()
            ax.hist(gpa_values, bins=20, color="#75CEEF", edgecolor='black', alpha=0.7)
            
            #labels & title
            ax.set_xlabel('Average GPA')
            ax.set_ylabel('Number of Colleges')
            ax.set_title('Distribution of Average GPA by College')
                
            sub_lt, sub_rt = st.columns(2, gap="medium")
            sub_lb, sub_rb = st.columns(2, gap="medium")

            with sub_lt:
                st.write("Budget KPI 1")
            with sub_rt:
                st.write("Budget KPI 2")
            with sub_lb:
                st.write("Budget KPI 3")
            with sub_rb:
                st.write("Budget KPI 4")            
                
        else:
            st.error(f"Failed to fetch data: HTTP {response.status_code}")
                
    except requests.exceptions.RequestException as e:
        st.error(f"Error connecting to API: {str(e)}")
        st.info("Please ensure the API server is running on http://api:4000")
    except Exception as e:
        st.error(f"Error creating histogram: {str(e)}")

with left_bottom:
    API_URL = "http://api:4000/api/colleges/averages/gpa"
    #with st.echo(code_location='above'):
    try:
        response = requests.get(API_URL)
        if response.status_code == 200:
            data = response.json()
                
            #convert to pandas dataframe
            df = pd.DataFrame(data)
                
            #extract GPA values
            gpa_values = [row['average_gpa'] for row in data]
                
            #histogram!
            fig, ax = plt.subplots()
            ax.hist(gpa_values, bins=20, color="#75CEEF", edgecolor='black', alpha=0.7)
            
            #labels & title
            ax.set_xlabel('Average GPA')
            ax.set_ylabel('Number of Colleges')
            ax.set_title('Distribution of Average GPA by College')
                
            st.pyplot(fig)
                
        else:
            st.error(f"Failed to fetch data: HTTP {response.status_code}")
                
    except requests.exceptions.RequestException as e:
        st.error(f"Error connecting to API: {str(e)}")
        st.info("Please ensure the API server is running on http://api:4000")
    except Exception as e:
        st.error(f"Error creating histogram: {str(e)}")

with right_bottom:
    API_URL = "http://api:4000/api/colleges/averages/gpa"
    #with st.echo(code_location='above'):
    try:
        response = requests.get(API_URL)
        if response.status_code == 200:
            data = response.json()
                
            #convert to pandas dataframe
            df = pd.DataFrame(data)
                
            #extract GPA values
            gpa_values = [row['average_gpa'] for row in data]
                
            #histogram!
            fig, ax = plt.subplots()
            ax.hist(gpa_values, bins=20, color="#75CEEF", edgecolor='black', alpha=0.7)
            
            #labels & title
            ax.set_xlabel('Average GPA')
            ax.set_ylabel('Number of Colleges')
            ax.set_title('Distribution of Average GPA by College')
                
            st.pyplot(fig)
                
        else:
            st.error(f"Failed to fetch data: HTTP {response.status_code}")
                
    except requests.exceptions.RequestException as e:
        st.error(f"Error connecting to API: {str(e)}")
        st.info("Please ensure the API server is running on http://api:4000")
    except Exception as e:
        st.error(f"Error creating histogram: {str(e)}")