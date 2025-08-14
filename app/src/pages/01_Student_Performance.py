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

# making the histogram to see the distribution of average GPA by college
st.subheader("Distribution of College Average GPA")
st.write("This histogram shows the distribution of average GPAs across different colleges. " \
"Each bar represents the number of colleges that fall within a specific average GPA range. " \
"The dashed line indicates the overall mean GPA across all colleges.")

# the with statment shows the code for this block above it 
with st.echo(code_location='above'):
    try:
        response = requests.get('http://web-api:4000/api/colleges/averages/gpa')
        if response.status_code == 200:
            data = response.json()

             # convert to pandas dataframe
            df = pd.DataFrame(data)
            df['average_gpa'] = pd.to_numeric(df['average_gpa'])

            # extract the average GPA
            gpa_values = []
            for gpa in df['average_gpa']:
                gpa_values.append(gpa)
            
            college_names = df['college'].tolist()
            
            # histogram!
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # bins
            n_bins = min(len(gpa_values), 16)  # to adjust bins based on data size
            counts, bins, patches = ax.hist(gpa_values, bins=n_bins, color="#80659eff", edgecolor='black', alpha=0.7)
            
            # labels, title, grid
            ax.set_xlabel('Average GPA')
            ax.set_ylabel('Number of Colleges')
            ax.set_title('Distribution of College Average GPA')
            ax.grid(True, alpha=0.3)
            
            # mean
            mean_gpa = df['average_gpa'].mean()
            ax.axvline(mean_gpa, color="#4a3c5aff", linestyle='--', 
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





# making the box plot to see the distribution of student GPAs by college
st.subheader("Distribution of Student GPAs by College")
st.write("This box plot illustrates the distribution of individual student GPAs within each college. " \
"Each box represents the IQR of GPAs for students in that college, along with the median GPA. " \
"The whiskers extend to 1.5 times the IQR, and any points outside this range are considered outliers.")

with st.echo(code_location='above'):
    try:
        response = requests.get('http://web-api:4000/api/students/gpas')
        if response.status_code == 200:
            data = response.json()

            # convert to dataframe
            df = pd.DataFrame(data)
            df['gpa'] = pd.to_numeric(df['gpa'])

            # box plot!
            fig, ax = plt.subplots(figsize=(12, 8))
            
            # get unique colleges
            colleges = df['college'].unique()
            gpa_by_college = []
            for college in colleges:
                college_gpas = df[df['college'] == college]['gpa'].tolist()
                gpa_by_college.append(college_gpas)
            
            # create box plot
            boxplot = ax.boxplot(gpa_by_college, labels=colleges, patch_artist=True)
            
            # labels, title, grid
            ax.set_xlabel('College')
            ax.set_ylabel('GPA')
            ax.set_title('GPA Distribution by College')
            ax.grid(True, alpha=0.3)
            
            # rotate x-axis labels if needed
            plt.xticks(rotation=45, ha='right')
            
            # colors!
            cmap = plt.cm.inferno
            colors = [cmap(i/len(colleges)) for i in range(len(colleges))] # gets list of colors

            for i in range(len(boxplot['boxes'])):
                boxplot['boxes'][i].set_facecolor(colors[i])
            
            # adjust layout to prevent label cutoff
            plt.tight_layout()
            
            st.pyplot(fig)
            
            # stats
            st.subheader("Summary Statistics by College")
            summary_stats = df.groupby('college')['gpa'].agg([
                'count', 'mean', 'median', 'std', 'min', 'max'
            ]).round(3)
            st.dataframe(summary_stats)
            
            # show data
            st.subheader("Individual Student GPAs by College")
            st.dataframe(df.sort_values(['college', 'gpa']))
            
        else:
            st.error(f"Failed to fetch data: HTTP {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        st.error(f"Error connecting to API: {str(e)}")
    except Exception as e:
        st.error(f"Error creating box plot: {str(e)}")
