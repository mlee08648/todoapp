import streamlit as st
from datetime import datetime
from todo_logic import connect_db, init_db, add_task, get_tasks, update_task_status, delete_task

conn = connect_db()
init_db(conn)

# App title
st.title("🐻‍❄️ My :primary[To-Do] App") # Color options are: blue, green, orange, red, violet, gray (or grey), rainbow, and primary

if 'form_key' not in st.session_state:
    st.session_state.form_key = 0

# Add task section
with st.form(key=f"add_task_form_{st.session_state.form_key}"):
    st.subheader("Add a New Task")

    col1, col2 = st.columns([4,1])
    with col1:
        description = st.text_input(
            "Order / Task Description",
            help="Order: 1 (do first) or 2 (do after)",
            placeholder="1 - Do the dishes.",
            key=f"description_{st.session_state.form_key}"
        )
    with col2:
        due_date = st.date_input(
            "Due Date",
            key=f"due_date_{st.session_state.form_key}"
        )

    submitted = st.form_submit_button("Add Task")
    if submitted:
        if description:
                due_date_str = due_date.strftime("%Y-%m-%d") if due_date else None
                add_task(conn, description, due_date_str)
                st.session_state.task_added = True
                st.session_state.form_key += 1
                st.rerun()
        else:
                st.error("Please enter a description.")

# Show success message after the form
if "task_added" in st.session_state:
      st.success("Task added!")
      del st.session_state.task_added # Clear the flag so it doesn't show again

with st.container(border=True):
    col1, col2 = st.columns(2)

    with col1:
        # Filtering
        filter_option = st.selectbox(
            "Filter Tasks",
            ["All", "Complete", "Pending"],
            index=2, #defaults to "Pending" (index 2)
            key="filter_option"
        )
    with col2:
        # Sorting
        sort_option = st.selectbox(
            "Sort By",
            ["ID", "Due Date"],
            index=1, # defaults to "Due Date"
            key="sort_option"
        )

# Display tasks section
st.subheader(":primary[Your Tasks]")

# Fetch tasks based on the selected filter
if filter_option == "Complete":
     tasks = get_tasks(conn, status="complete")
elif filter_option == "Pending":
     tasks = get_tasks(conn, status="pending")
else:
    tasks = get_tasks(conn) # Show all tasks

# Sort tasks based on the selected option
if sort_option == "Due Date":
    # Separate tasks into those with due date and those without
    dated_tasks = [t for t in tasks if t[3]]
    undated_tasks = [t for t in tasks if not t[3]]

    # Sort tasks with due dates by date
    dated_tasks.sort(key=lambda x: datetime.strptime(x[3], "%Y-%m-%d").date())

    # Combine lists: dated tasks first (sorted), then undated tasks
    tasks = dated_tasks + undated_tasks
else:
    tasks.sort(key=lambda x: x[0]) # sort by ID

# Edit task form
for task in tasks:
    task_id, desc, status, due_date = task
    if f"editing_{task_id}" in st.session_state:
        with st.form(key=f"edit_form_{task_id}"):
            st.subheader(f"Edit Task {task_id}")
            new_desc = st.text_input("Description", value=desc, key=f"edit_desc_{task_id}")
            new_due_date = st.date_input("Due Date", value=due_date if due_date else None, key=f"edit_due_date_{task_id}")
            submitted = st.form_submit_button("Save Changes")
            if submitted:
                # Update the task in the database
                new_due_date_str = new_due_date.strftime("%Y-%m-%d") if new_due_date else None
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE tasks SET description = ?, due_date = ? WHERE id = ?",
                    (new_desc, new_due_date_str, task_id)
                )
                conn.commit()
                del st.session_state[f"editing_{task_id}"]  # Exit edit mode
                st.rerun()
            if st.form_submit_button("Cancel"):
                del st.session_state[f"editing_{task_id}"]  # Exit edit mode
                st.rerun()

if not tasks:
    st.info("No tasks yet! Add one above.")
else:
    for task in tasks:
         task_id, desc, status, due_date = task # Unpack task data
         with st.container(border=True): # Group task elements in a row
            col1, col2, col3, col4, col5 = st.columns([6, 1.3, .8, .8, .8], gap="small") # Split into 5 columns

            # Column 1: task description
            with col1:
                st.write(f"**{desc}**") # Bold task description

            # Column 2: Due date
            with col2:
                 if due_date:
                    st.write(f"{due_date}") # Show due date if it exists

            # Column 3: checkbox to toggle task status
            with col3:
                is_complete = st.checkbox(
                     "✅",
                     value=(status == "complete"),
                     key=f"checkbox_{task_id}" # Unique key per task
                )
                # Update status if checkbox is toggled
                if is_complete != (status == "complete"):
                     new_status = "complete" if is_complete else "pending"
                     update_task_status(conn, task_id, new_status)
                     st.rerun() # Refresh to show updated status

            # Column 4: Edit button
            with col4:
                if st.button("✏️", key=f"edit_{task_id}"):
                     st.session_state[f"editing_{task_id}"] = True
                     st.rerun()

            # Column 5: Delete button
            with col5:
                 if st.button("🗑️", key=f"delete_{task_id}"):
                      delete_task(conn,task_id)
                      st.rerun()