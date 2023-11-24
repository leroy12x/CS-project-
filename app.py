import streamlit as st
import calendar
from datetime import datetime


# Funktion zur Anzeige des Kalenders für den ausgewählten Monat
def display_calendar(year, month, tasks, show_week=False, week_number=None):
    cal = calendar.Calendar().monthdayscalendar(year, month)
    if show_week:
        days = cal[week_number - 1] if week_number <= len(cal) else []
        st.title(f"Kalenderwoche {week_number}")
    else:
        st.title(f"Kalender für {calendar.month_name[month]} {year}")

    table = "<table style='width:100%; border-collapse: collapse;'>"

    # Tabellenkopf mit den Wochentagen
    table += "<tr>"
    for day in ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]:
        table += f"<th style='border: 1px solid black; padding: 8px; text-align: center;'>{day}</th>"
    table += "</tr>"

    # Darstellung des Kalenders
    for week in cal if not show_week else [days]:
        for day in week:
            if show_week and day == 0:
                table += "<tr><td colspan='7' style='border: 1px solid black; padding: 8px; text-align: center;'>---</td></tr>"
            elif day != 0:
                tasks_for_day = tasks.get((year, month, day), [])
                task_info = "<br>".join([f"{task['time']} - {task['end_time']}: {task['description']}" for task in tasks_for_day])
                table += f"<td style='border: 1px solid black; padding: 8px; text-align: left; vertical-align: top; height: 100px;'>"
                table += f"<span style='text-decoration: none; color: black;'>{day}</span>"
                table += f"<div style='display: none; position: absolute; background-color: white; border: 1px solid black; padding: 8px;'>{task_info}</div>"
                table += "</td>"
            else:
                table += "<td style='border: 1px solid black; padding: 8px;'></td>"
        table += "</tr>"

    table += "</table>"
    st.write(table, unsafe_allow_html=True)

# Funktion zur Anzeige der Aufgabenübersicht und zum Löschen von Aufgaben
def display_task_overview():
    st.title("Aufgabenübersicht")

    tasks = st.session_state.get('tasks', {})
    tasks_to_delete = []

    for date, day_tasks in tasks.items():
        st.subheader(f"Aufgaben für {date[0]}-{date[1]}-{date[2]}")
        for idx, task in enumerate(day_tasks):
            st.write(f"{idx + 1}. {task['time']} - {task['end_time']}: {task['description']}")
            if st.checkbox(f"Löschen {date[0]}-{date[1]}-{date[2]}"):
                tasks_to_delete.append((date, idx))

    if tasks_to_delete:
        for date, idx in tasks_to_delete:
            del tasks[date][idx]
            st.success(f"Aufgabe gelöscht: {date[0]}-{date[1]}-{date[2]}, Index: {idx}")
        st.session_state.tasks = tasks

# Funktion zur Anzeige des Taskmanagers
def display_task_manager():
    st.title("Taskmanager")
    task_date = st.date_input("Datum auswählen", key="task_date")
    task_time = st.time_input("Startzeit eingeben", key="task_time")
    task_end_date = st.date_input("Enddatum auswählen", key="task_end_date")
    task_end_time = st.time_input("Endzeit eingeben", key="task_end_time")
    task_description = st.text_input("Aufgabenbeschreibung eingeben", key="task_description")

    if st.button("Aufgabe hinzufügen"):
        start_date_time = datetime.combine(task_date, task_time)
        end_date_time = datetime.combine(task_end_date, task_end_time)
        duration = end_date_time - start_date_time

        task_info = {
            'time': str(task_time),
            'end_time': str(task_end_time),
            'duration': str(duration),
            'description': task_description
        }
        tasks = st.session_state.get('tasks', {})
        date_key = (task_date.year, task_date.month, task_date.day)
        if date_key in tasks:
            tasks[date_key].append(task_info)
        else:
            tasks[date_key] = [task_info]
        st.session_state.tasks = tasks
        st.success(f"Aufgabe für {task_date} von {task_time} bis {task_end_time} hinzugefügt!")

        st.experimental_rerun()


# Navigation zwischen den Seiten
def main():
    st.sidebar.title("Navigation")
    app_mode = st.sidebar.selectbox(
        "Wähle eine Seite",
        ["Kalender anzeigen", "Taskmanager", "Aufgabenübersicht"]
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
        show_week = st.checkbox("Nur eine Woche anzeigen")
        if show_week:
            week_number = st.slider("Kalenderwoche auswählen", 1, 6, 1)
            st.button("Woche anzeigen")
        else:
            week_number = None
        display_calendar(year, month_index, tasks, show_week, week_number)
    elif app_mode == "Taskmanager":
        display_task_manager()

        # Display für die Taskübersicht unterhalb des Taskmanagers
        display_task_overview()

    elif app_mode == "Aufgabenübersicht":
        display_task_overview()

if __name__ == "__main__":
    main()
