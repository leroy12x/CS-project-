
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

# Liste der Monate
month_names = [
    "Januar", "Februar", "März", "April",
    "Mai", "Juni", "Juli", "August",
    "September", "Oktober", "November", "Dezember"
]

selected_month = st.selectbox("Monat auswählen", month_names)

# Index des ausgewählten Monats im Array der Monatsnamen
month_index = month_names.index(selected_month) + 1

display_monthly_calendar(year, month_index)
def display_task_manager():
    st.title("Taskmanager")
    task_date = st.date_input("Datum auswählen")
    task_description = st.text_input("Aufgabenbeschreibung eingeben")

    if st.button("Aufgabe hinzufügen"):
        # Hier könntest du den Code einfügen, um die Aufgabe zu speichern oder zu verarbeiten
        st.success(f"Aufgabe für {task_date}: '{task_description}' hinzugefügt!")

# Navigation zwischen den Seiten
def main():
    st.sidebar.title("Navigation")
    app_mode = st.sidebar.selectbox(
        "Wähle eine Seite",
        ["Kalender anzeigen", "Taskmanager"]
    )

    if app_mode == "Kalender anzeigen":
        year = st.number_input("Jahr eingeben", min_value=1900, max_value=2100, value=2023)
        month_names = [
            "Januar", "Februar", "März", "April",
            "Mai", "Juni", "Juli", "August",
            "September", "Oktober", "November", "Dezember"
        ]
        selected_month = st.selectbox("Monat auswählen", month_names)
        month_index = month_names.index(selected_month) + 1
        display_monthly_calendar(year, month_index)
    elif app_mode == "Taskmanager":
        display_task_manager()

if __name__ == "__main__":
    main()
