print ('Hello Wolrd ')
import streamlit as st
# Title of the app
st.title('My Streamlit App')

# Adding text to the app
st.write('Welcome to my first Streamlit app!')

# Adding a slider widget
slider_value = st.slider('Select a value', 0, 100, 50)

# Displaying the value selected on the slider
st.write('You selected:', slider_value)