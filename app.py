
import streamlit as st
import calendar

def display_monthly_calendar(year, month):
    cal = calendar.monthcalendar(year, month)
    month_name = calendar.month_name[month]

    st.title(f"Kalender für {month_name} {year}")

    col_width = 50

    # Tabellenkopf mit den Wochentagen
    st.write("|".join(["Mo".center(col_width), "Di".center(col_width), "Mi".center(col_width), "Do".center(col_width), "Fr".center(col_width), "Sa".center(col_width), "So".center(col_width)]))
    st.write("-" * (col_width * 7))

    # Darstellung des Kalenders
    for week in cal:
        week_str = "|".join([str(day).center(col_width) if day != 0 else " ".center(col_width) for day in week])
        st.write(week_str)

# Streamlit App
st.title("Monatskalender")
year = st.number_input("Jahr eingeben", min_value=1900, max_value=2100, value=2023)
month = st.slider("Monat auswählen", 1, 12, 1)

display_monthly_calendar(year, month)