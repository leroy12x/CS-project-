import streamlit as st
import calendar

# Funktion zur Anzeige des Kalenders für den ausgewählten Monat
def display_monthly_calendar(year, month, tasks):
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
                tasks_for_day = tasks.get((year, month, day), [])
                task_info = "<br>".join([f"{task['time']}, {task['duration']}" for task in tasks_for_day])
                table += f"<td style='border: 1px solid black; padding: 8px; text-align: left; vertical-align: top;'>{day}<br>{task_info}</td>"
            else:
                table += "<td style='border: 1px solid black; padding: 8px;'></td>"
        table += "</tr>"

    table += "</table>"
    st.write(table, unsafe_allow_html=True)

# Funktion zur Anzeige des Taskmanagers
def display_task_manager():
    st.title("Taskmanager")
    task_date = st.date_input("Datum auswählen", key="task_date")
    task_time = st.time_input("Uhrzeit eingeben", key="task_time")
    task_duration = st.text_input("Dauer eingeben (z.B. 1 Stunde)", key="task_duration")
    task_description = st.text_input("Aufgabenbeschreibung eingeben", key="task_description")

    if st.button("Aufgabe hinzufügen"):
        task_info = {
            'time': str(task_time),
            'duration': task_duration,
            'description': task_description
        }
        tasks = st.session_state.get('tasks', {})
        date_key = (task_date.year, task_date.month, task_date.day)
        if date_key in tasks:
            tasks[date_key].append(task_info)
        else:
            tasks[date_key] = [task_info]
        st.session_state.tasks = tasks
        st.success(f"Aufgabe für {task_date} um {task_time} hinzugefügt!")

        st.experimental_rerun()

# Navigation zwischen den Seiten
def main():
    st.sidebar.title("Navigation")
    app_mode = st.sidebar.selectbox(
        "Wähle eine Seite",
        ["Kalender anzeigen", "Taskmanager"]
    )

    if app_mode == "Kalender anzeigen":
        year = st.number_input("Jahr eingeben", min_value=1900, max_value=2100, value=2023, key="calendar_year")
        month_names = [
            "Januar", "Februar", "März", "April",
            "Mai", "Juni", "Juli", "August",
            "September", "Oktober", "November", "Dezember"
        ]
        selected_month = st.selectbox("Monat auswählen", month_names, key="selected_month")
        month_index = month_names.index(selected_month) + 1
        tasks = st.session_state.get('tasks', {})
        display_monthly_calendar(year, month_index, tasks)
    elif app_mode == "Taskmanager":
        display_task_manager()

if __name__ == "__main__":
    main()
