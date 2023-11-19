
import streamlit as st
import calendar
import datetime

# Title of the app
st.title('Calendar View')

# Get today's date
today = datetime.date.today()

# Get the first day of the current month
first_day_of_month = today.replace(day=1)

# Get the last day of the current month
last_day_of_month = first_day_of_month.replace(
    month=first_day_of_month.month % 12 + 1,
    day=1) - datetime.timedelta(days=1)

# Create a header with the name of the month and year
st.header(first_day_of_month.strftime('%B %Y'))

# Create a layout to display the days of the current month
days_of_week = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

col_width = st.columns(7)
for i, day in enumerate(days_of_week):
    col_width[i].write(day)

# Create a list to hold the days of the month
days_list = []

# Fill in the matrix with the days of the month
for day in range(1, last_day_of_month.day + 1):
    date = first_day_of_month + datetime.timedelta(days=day - 1)
    week_day = date.weekday()  # Get the day of the week (0 - Monday, 6 - Sunday)
    days_list.append((date, week_day))

# Display the days of the month in the layout
for date, week_day in days_list:
    cell = st.columns(7)[week_day]
    cell.write(f"{date.day}")