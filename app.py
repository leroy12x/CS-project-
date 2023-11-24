import streamlit as st
import calendar
from datetime import datetime

# Funktion zur Anzeige des Kalenders für den ausgewählten Monat
def display_calendar(year, month, tasks, show_week=False, week_number=None):
    if show_week:
        cal = calendar.Calendar().monthdayscalendar(year, month)
        days = cal[week_number - 1] if week_number <= len(cal) else []
        st.title(f"Kalenderwoche {week_number}")
    else:
        cal = calendar.monthcalendar(year, month)
        st.title(f"Kalender für {calendar.month_name[month]} {year}")

    for week in cal:
        for day in week:
            if show_week and day == 0:
                st.write("---")
            elif day != 0:
                tasks_for_day = tasks.get((year, month, day), [])
                task_info = "\n".join([f"{task['time']} - {task['end_time']}: {task['description']}" for task in tasks_for_day])

                col1, col2 = st.beta_columns(2)
                col1.subheader(f"{day}.{month}.{year}")
                with col2:
                    st.write(task_info)
                    st.write("---")
# Funktion zur Anzeige der Aufgabenübersicht und zum Löschen von Aufgaben
def display_task_overview():
    st.title("Aufgabenübersicht")

    tasks = st.session_state.get('tasks', {})
    tasks_to_delete = []

    for date, day_tasks in tasks.items():
        st.subheader(f"Aufgaben für {date[0]}-{date[1]}-{date[2]}")
        for idx, task in enumerate(day_tasks):
            st.write(f"{idx + 1}. {task['time']} - {task['end_time']}: {task['description']}")
            if st.checkbox(f"Löschen##{date[0]}-{date[1]}-{date[2]}##{idx}"):
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
    year = st.number_input("Jahr eingeben", min_value=1900, max_value=2100, value=2023)
    month_index = st.slider("Monat auswählen", 1, 12, 1)
    show_week = st.checkbox("Nur eine Woche anzeigen")

    if show_week:
        week_number = st.slider("Kalenderwoche auswählen", 1, 6, 1)
    else:
        week_number = None

    tasks = {}  # Deine Aufgaben hier

    display_calendar(year, month_index, tasks, show_week, week_number)

if __name__ == "__main__":
    main()
