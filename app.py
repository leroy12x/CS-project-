import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import math
#API
import requests



def get_current_semester():
    url = "https://integration.preprod.unisg.ch/eventapi/timeLines/currentTerm"
    headers = {
        "X-ApplicationId": "587acf1c-24d0-4801-afda-c98f081c4678",
        "API-Version": "1",
        "X-RequestedLanguage": "de"}

    response = requests.get(url, headers=headers)
    if response.ok:
        return response.json()
    else:
        print("Error calling API: ", response.status_code)
        return None




# Fetch and display the current semester
semester_info = get_current_semester()
if semester_info:
    # Extract and display the description from the semester information
    semester_description = semester_info.get('description', 'No description available')
else:
    st.error("Failed to fetch current semester information.")
    st.write("semester_description")
semester_ids = get_current_semester()
if semester_ids:
    # Extract and display the description from the semester information
    semester_id = semester_info.get('id')
else:
    st.error("Failed to fetch current semester id.")






def get_events_by_term(term_id):
    url2 = f"https://integration.preprod.unisg.ch/eventapi/Events/byTerm/{term_id}"
    headers = {
        "X-ApplicationId": "587acf1c-24d0-4801-afda-c98f081c4678",
        "API-Version": "1",
        "X-RequestedLanguage": "en"
    }
    response = requests.get(url2, headers=headers)
    if response.ok:
        return pd.DataFrame(response.json())
    else:
        st.error(f"Error calling API: {response.status_code}")
        return pd.DataFrame()


  # Load tasks from CSV if they exist, else initialize as empty dictionary

def display_to_do():
    tasks = load_tasks_from_csv()
    st.session_state.tasks = tasks   # Initialize session state

    st.markdown("<h2>Tasks with ECTS and Time Estimates</h2>", unsafe_allow_html=True)
    tasks = load_tasks_from_csv()
    calculate_ects_percentage(tasks)

    for day, day_tasks in tasks.items():
        st.subheader(f"Tasks for {day}")

        for task in day_tasks:
            task_name = task['name']
            task_time = task['time']
            due_date_str = task['due_date']
            task_key = f"{task_name}_{due_date_str}"

            # Handle cases where remaining_hours might be None
            remaining_hours = task.get('remaining_hours')
            if remaining_hours is None:
                task_ects = float(task['ects'])
                task_percentage = float(task['percentage'])
                total_ects = round(task_ects * (task_percentage / 100), 2)
                remaining_hours = total_ects * 30  # Multiply ECTS by 30 to estimate work hours

            # Check if task is completed
            if task.get('completed', False):
                st.markdown(f"<span style='color: green;'>{task_name} - Completed on: {task_time}</span>", unsafe_allow_html=True)
            else:
                overdue = datetime.strptime(due_date_str, '%Y-%m-%d') < datetime.now()
                color = "red" if overdue else "orange"
                st.markdown(f"<span style='color: {color};'>{task_name} ({task['total_ects']} ECTS) - Due: {task_time}{' (Overdue)' if overdue else ''}</span>", unsafe_allow_html=True)
                st.write(f"Estimated Remaining Work Hours: {remaining_hours} hours")
            if not task.get('completed', False):
                if st.button(f"Mark as Completed", key=task_key):
                    mark_as_completed(task_name, due_date_str)
                    task['completed'] = True  # Setze den Status der Aufgabe auf abgeschlossen
                    save_tasks_to_csv(tasks)  # Speichere die aktualisierten Aufgaben
                    st.experimental_rerun()  # Seite neu laden, um Änderungen anzuzeigen

                







def display_task_manager():
    st.markdown("<h2>Create Tasks</h2>", unsafe_allow_html=True)
    # Input field for course ID
    # Set default allocated time to 1 hour
    placeholder_text_time = "Enter the Time in the format 12:00"
    task_allocated_time = st.text_input("Deadline", placeholder=placeholder_text_time,key="task_allocated_time")
    task_due_date = st.date_input("Select Due Date", key="task_due_date")
    placeholder_text_name = "Copy your COURSE NAME"
    task_name = st.text_input("Enter Task Name",placeholder=placeholder_text_name, key="task_name")
    task_description = st.text_input("Enter Task Description", key="task_description")
    placeholder_text_ects = "Leave blank when you have a COURSE NAME"
    task_ects = st.text_input("Enter ECTS Points",placeholder=placeholder_text_ects, key="task_ects")
    task_percentage = st.text_input("Enter Percentage of Grade", key="task_percentage")

    if st.button("Add Task"):


        tasks = load_tasks_from_csv()
        start_time = datetime.strptime(task_allocated_time, "%H:%M").time()  # Just time component
        start_date_time = get_datetime_on_date(task_due_date, start_time)
        task_percentage = int(task_percentage)
        if task_ects and task_ects.strip():
            task_ects = float(task_ects)
        if task_name is not None:
            events_df = get_events_by_term(semester_id)
            # Filter events by the provided course ID
            if not events_df.empty:
                # Ensure the course_id is a string and remove any leading/trailing whitespace
                course_name = str(task_name).strip()

                # Attempt to match the course ID as an integer if it is numeric
                if course_name:
                    course_events = events_df[events_df['title'] == course_name]
                     # Set the title as task name
                    max_credits_list = course_events['maxCredits'].tolist()
                    if max_credits_list: #and isinstance(max_credits_list[0], list) and len(max_credits_list[0]) > 0:
                        task_ects = (int(max_credits_list[0][0])/100) # Set maxCredits as ECTS
                    else:
                        st.error(f"No maxCredits found for Course name: {course_name}")
                else:
                    st.error(f"No events found for Course name: {course_name}")
            else:
                st.error("No events data available.")
        else:
            st.warning('Please enter a Course ID.')

        task_info = {
            'time': start_date_time.strftime("%H:%M"),
            'description': task_description,
            'name': task_name,
            'ects': task_ects,
            'percentage': task_percentage,
            'due_date': task_due_date.strftime('%Y-%m-%d'),
            'remaining_hours':(task_ects*(task_percentage/100))*30, # Format the date
            'completed': False  # Correctly placed inside task_info
        }

        date_key = (start_date_time.year, start_date_time.month, start_date_time.day)
        if date_key in tasks:
            tasks[date_key].append(task_info)
        else:
            tasks[date_key] = [task_info]

        # Save tasks to the CSV file
        save_tasks_to_csv(tasks)

        st.success(f"Task added at {start_date_time} !")

        st.experimental_rerun()


def get_datetime_on_date(date, time):
    # Combine the date with the time to obtain a combined datetime object
    combined_datetime = datetime.combine(date, time)
    return combined_datetime



# Function to save tasks to a CSV file
def save_tasks_to_csv(tasks):
    df = pd.DataFrame([
        (
            key[0], key[1], key[2],
            task['time'], task['name'], task['description'],
            task['ects'], task['percentage'], task['due_date'],
            task.get('completed', False), task.get('remaining_hours', None)  # Added remaining_hours
        )
        for key, tasks_list in tasks.items() for task in tasks_list
    ], columns=['Year', 'Month', 'Day', 'Time', 'Name', 'Description', 'ECTS', 'Percentage', 'Due Date', 'Completed', 'Remaining Hours'])  # Added 'Remaining Hours' column

    df.to_csv('tasks3.csv', index=False)
    return tasks





# Function to load tasks from a CSV file
def load_tasks_from_csv():
    try:
        df = pd.read_csv('tasks3.csv')
        tasks = {}
        for _, row in df.iterrows():
            date_key = (int(row['Year']), int(row['Month']), int(row['Day']))
            task_info = {
                'time': row['Time'],
                'name': row['Name'],
                'description': row['Description'],
                'ects': row['ECTS'],
                'percentage': row['Percentage'],
                'due_date': row['Due Date'],
                'completed': row.get('Completed', False),
                'remaining_hours': row.get('Remaining Hours')  # Load remaining_hours
            }
            if date_key in tasks:
                tasks[date_key].append(task_info)
            else:
                tasks[date_key] = [task_info]
        return tasks
    except FileNotFoundError:
        return {}





def calculate_ects_percentage(tasks):
    for day_tasks in tasks.values():
        for task in day_tasks:
            task['total_ects'] = round(task['ects'] * (task['percentage'] / 100), 2)




# Function to edit or delete tasks
def edit_tasks():
    st.markdown("<h2>Edit Tasks</h2>", unsafe_allow_html=True)

    tasks = load_tasks_from_csv()
    task_list = [f"{task['name']} (Due: {task['due_date']})" for day_tasks in tasks.values() for task in day_tasks]

    selected_task_description = st.selectbox("Select a Task to Edit", task_list)
    selected_task_details = None

    # Find the task in the tasks dictionary
    for date_key, day_tasks in tasks.items():
        for task in day_tasks:
            if selected_task_description == f"{task['name']} (Due: {task['due_date']})":
                selected_task_details = task
                selected_date_key = date_key  # Keep track of the date key where the task is found
                break

    if selected_task_details:
        new_description = st.text_input("Task Name", value=selected_task_details['name'])
        new_due_date = st.date_input("Due Date", value=datetime.strptime(selected_task_details['due_date'], '%Y-%m-%d'))
        new_ects = st.text_input("ECTS Points", value=selected_task_details['ects'])
        new_percentage = st.number_input("Percentage of Grade", value=selected_task_details['percentage'], min_value=0, max_value=100)

        if st.button("Update Task"):
            selected_task_details['name'] = new_description
            selected_task_details['due_date'] = new_due_date.strftime('%Y-%m-%d')
            selected_task_details['ects'] = new_ects
            selected_task_details['percentage'] = new_percentage
            save_tasks_to_csv(tasks)
            st.success("Task updated successfully!")


        if st.button("Delete Task"):
            # Remove the selected task from the list of tasks for that day
            tasks[selected_date_key].remove(selected_task_details)
            # If the day has no more tasks, remove the day from the tasks dictionary
            if not tasks[selected_date_key]:
                del tasks[selected_date_key]
            save_tasks_to_csv(tasks)
            st.success("Task deleted successfully!")











    # Function to handle marking tasks as completed
def mark_as_completed(task_name, due_date_str):
    # Convert the date into a datetime object
    due_date = datetime.strptime(due_date_str, '%Y-%m-%d')
    date_key = (due_date.year, due_date.month, due_date.day)

    # Check whether the date exists as a key
    if date_key in st.session_state.tasks:
        for task in st.session_state.tasks[date_key]:
            if task['name'] == task_name and task['due_date'] == due_date_str:
                task['completed'] = True
                save_tasks_to_csv(st.session_state.tasks)
                break



def display_weekly_calendar():
    st.markdown("<h2>Weekly Calendar</h2>", unsafe_allow_html=True)
    tasks = load_tasks_from_csv()  # Ensure this function returns a dictionary of tasks

    today = datetime.today()

    # Display last week, current week, and next week
    for week in range(-1, 2):
        week_start = today - timedelta(days=today.weekday()) + timedelta(weeks=week)
        week_label = "Last Week" if week == -1 else "Next Week" if week == 1 else "Current Week"
        st.subheader(week_label)

        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

        for i, day in enumerate(days):
            day_date = week_start + timedelta(days=i)
            # Create a row for each day
            day_col, task_col = st.columns([1, 5])  # Adjust the ratio as needed

            with day_col:
                st.markdown(f"**{day} - {day_date.strftime('%b %d')}**", unsafe_allow_html=True)

            with task_col:
                day_tasks = tasks.get((day_date.year, day_date.month, day_date.day), [])
                if day_tasks:
                    for task in day_tasks:
                        due_date = datetime.strptime(task['due_date'], '%Y-%m-%d')
                        overdue = due_date < today
                        completed = task.get('completed', False)  # Access the completed status
                        task_ects = float(task['ects'])
                        task_percentage = float(task['percentage'])
                        task['total_ects'] = round(task_ects * (task_percentage / 100), 2)
                        # Task description with time, name, and other details
                        task_display = f"{task['time']} - {task['name']}: {task['description']} (ECTS: {task['ects']}, Percentage: {task['percentage']})"

                        # Apply color styling based on the task status
                        if completed:
                            st.markdown(f"<span style='color: green;'>{task_display}</span>", unsafe_allow_html=True)
                        elif overdue:
                            st.markdown(f"<span style='color: red;'>{task_display}</span>", unsafe_allow_html=True)
                        else:
                            st.markdown(f"<span style='color: orange;'>{task_display}</span>", unsafe_allow_html=True)
                else:
                    st.write("No tasks")



# Function to record hours worked and subtract them from the Estimated Remaining Work Hours
def display_work_done():
    st.markdown("<h2>Record Work</h2>", unsafe_allow_html=True)

    tasks = load_tasks_from_csv()  # Load existing tasks

    # Create a list for task selection
    task_list = [f"{task['name']} (Due: {task['due_date']})" for day_tasks in tasks.values() for task in day_tasks]

    selected_task_description = st.selectbox("Select a Task", task_list)
    selected_task_details = None

    # Find the selected task in the tasks dictionary
    for date_key, day_tasks in tasks.items():
        for task in day_tasks:
            if selected_task_description == f"{task['name']} (Due: {task['due_date']})":
                selected_task_details = task
                break

    if selected_task_details:
        hours_worked = st.number_input("Enter hours worked", min_value=0.0, step=0.5)

        if st.button("Record Hours"):
            # Calculate and update the remaining hours
            task_ects = float(selected_task_details['ects'])
            task_percentage = float(selected_task_details['percentage'])
            total_ects = round(task_ects * (task_percentage / 100), 2)
            estimated_hours = total_ects * 30  # ECTS to hours
            remaining_hours = max(0, estimated_hours - hours_worked)  # Ensure it doesn't go below zero

            # Update task info
            selected_task_details['remaining_hours'] = remaining_hours

            # Save the updated tasks
            save_tasks_to_csv(tasks)
            st.success(f"Updated remaining work hours for '{selected_task_details['name']}' to {remaining_hours} hours.")



def initialize_session_state():
    if 'tasks' not in st.session_state:
        st.session_state.tasks = load_tasks_from_csv()

def display_front_page():
    st.markdown("<h1 style='text-align: center; color: green;'>Welcome to StudySprint</h1>", unsafe_allow_html=True)
    st.write("<h4 style='text-align: center;'>Never forget your tasks again!</h4>", unsafe_allow_html=True)

    st.markdown("---")  # Divider

    st.markdown("<h3 style='text-align: center;'>Features:</h3>", unsafe_allow_html=True)
    st.markdown(
        "<div style='text-align: center;'>"
        "<ul style='list-style-position: inside; padding-left: 0; display: inline-block; text-align: left;'>"
        "<li>Task Management</li>"
        "<li>To Do List</li>"
        "<li>Weekly Calendar</li>"
        "</ul>"
        "</div>", unsafe_allow_html=True)

    st.markdown("---")  # Divider

    st.markdown("<p style='text-align: center;'>Start your journey with StudySprint by selecting an option from the sidebar.</p>", unsafe_allow_html=True)

def display_navigation():
    st.sidebar.markdown("<h2 style='color: green;'>Navigation</h2>", unsafe_allow_html=True)
    selected_option = st.sidebar.radio("", ["Front Page", "Create Tasks", "Edit Tasks", "Record Work", "To Do List", "Weekly Calendar"])

    if selected_option == "Front Page":
        display_front_page()
    elif selected_option == "Create Tasks":
        display_task_manager()
    elif selected_option == "Edit Tasks":
        edit_tasks()
    elif selected_option == "Record Work":
        display_work_done()
    elif selected_option == "To Do List":
        display_to_do()
    elif selected_option == "Weekly Calendar":
        display_weekly_calendar()

def main():
    display_navigation()

if __name__ == "__main__":
    main()