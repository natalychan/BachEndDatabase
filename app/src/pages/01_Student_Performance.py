import logging
logger = logging.getLogger(__name__)
import pandas as pd
import streamlit as st
from streamlit_extras.app_logo import add_logo
import matplotlib.pyplot as plt
import numpy as np
import plotly.express as px
from modules.nav import SideBarLinks
import requests

# Call the SideBarLinks from the nav module in the modules directory
SideBarLinks()

# set the header of the page
st.header('Student Performance Data')

# You can access the session state to make a more customized/personalized app experience
st.write(f"### Hi, {st.session_state['first_name']}.")


# the with statment shows the code for this block above it 
with st.echo(code_location='above'):
    try:
        response = requests.get('http://your-api-base-url/api/colleges/averages/gpa')
        if response.status_code == 200:
            data = response.json()
            
            # convert to pandas dataframe
            df = pd.DataFrame(data)
            
            # extract the average GPA
            gpa_values = df['average_gpa'].tolist()
            college_names = df['college'].tolist()
            
            # histogram!
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # bins
            n_bins = min(len(gpa_values), 16)  # to adjust bins based on data size
            counts, bins, patches = ax.hist(gpa_values, bins=n_bins, edgecolor='black', alpha=0.7)
            
            # labels, title, grid
            ax.set_xlabel('Average GPA')
            ax.set_ylabel('Number of Colleges')
            ax.set_title('Distribution of Average GPA by College')
            ax.grid(True, alpha=0.3)
            
            # mean
            mean_gpa = df['average_gpa'].mean()
            ax.axvline(mean_gpa, color='red', linestyle='--', 
                      label=f'Overall Mean: {mean_gpa:.2f}')
            ax.legend()
            
            st.pyplot(fig)
            
            # show the data table below the histogram
            st.subheader("College GPA Data")
            st.dataframe(df)
            
        else:
            st.error(f"Failed to fetch data: HTTP {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        st.error(f"Error connecting to API: {str(e)}")
    except Exception as e:
        st.error(f"Error creating histogram: {str(e)}")


with st.echo(code_location='above'):
    try:
        API_URL = "http://web-api:4000/api/students/gpas"
        response = requests.get(API_URL)
        if response.status_code == 200:
            data = response.json()

            # extract GPA values
            gpa_values = [row['gpa'] for row in data]
            
            # histogram!
            fig, ax = plt.subplots()
            ax.hist(gpa_values, bins=16, color="#ffae00ff", edgecolor="#e09900ff", alpha=0.7)
            
            # titles, labels, grid
            ax.set_xlabel('Student GPA')
            ax.set_ylabel('Number of Students')
            ax.set_title('Distribution of Student GPAs')
            ax.grid(True, alpha=0.3)

            st.pyplot(fig)
            
        else:
            st.error(f"Failed to fetch data: HTTP {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        st.error(f"Error connecting to API: {str(e)}")
        
    except Exception as e:
        st.error(f"Error creating histogram: {str(e)}")
