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


  # Load tasks from CSV if they exist, else initialize as empty dictionary


def display_task_ects_estimate():
    load_tasks_from_csv()  # Initialize session state

    st.title("Tasks with ECTS and Time Estimates")
    tasks = load_tasks_from_csv() 
    calculate_ects_percentage(tasks)

    for day, day_tasks in tasks.items():
        st.subheader(f"Tasks for {day}")

        for task in day_tasks:
            task_name = task['name']
            
            # Ensure 'ects' and 'percentage' are converted to numbers
            task_ects = float(task['ects'])
            task_percentage = float(task['percentage'])
            task['total_ects'] = round(task_ects * (task_percentage / 100), 2)

            ects_task = task['total_ects'] * 30  # Multiply ECTS by 20 to estimate work hours

            # Check if task is completed
            if task.get('completed', False):
                st.markdown(f"<span style='color: green;'>{task_name} - Completed on: {task['due_date']}</span>", unsafe_allow_html=True)
            else:
                overdue = datetime.strptime(task['due_date'], '%Y-%m-%d') < datetime.now()
                color = "red" if overdue else "black"
                st.markdown(f"<span style='color: {color};'>{task_name} ({task_ects} ECTS) - Due: {task['due_date']}{' (Overdue)' if overdue else ''}</span>", unsafe_allow_html=True)
                
                # Display ECTS and estimated remaining work hours
                st.write(f"{task['name']}({task['description']})")
                st.write(f"ECTS: {task['total_ects']}")
                st.write(f"Estimated Remaining Work Hours: {ects_task} hours")
                    
                    
        
        
                
def display_task_manager():
    st.title("Create Tasks")  # Renamed from "Task Manager"
    # Input field for course ID
    # Set default allocated time to 1 hour
    placeholder_text_time = "Enter the Time in the format 12:00"
    task_allocated_time = st.text_input("Deadline", placeholder=placeholder_text_time,key="task_allocated_time")
    task_due_date = st.date_input("Select Due Date", key="task_due_date") 
    placeholder_text_name = "Leave blank when you have a COURSE ID"
    task_name = st.text_input("Enter Task Name",placeholder=placeholder_text_name, key="task_name")
    task_description = st.text_input("Enter Task Description", key="task_description")
    placeholder_text_ects = "Leave blank when you have a COURSE ID"
    task_ects = st.text_input("Enter ECTS Points",placeholder=placeholder_text_ects, key="task_ects")
    task_id = st.text_input("Enter COURSE ID ", key="task_id")         
    task_percentage = st.text_input("Enter Percentage of Grade", key="task_percentage")
            
    if st.button("Add Task"):
        
           
        tasks = load_tasks_from_csv()
        start_time = datetime.strptime(task_allocated_time, "%H:%M").time()  # Just time component
        start_date_time = get_datetime_on_date(task_due_date, start_time)
        task_percentage = int(task_percentage)
        if task_ects and task_ects.strip():
            task_ects = int(task_ects)
        if task_id is not None: # das war es glaube ich 
            events_df = get_events_by_term(semester_id)
            st.write(f"{events_df}")
            # Filter events by the provided course ID
            if not events_df.empty:
                # Ensure the course_id is a string and remove any leading/trailing whitespace
                course_id = str(task_id).strip()

                # Attempt to match the course ID as an integer if it is numeric
                if course_id.isdigit():
                    course_id = int(course_id)
                    course_events = events_df[events_df['id'] == course_id]
                    title_list = course_events['title'].tolist()
                    if title_list and isinstance(title_list[0], str):
                        task_name = title_list[0]  # Set the title as task name
                    max_credits_list = course_events['maxCredits'].tolist()
                    if max_credits_list and isinstance(max_credits_list[0], list) and len(max_credits_list[0]) > 0:
                        task_ects = (int(max_credits_list[0][0])/100) # Set maxCredits as ECTS
                    else:
                        st.error(f"No maxCredits found for Course ID: {course_id}")
                else:
                    st.error(f"No events found for Course ID: {course_id}")
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

        st.success(f"Task added at {start_date_time} !")

        st.experimental_rerun()

       
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
    df.to_csv('tasks3.csv', index=False)





# Function to load tasks from a CSV file
def load_tasks_from_csv():
    try:
        df = pd.read_csv('tasks3.csv')
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




def calculate_ects_percentage(tasks):
    for day_tasks in tasks.values():
        for task in day_tasks:
            task['total_ects'] = round(task['ects'] * (task['percentage'] / 100), 2)




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

# Anpassung der main-Funktion, um die neue Funktion aufzurufen

# Function to fetch current semester information




def main():
    st.sidebar.title("Navigation")
    app_mode = st.sidebar.selectbox("Choose a Page", ["Create Tasks", "To Do List", "Edit Tasks", "Weekly Calendar"])

    if app_mode == "Create Tasks":
        display_task_manager()
    elif app_mode == "To Do List":
        display_task_ects_estimate()
    elif app_mode == "Edit Tasks":
        edit_tasks()
    elif app_mode == "Weekly Calendar":
        display_weekly_calendar()

if __name__ == "__main__":
    main()