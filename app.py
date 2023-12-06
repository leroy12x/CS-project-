import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import math

# Function to display the calendar for the selected month
def display_weekly_calendar(year, month, week, tasks):
    # Commented out for the To Do List version
    pass

def display_task_overview():
    st.title("To Do List")
    tasks = load_tasks_from_csv()

    for day, day_tasks in tasks.items():
        st.subheader(f"Tasks for {day}")
        for task in day_tasks:
            if task['completed']:
                st.write(f"Completed: {task['description']}")
            else:
                overdue = datetime.strptime(task['due_date'], '%Y-%m-%d') < datetime.now()
                st.write(f"{task['description']} - Due: {task['due_date']} {'(Overdue)' if overdue else ''}")
                if st.button(f"Mark as Completed", key=f"complete_{task['description']}"):
                    task['completed'] = True
                    save_tasks_to_csv(tasks)
                    st.experimental_rerun()
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
            'due_date': task_due_date.strftime('%Y-%m-%d'),  # Format the date
            'completed': False  # Correctly placed inside task_info
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
    df = pd.DataFrame([(key[0], key[1], key[2], task['time'], task['end_time'], task['duration'], task['description'], task['ects'], task['percentage'], task['due_date'], task['completed'])
                       for key, tasks_list in tasks.items() for task in tasks_list],
                      columns=['Year', 'Month', 'Day', 'Time', 'End Time', 'Duration', 'Description', 'ECTS', 'Percentage', 'Due Date', 'Completed'])
    df.to_csv('tasks.csv', index=False)

# Function to load tasks from a CSV file
def load_tasks_from_csv():
    try:
        df = pd.read_csv('tasks.csv')
        tasks = {}
        for _, row in df.iterrows():
            date_key = (int(row['Year']), int(row['Month']), int(row['Day']))
            task_info = {
                'time': row['Time'],
                'end_time': row['End Time'],
                'duration': row['Duration'],
                'description': row['Description'],
                'ects': row['ECTS'],
                'percentage': row['Percentage'],
                'due_date': row['Due Date'],
                'completed': row.get('Completed', False)  # Use get() method for safe access
            }
            if date_key in tasks:
                tasks[date_key].append(task_info)
            else:
                tasks[date_key] = [task_info]
        return tasks
    except FileNotFoundError:
        return {}



# Function to edit or delete tasks
def edit_tasks():
    st.title("Edit Tasks")

    tasks = load_tasks_from_csv()
    task_list = [f"{task['description']} (Due: {task['due_date']})" for day_tasks in tasks.values() for task in day_tasks]

    selected_task = st.selectbox("Select a Task to Edit", task_list)

    # Find the task in the tasks dictionary
    for day_tasks in tasks.values():
        for task in day_tasks:
            if selected_task.startswith(task['description']):
                selected_task_details = task
                break

    if 'selected_task_details' in locals():
        new_description = st.text_input("Task Description", value=selected_task_details['description'])
        new_due_date = st.date_input("Due Date", value=datetime.strptime(selected_task_details['due_date'], '%Y-%m-%d'))
        new_ects = st.number_input("ECTS Points", value=selected_task_details['ects'], min_value=0)
        new_percentage = st.number_input("Percentage of Grade", value=selected_task_details['percentage'], min_value=0, max_value=100)

        if st.button("Update Task"):
            selected_task_details['description'] = new_description
            selected_task_details['due_date'] = new_due_date.strftime('%Y-%m-%d')
            selected_task_details['ects'] = new_ects
            selected_task_details['percentage'] = new_percentage
            save_tasks_to_csv(tasks)
            st.success("Task updated successfully!")

        if st.button("Delete Task"):
            day_tasks.remove(selected_task_details)
            save_tasks_to_csv(tasks)
            st.success("Task deleted successfully!")

# Function to save tasks to a CSV file
def save_tasks_to_csv(tasks):
    df = pd.DataFrame([(key[0], key[1], key[2], task['time'], task['end_time'], task['duration'], task['description'], task['ects'], task['percentage'], task['due_date'])
                       for key, tasks_list in tasks.items() for task in tasks_list],
                      columns=['Year', 'Month', 'Day', 'Time', 'End Time', 'Duration', 'Description', 'ECTS', 'Percentage', 'Due Date'])
    df.to_csv('tasks.csv', index=False)

# Function to load tasks from a CSV file
def load_tasks_from_csv():
    try:
        df = pd.read_csv('tasks.csv')
        tasks = {}
        for _, row in df.iterrows():
            date_key = (int(row['Year']), int(row['Month']), int(row['Day']))
            task_info = {
                'time': row['Time'],
                'end_time': row['End Time'],
                'duration': row['Duration'],
                'description': row['Description'],
                'ects': row['ECTS'],
                'percentage': row['Percentage'],
                'due_date': row['Due Date']
            }
            if date_key in tasks:
                tasks[date_key].append(task_info)
            else:
                tasks[date_key] = [task_info]
        return tasks
    except FileNotFoundError:
        return {}
def display_task_overview():
    st.title("To Do List")
    tasks = load_tasks_from_csv()

    # Filter tasks into pending and completed
pending_tasks = [task for day_tasks in tasks.values() for task in day_tasks if not task.get('completed', False)]
    completed_tasks = [task for day_tasks in tasks.values() for task in day_tasks if task.get('completed', False)]

    # Display pending tasks
    st.subheader("Pending Tasks")
    for task in pending_tasks:
        due_date = datetime.strptime(task['due_date'], '%Y-%m-%d')
        overdue = due_date < datetime.now()
        task_info = f"{task['description']} - Due: {due_date.strftime('%Y-%m-%d')} {'(Overdue)' if overdue else ''}"
        st.write(task_info)
        if st.button("Mark as Completed", key=f"complete_{task['description']}"):
            task['completed'] = True
            save_tasks_to_csv(tasks)
            # Force a refresh of the task lists
            st.session_state.tasks = load_tasks_from_csv()

    # Display completed tasks
    st.subheader("Completed Tasks")
    for task in completed_tasks:
        due_date = datetime.strptime(task['due_date'], '%Y-%m-%d')
        st.markdown(f"<span style='color: green;'>{task['description']} - Completed on: {due_date.strftime('%Y-%m-%d')}</span>", unsafe_allow_html=True)

    # Update the session state after any changes
    st.session_state.tasks = tasks
# Modify the main function to include the edit tasks option
def main():
    st.sidebar.title("Navigation")
    app_mode = st.sidebar.selectbox("Choose a Page", ["Create Tasks", "To Do List", "Edit Tasks"])

    if app_mode == "Create Tasks":
        display_task_manager()
    elif app_mode == "To Do List":
        display_task_overview()
    elif app_mode == "Edit Tasks":
        edit_tasks()

if __name__ == "__main__":
    main()
