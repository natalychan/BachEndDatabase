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
    arr = np.random.normal(1, 1, size=100)
    test_plot, ax = plt.subplots()
    ax.hist(arr, bins=20)

    st.pyplot(test_plot)


API_URL = "http://web-api:4000/colleges/averages/gpa"
with st.echo(code_location='above'):
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
        st.info("Please ensure the API server is running on http://web-api:4000")
    except Exception as e:
        st.error(f"Error creating histogram: {str(e)}")