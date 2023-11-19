print ('Hello Wolrd ')
import streamlit as st
import datetime

# Title of the app
st.title('Task Manager')

# Date selection
selected_date = st.date_input('Select a date', datetime.date.today())

# Task input
task = st.text_input('Enter task description')

# Button to add task
if st.button('Add Task'):
    # Store tasks for different dates
    if 'tasks' not in st.session_state:
        st.session_state.tasks = {}
