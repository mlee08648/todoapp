import sqlite3
from datetime import datetime

def connect_db():
     return sqlite3.connect('tasks.db')

def init_db(conn):
    cursor = conn.cursor() # If adding new column, do it below under CREATE; modifying a column label requires creating a new table and copying data over; easier to just add a new column.
    cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   description TEXT NOT NULL,
                   status TEXT DEFAULT 'pending',
                   due_date DATE
            )
    ''')
    conn.commit()

def add_task(conn, description, due_date=None):
    cursor = conn.cursor()
    if due_date:
        try:
              datetime.strptime(due_date, "%Y-%m-%d")
        except ValueError:
            print("Invalid date format! Use YYYY-MM-DD (e.g., 2026-12-31).")
            return
    cursor.execute("INSERT INTO tasks (description, due_date) VALUES (?, ?)", (description, due_date)) # ? added as placeholder to prevent SQL injection security risk
    conn.commit()

def get_tasks(conn, status=None): # status=None is a default behavior: if no specific status is provided, every task is retrieved but if status="pending", only pending tasks are retrieved
    cursor = conn.cursor()
    if status:
        cursor.execute("SELECT id, description, status, due_date FROM tasks WHERE status = ?", (status,))
    else:
        cursor.execute("SELECT id, description, status, due_date FROM tasks")
    return cursor.fetchall()

def update_task_status(conn, task_id, new_status):
    cursor = conn.cursor()
    cursor.execute("UPDATE tasks SET status = ? WHERE id = ?", (new_status, task_id))
    conn.commit()

def update_task(conn, task_id, description, due_date=None):
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE tasks SET description = ?, due_date = ? WHERE id = ?",
        (description, due_date, task_id)
    )
    conn.commit()

def delete_task(conn, task_id):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()

# Putting the CLI loop inside this function.
def run_cli():
    conn = connect_db()
    init_db(conn)

    while True:
        print("\nChoose an action:")
        print("1. Add task")
        print("2. View tasks")
        print("3. Mark task complete")
        print("4. Delete task")
        print("5. Exit")

        choice = input("Enter your choice: ")

        try:
            if choice == '1':
                    description = input("Enter task description: ")
                    due_date = input("Enter due date (YYYY-MM-DD, optional): ")
                    add_task(conn, description, due_date)
                    print("Task added.")

            elif choice == '2':
                    tasks = get_tasks(conn)
                    if tasks:
                        print("\nTasks:")
                        for task in tasks:
                                print(f"ID: {task[0]}, Description: {task[1]}, Status: {task[2]}, Due Date: {task[3]}")
                    else:
                        print("No tasks found.")

            elif choice == '3':
                    tasks = get_tasks(conn, status='pending') # Only show pending tasks
                    if tasks:
                        print("\nPending Tasks:")
                        for task in tasks:
                            print(f"ID: {task[0]}, Description: {task[1]}, Status: {task[2]}, Due Date: {task[3]}")
                        try:
                                task_id = int(input("Enter the ID of the task to mark complete: "))
                                update_task_status(conn, task_id, 'complete')
                                print("Task status updated.")
                        except ValueError:
                                print("Invalid task ID. Please enter a number.")
                        except Exception as e:
                                print(f"An error occurred: {e}")
                    else:
                        print("No pending tasks found.")

            elif choice == '4':
                    tasks = get_tasks(conn)
                    if tasks:
                        print("\nTasks:")
                        for task in tasks:
                            print(f"ID: {task[0]}, Description: {task[1]}, Status: {task[2]}, Due Date: {task[3]}")
                        try:
                            task_id = int(input("Enter the ID of the task to delete: "))
                            delete_task(conn, task_id)
                            print("Task deleted.")
                        except ValueError:
                            print("Invalid task ID. Please enter a number.")
                        except Exception as e:
                            print(f"An error occurrred: {e}")
                    else:
                        print("No tasks found.")
            elif choice == '5':
                break
            else:
                print("Invalid choice.")
        except ValueError:
            print("Invalid input. Please enter a number.")
        except sqlite3.Error as e:
            print(f"A database error ocurred: {e}")
        except Exception as e:
            print(f"An unxpected error occurrred: {e}")

    conn.commit()
    conn.close() 

# Ensures the CLI only runs when you execute directly from todo_logic.py
if __name__ == "__main__":
     run_cli()                     