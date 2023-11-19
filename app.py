
import streamlit as st
import calendar
import datetime

# Title of the app
st.title('Calendar View')

# Get today's date
today = datetime.date.today()

# Get the first day of the current month
first_day_of_month = today.replace(day=1)

# Get the calendar object for the current month
cal = calendar.monthcalendar(today.year, today.month)

# Display the header with the name of the month and year
st.header(first_day_of_month.strftime('%B %Y'))

# Display the days of the week
days_of_week = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
st.markdown(" | ".join(days_of_week))

# Display the days of the month
for week in cal:
    row = ""
    for day in week:
        if day == 0:
            row += "   | "  # If the day is 0, display an empty cell
        else:
            row += f"{day:2d} | "  # Display the day with padding
    st.markdown(row)