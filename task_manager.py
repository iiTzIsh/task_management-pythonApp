import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from tkcalendar import Calendar

# Database Setup
def init_db():
    conn = sqlite3.connect("task_manager.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS tasks (
                        id INTEGER PRIMARY KEY,
                        name TEXT,
                        description TEXT,
                        deadline TEXT,
                        category TEXT,
                        priority INTEGER)''') 
    cursor.execute('''CREATE TABLE IF NOT EXISTS completed_tasks (
                        id INTEGER PRIMARY KEY,
                        name TEXT,
                        description TEXT,
                        deadline TEXT,
                        category TEXT,
                        priority INTEGER)''') 
    conn.commit()
    conn.close()

# Add Task
def add_task(name, description, deadline, category, priority):
    conn = sqlite3.connect("task_manager.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tasks (name, description, deadline, category, priority) VALUES (?, ?, ?, ?, ?)",
                   (name, description, deadline, category, priority))
    conn.commit()
    conn.close()
    refresh_task_list()

# Move Task to Completed Tasks
def mark_task_complete():
    selected_item = treeview.selection()
    if selected_item:
        task_id = treeview.item(selected_item[0])["values"][0]
        conn = sqlite3.connect("task_manager.db")
        cursor = conn.cursor()

        # Fetch task from the tasks table
        cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        task = cursor.fetchone()

        if task:
            # Move task to completed_tasks table
            cursor.execute('''INSERT INTO completed_tasks (id, name, description, deadline, category, priority) 
                              VALUES (?, ?, ?, ?, ?, ?)''', task)
            
            # Delete task from tasks table
            cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            conn.commit()

            # Remove from treeview and refresh
            treeview.delete(selected_item[0])
            refresh_task_list()

        conn.close()

# View Completed Tasks
def view_completed_tasks():
    completed_window = tk.Toplevel()
    completed_window.title("Completed Tasks")

    columns = ("Name", "Description", "Deadline", "Category", "Priority")
    completed_treeview = ttk.Treeview(completed_window, columns=columns, show="headings", height=15)
    completed_treeview.grid(row=0, column=0, columnspan=4, padx=20, pady=20)

    # Columns configuration
    for col in columns:
        completed_treeview.heading(col, text=col, anchor=tk.W)
        completed_treeview.column(col, anchor=tk.W, width=150)

    # Fetch completed tasks from the database and display
    conn = sqlite3.connect("task_manager.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM completed_tasks ORDER BY priority")
    tasks = cursor.fetchall()
    conn.close()

    for task in tasks:
        completed_treeview.insert("", "end", values=(task[1], task[2], task[3], task[4], task[5]))

# Delete Task
def delete_task():
    selected_item = treeview.selection()
    if selected_item:
        task_id = treeview.item(selected_item[0])["values"][0]
        confirm = messagebox.askyesno("Delete Task", "Are you sure you want to delete this task?")
        if confirm:
            conn = sqlite3.connect("task_manager.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            conn.commit()
            conn.close()

            # Remove the task from the treeview
            treeview.delete(selected_item[0])
            refresh_task_list()
        else:
            messagebox.showinfo("Info", "Task not deleted.")

# Refresh Task List
def refresh_task_list():
    for row in treeview.get_children():
        treeview.delete(row)  

    conn = sqlite3.connect("task_manager.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks ORDER BY priority")
    tasks = cursor.fetchall()
    conn.close()

    # Populate treeview with tasks
    for task in tasks:
        treeview.insert("", "end", values=(task[0], task[1], task[2], task[3], task[4], task[5]))  

# Add Task Dialog
def add_task_dialog():
    def save_task():
        name = name_var.get()
        description = description_var.get("1.0", "end-1c")
        deadline = deadline_var.get_date()
        category = category_var.get()
        priority = priority_var.get()

        if name and deadline:
            add_task(name, description, deadline, category, priority)
            add_dialog.destroy()
        else:
            messagebox.showerror("Input Error", "Task Name and Deadline are required.")

    add_dialog = tk.Toplevel()
    add_dialog.title("Add Task")

    name_var = tk.StringVar()
    description_var = tk.Text(add_dialog, height=5, width=40) 
    deadline_var = Calendar(add_dialog, selectmode="day") 
    category_var = tk.StringVar()
    priority_var = tk.IntVar()

    # Layout
    ttk.Label(add_dialog, text="Task Name:").grid(row=0, column=0, padx=10, pady=10)
    ttk.Entry(add_dialog, textvariable=name_var).grid(row=0, column=1, padx=10, pady=10)

    ttk.Label(add_dialog, text="Description:").grid(row=1, column=0, padx=10, pady=10)
    description_var.grid(row=1, column=1, padx=10, pady=10)

    ttk.Label(add_dialog, text="Deadline:").grid(row=2, column=0, padx=10, pady=10)
    deadline_var.grid(row=2, column=1, padx=10, pady=10)

    ttk.Label(add_dialog, text="Category:").grid(row=3, column=0, padx=10, pady=10)
    category_dropdown = ttk.OptionMenu(add_dialog, category_var, "Work", "Personal", "Education", "Event", "Creative")
    category_dropdown.grid(row=3, column=1, padx=10, pady=10)

    ttk.Label(add_dialog, text="Priority:").grid(row=4, column=0, padx=10, pady=10)
    priority_dropdown = ttk.OptionMenu(add_dialog, priority_var, 1, 2, 3, 4, 5) 
    priority_dropdown.grid(row=4, column=1, padx=10, pady=10)

    ttk.Button(add_dialog, text="Add Task", command=save_task).grid(row=5, column=0, columnspan=2, pady=10)

# UI Setup
root = tk.Tk()
root.title("Task Management System")
root.geometry("950x500")
root.iconbitmap('logo.ico')
root.resizable(False,False)  

# Treeview for tasks 
columns = ("ID", "Name", "Description", "Deadline", "Category", "Priority")  
treeview = ttk.Treeview(root, columns=columns, show="headings", height=15)
treeview.grid(row=0, column=0, columnspan=4, padx=20, pady=20)

# Columns configuration
for col in columns:
    treeview.heading(col, text=col, anchor=tk.W)
    treeview.column(col, anchor=tk.W, width=150)

# Buttons in a frame for better layout and styling
button_frame = ttk.Frame(root)
button_frame.grid(row=1, column=0, columnspan=4, pady=20)
label_frame = ttk.Frame(root)
label_frame.grid(row=2, column=0, columnspan=4, pady=20)

ttk.Button(button_frame, text="Add Task", command=add_task_dialog, width=20).grid(row=0, column=0, padx=10, pady=10)
ttk.Button(button_frame, text="Mark as Complete", command=mark_task_complete, width=20).grid(row=0, column=1, padx=10, pady=10)
ttk.Button(button_frame, text="Completed Tasks", command=view_completed_tasks, width=20).grid(row=0, column=3, padx=10, pady=10)
ttk.Button(button_frame, text="Delete Task", command=delete_task, width=20).grid(row=0, column=2, padx=10, pady=10)
ttk.Label(label_frame,text='Developed by Ishara Madusanka #fun_project :)').grid(row=0, column=3, padx=10, pady=5)


# Initializing 
init_db()
refresh_task_list()

root.mainloop()
