
import streamlit as st
import calendar

def display_monthly_calendar(year, month):
    cal = calendar.monthcalendar(year, month)
    month_name = calendar.month_name[month]

    st.title(f"Kalender für {month_name} {year}")

    # Erstelle eine leere Tabelle für den Kalender
    table = "<table style='width:100%; border-collapse: collapse;'>"

    # Tabellenkopf mit den Wochentagen
    table += "<tr>"
    for day in ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]:
        table += f"<th style='border: 1px solid black; padding: 8px; text-align: center;'>{day}</th>"
    table += "</tr>"

    # Darstellung des Kalenders
    for week in cal:
        table += "<tr>"
        for day in week:
            if day != 0:
                table += f"<td style='border: 1px solid black; padding: 8px; text-align: center;'>{day}</td>"
            else:
                table += "<td style='border: 1px solid black; padding: 8px;'></td>"
        table += "</tr>"

    table += "</table>"
    st.write(table, unsafe_allow_html=True)

# Streamlit App
st.title("Monatskalender")
year = st.number_input("Jahr eingeben", min_value=1900, max_value=2100, value=2023)
month = st.slider("Monat auswählen", 1, 12, 1)

display_monthly_calendar(year, month)
def display_settings():
    st.title("Einstellungen")
    # Hier füge den Code für die Einstellungsseite ein

# Navigation zwischen den Seiten
def main():
    st.sidebar.title("Navigation")
    app_mode = st.sidebar.selectbox(
        "Wähle eine Seite",
        ["Kalender anzeigen", "Einstellungen"]
    )

    if app_mode == "Kalender anzeigen":
        display_calendar()
    elif app_mode == "Einstellungen":
        display_settings()

if __name__ == "__main__":
    main()
