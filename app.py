import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import math
#fuer API
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
    st.write(f"{semester_description}")
else:
    st.error("Failed to fetch current semester information.")

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


def initialize_session_state():
    # Initialize session state variables if not already present
    if 'tasks' not in st.session_state:
        st.session_state.tasks = load_tasks_from_csv()  # Load tasks from CSV if they exist, else initialize as empty dictionary




       
def get_datetime_on_date(date, time):
    # Kombiniere das Datum mit der Uhrzeit, um ein kombiniertes datetime-Objekt zu erhalten
    combined_datetime = datetime.combine(date, time)
    return combined_datetime



# Function to save tasks to a CSV file
def save_tasks_to_csv(tasks):
    # Use .get('completed', False) to safely access the 'completed' status with a default of False
    df = pd.DataFrame([(key[0], key[1], key[2], task['time'],task['name'],task['description'], task['ects'], task['percentage'], task['due_date'], task.get('completed', False))
                       for key, tasks_list in tasks.items() for task in tasks_list],
                      columns=['Year', 'Month', 'Day', 'Time', 'Name' ,'Description', 'ECTS', 'Percentage', 'Due Date', 'Completed'])
    df.to_csv('tasks2.csv', index=False)





# Function to load tasks from a CSV file
def load_tasks_from_csv():
    try:
        df = pd.read_csv('tasks2.csv')
        tasks = {}
        for _, row in df.iterrows():
            date_key = (int(row['Year']), int(row['Month']), int(row['Day']))
            task_info = {
                'time': row['Time'],
                'name':row['Name'],
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
        new_ects = st.number_input("ECTS Points", value=selected_task_details['ects'], min_value=0)
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
        
        
        
        
            
def display_task_overview():
    initialize_session_state()  # Initialize session state

    st.title("To Do List")
    tasks = st.session_state.tasks

    for day, day_tasks in tasks.items():
        st.subheader(f"Tasks for {day}")
        for task in day_tasks:
            task_name = task['name']
            task_key = f"complete_{task_name}_{day}"

            if task.get('completed', False):
                # Completed tasks in green
                st.markdown(f"<span style='color: green;'>{task_name} - Completed on: {task['due_date']}</span>", unsafe_allow_html=True)
            else:
                overdue = datetime.strptime(task['due_date'], '%Y-%m-%d') < datetime.now()
                color = "red" if overdue else "black"
                st.markdown(f"<span style='color: {color};'>{task_name} - Due: {task['due_date']}{' (Overdue)' if overdue else ''}</span>", unsafe_allow_html=True)
                if st.button(f"Mark as Completed", key=task_key):
                    mark_as_completed(task_name, task['due_date'])  # Pass task_name and due_date for marking completion


                    



    # Function to handle marking tasks as completed
    def mark_as_completed(task_name, due_date):
        for day, day_tasks in st.session_state.tasks.items():
            for task in day_tasks:
                if task['name'] == task_name and task['due_date'] == due_date:
                    task['completed'] = True
                    save_tasks_to_csv(st.session_state.tasks)  # Save the updated tasks
                    break






    # Display tasks with color coding
    for day, day_tasks in st.session_state.tasks.items():
        st.subheader(f"Tasks for {day}")
        for task in day_tasks:
            due_date = datetime.strptime(task['due_date'], '%Y-%m-%d')
            overdue = due_date < datetime.now()
            if task.get('completed', False):
                # Completed tasks in green
                st.markdown(f"<span style='color: green;'>{task['description']} - Completed on: {task['due_date']}</span>", unsafe_allow_html=True)
            else:
                # Pending tasks in default color or red if overdue
                color = "red" if overdue else "black"
                st.markdown(f"<span style='color: {color};'>{task['description']} - Due: {task['due_date']}{' (Overdue)' if overdue else ''}</span>", unsafe_allow_html=True)
                if st.button(f"Mark as Completed", key=f"complete_{task['description']}_{day}"):
                    mark_as_completed(task['description'], day)




def display_weekly_calendar():
    st.title("Weekly Calendar")
    tasks = load_tasks_from_csv()  # Ensure this function returns a dictionary of tasks

    today = datetime.today()
    start_of_week = today - timedelta(days=today.weekday())
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    cols = st.columns(7)
    for i, day in enumerate(days):
        with cols[i]:
            st.subheader(day)
            day_date = start_of_week + timedelta(days=i)
            st.write(day_date.strftime('%b %d'))

            day_tasks = tasks.get((day_date.year, day_date.month, day_date.day), [])
            if day_tasks:
                 for task in day_tasks:
                    due_date = datetime.strptime(task['due_date'], '%Y-%m-%d')
                    overdue = due_date < today
                    completed = task.get('completed', False)  # Access the completed status
                    
                    # Apply color styling based on the task status
                    if completed:
                        st.markdown(f"<span style='color: green;'>{task['description']}</span>", unsafe_allow_html=True)
                    elif overdue:
                        st.markdown(f"<span style='color: red;'>{task['description']}</span>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<span style='color: orange;'>{task['description']}</span>", unsafe_allow_html=True)
            else:
                st.write("No tasks")
# Anpassung der main-Funktion, um die neue Funktion aufzurufen

# Function to fetch current semester information




def main():
    st.sidebar.title("Navigation")
    app_mode = st.sidebar.selectbox("Choose a Page", ["Create Tasks", "To Do List", "Edit Tasks", "Weekly Calendar"])

    if app_mode == "Create Tasks":
        display_task_manager()
    elif app_mode == "To Do List":
        display_task_overview()
    elif app_mode == "Edit Tasks":
        edit_tasks()
    elif app_mode == "Weekly Calendar":
        display_weekly_calendar()

if __name__ == "__main__":
    main()

