#!pip install streamlit
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import math

st.set_page_config(
    initial_sidebar_state="auto",
    layout="wide",
    page_icon"📅"
    page_title="HSG Task Manager"
    )

# Function to display the calendar for the selected month
def display_weekly_calendar(year, month, week, tasks):
    # Commented out for the To Do List version
    pass

# Function to display the task overview and delete tasks
def display_task_overview():
    # Set the title for the section in the Streamlit app
    st.title("To Do List")

    # Retrieve the tasks from the CSV file
    tasks = load_tasks_from_csv()

    # Sort tasks based on grade relevance (descending order)
    sorted_tasks = sorted((task for day_tasks in tasks.values() for task in day_tasks), key=lambda x: x['ects'] * (x['percentage'] / 100), reverse=True)

    # Display sorted tasks
    for idx, task in enumerate(sorted_tasks):
        st.write(f"{idx + 1}. Description: {task['description']}, ECTS: {task['ects']}, Percentage: {task['percentage']}%, Grade Relevance: {task['ects'] * (task['percentage'] / 100)}, Due Date: {task['due_date']}")

# Function to display the task manager (now renamed to Create Tasks)
def display_task_manager():
    st.title("Create Tasks")  # Renamed from "Task Manager"
    # Set default allocated time to 1 hour
    task_allocated_time = st.time_input("Enter Allocated Time", value=datetime.strptime("01:00", "%H:%M").time(), key="task_allocated_time")
    task_due_date = st.date_input("Select Due Date", key="task_due_date")  # Renamed from "task_end_date"
    task_description = st.text_input("Enter Task Description", key="task_description")

    # New input fields for ECTS and Percentage
    task_ects = st.number_input("Enter ECTS Points", min_value=0, key="task_ects")
    task_percentage = st.number_input("Enter Percentage of Grade", min_value=0, max_value=100, key="task_percentage")

    if st.button("Add Task"):
        tasks = load_tasks_from_csv()
        start_date_time = compute_start_time(tasks, task_due_date)

        end_date_time = start_date_time + timedelta(hours=task_allocated_time.hour, minutes=task_allocated_time.minute)
        duration = end_date_time - start_date_time

        task_info = {
            'time': start_date_time.strftime("%H:%M"),
            'end_time': end_date_time.strftime("%H:%M"),
            'duration': str(duration),
            'description': task_description,
            'ects': task_ects,
            'percentage': task_percentage,
            'due_date': task_due_date  # Use 'due_date' instead of 'end_time' for the due date
        }

        date_key = (start_date_time.year, start_date_time.month, start_date_time.day)
        if date_key in tasks:
            tasks[date_key].append(task_info)
        else:
            tasks[date_key] = [task_info]

        # Save tasks to the CSV file
        save_tasks_to_csv(tasks)

        st.success(f"Task added from {start_date_time} to {end_date_time}!")

        st.experimental_rerun()

# Function to compute the start time for the task
def compute_start_time(tasks, due_date):
    # Filter out tasks with empty time values
    tasks_with_time = [task for day_tasks in tasks.values() for task in day_tasks if pd.notna(task.get('end_time'))]

    # Convert float values to string
    for task in tasks_with_time:
        if isinstance(task['end_time'], float) and not math.isnan(task['end_time']):
            task['end_time'] = str(int(task['end_time']))

    # Sort tasks by end time in ascending order
    sorted_tasks = sorted(tasks_with_time, key=lambda x: datetime.strptime(x['end_time'], "%H:%M"))

    current_time = datetime.now()
    start_time = current_time

    for task in sorted_tasks:
        task_end_time = datetime.strptime(task['end_time'], "%H:%M")
        task_due_date = datetime(due_date.year, due_date.month, due_date.day, task_end_time.hour, task_end_time.minute)
        if task_due_date > current_time and task_due_date.date() <= due_date:
            start_time = task_due_date
            break

    return start_time

# Function to save tasks to a CSV file
def save_tasks_to_csv(tasks):
    # Convert tasks to a dataframe
    df = pd.DataFrame([(key[0], key[1], key[2], task['time'], task['end_time'], task['duration'], task['description'], task['ects'], task['percentage'], task['due_date'])
                       for key, tasks_list in tasks.items() for task in tasks_list],
                      columns=['Year', 'Month', 'Day', 'Time', 'End Time', 'Duration', 'Description', 'ECTS', 'Percentage', 'Due Date'])

    # Save the dataframe to a CSV file
    df.to_csv('tasks.csv', index=False)

# Function to load tasks from a CSV file
def load_tasks_from_csv():
    try:
        # Load the CSV file into a dataframe
        df = pd.read_csv('tasks.csv')

        # Convert the dataframe to the tasks dictionary
        tasks = {}
        for _, row in df.iterrows():
            date_key = (int(row.get('Year', 0)), int(row.get('Month', 0)), int(row.get('Day', 0)))
            task_info = {
                'time': row.get('Time', ''),
                'end_time': row.get('End Time', ''),
                'duration': row.get('Duration', ''),
                'description': row.get('Description', ''),
                'ects': row.get('ECTS', 0),
                'percentage': row.get('Percentage', 0),
                'due_date': row.get('Due Date', '')
            }
            if date_key in tasks:
                tasks[date_key].append(task_info)
            else:
                tasks[date_key] = [task_info]

        return tasks

    except FileNotFoundError:
        # If the file doesn't exist, return an empty dictionary
        return {}

# Navigation between pages
def main():
    st.sidebar.title("Navigation")
    app_mode = st.sidebar.selectbox(
        "Choose a Page",
        ["Create Tasks", "To Do List"]  # Renamed from "Task Manager"
    )

    # Commented out for the To Do List version
    # if app_mode == "Show Calendar":
    #     year = st.number_input("Enter Year", min_value=1900, max_value
    if app_mode == "Create Tasks":
        display_task_manager()
    elif app_mode == "To Do List":
        display_task_overview()

if __name__ == "__main__":
    main()


"""

#just some basic things to import that would be useful for our program:
import streamlit as st
import calendar
from datetime import datetime


# Funktion zur Anzeige des Kalenders für den ausgewählten Monat
def display_weekly_calendar(year, month, week,tasks):
    cal = calendar.monthcalendar(year, month)
    month_name = calendar.month_name[month]

    st.title(f"Wochenansicht für {week}. Woche in {month_name} {year}")

    # Tabelle für den Kalender
    table = "<table style='width:100%; border-collapse: collapse;'>"

    # Tabellenkopf mit den Wochentagen
    table += "<tr>"
    for day in ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]:
        table += f"<th style='border: 1px white; padding: 8px; text-align: center;'>{day}</th>"
    table += "</tr>"

    # Darstellung der ausgewählten Woche
    selected_week = cal[week - 1]
    table += "<tr>"
    for day in selected_week:
        if day != 0:
            tasks_for_day = tasks.get((year, month, day), [])
            task_info = "<br>".join([f"{task['time']}, {task['duration']}" for task in tasks_for_day])
            table += f"<td style='border: 1px solid black; padding: 8px; text-align: left; vertical-align: top;'>{day}<br>{task_info}</td>"
        else:
            table += "<td style='border: 1px white; padding: 8px;'></td>"
    table += "</tr>"

    table += "</table>"
    st.markdown(table, unsafe_allow_html=True)

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
        week = st.slider("Woche auswählen", 1, 5, 1)
        tasks = st.session_state.get('tasks', {})
        display_weekly_calendar(year, month_index,week, tasks)
    elif app_mode == "Taskmanager":
        display_task_manager()

        # Display für die Taskübersicht unterhalb des Taskmanagers
        display_task_overview()

    elif app_mode == "Aufgabenübersicht":
        display_task_overview()

if __name__ == "__main__":
    main()

"""
