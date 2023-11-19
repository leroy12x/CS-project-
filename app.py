
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

# Calculate the number of days in the current month
num_days = (last_day_of_month - first_day_of_month).days + 1

# Create a list to hold the days of the week
days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

# Create a layout to display the days of the current month
col_width = st.columns(7)
for i, day in enumerate(days_of_week):
    col_width[i].write(day)

days_list = [[] for _ in range(6)]  # A 6x7 matrix to hold the days of the month
counter = 0

# Fill in the matrix with the days of the month
for day in range(1, num_days + 1):
    date = first_day_of_month + datetime.timedelta(days=day - 1)
    week_day = date.weekday()  # Get the day of the week (0 - Monday, 6 - Sunday)
    days_list[counter].append(date.strftime('%d'))
    if week_day == 6:  # If it's Sunday, move to the next row
        counter += 1

# Display the days of the month in the layout
for week in days_list:
    for day in week:
        st.write(day)