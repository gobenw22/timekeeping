import tkinter as tk
from tkinter import simpledialog, messagebox, ttk
import csv
import os
import sys
import subprocess
from datetime import datetime, timedelta
from collections import defaultdict

# Define the absolute path to the CSV file
csv_file_path = r'C:\Users\Benjamin Wildmon\Desktop\EnterHours\data_log.csv'
summary_file_path = r'C:\Users\Benjamin Wildmon\Desktop\EnterHours\weekly_summary.csv'

class CustomDialog(simpledialog.Dialog):
    def __init__(self, parent, title, prompt):
        self.prompt = prompt
        self.result = None
        super().__init__(parent, title)
        
    def body(self, master):
        tk.Label(master, text=self.prompt).pack(padx=5, pady=5)
        self.entry = tk.Entry(master)
        self.entry.pack(padx=5, pady=5)
        self.entry.focus_set()  # Set focus on the entry widget
        return self.entry

    def apply(self):
        self.result = self.entry.get()

def get_input(prompt):
    dialog = CustomDialog(root, "Input", prompt)
    return dialog.result

def get_data():
    root.withdraw()  # Hide the root window

    # Prompt for client name
    client_name = get_input("Enter client name:")
    if client_name is None:
        root.deiconify()  # Show the main window again
        return  # Exit if the user cancels

    # Prompt for task description
    task_description = get_input("Enter task description:")
    if task_description is None:
        root.deiconify()  # Show the main window again
        return  # Exit if the user cancels

    # Get the current time entry as a floating-point decimal
    entry_time = get_input("Enter hours worked (e.g., 1.25):")
    if entry_time is None:
        root.deiconify()  # Show the main window again
        return  # Exit if the user cancels

    try:
        entry_time_float = float(entry_time)  # Validate the input
    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter a valid number for hours worked.")
        root.deiconify()  # Show the main window again
        return

    # Get the current timestamp
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Store data in CSV
    with open(csv_file_path, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([client_name, task_description, entry_time_float, timestamp])
    
    root.deiconify()  # Show the main window again

def calculate_hours():
    total_hours_today = 0.0
    total_hours_week = 0.0
    today = datetime.now().date()
    week_start = today - timedelta(days=today.weekday())  # Monday of the current week

    if os.path.exists(csv_file_path):
        with open(csv_file_path, 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                try:
                    entry_date = datetime.strptime(row[3], '%Y-%m-%d %H:%M:%S').date()
                    entry_hours = float(row[2])
                    if entry_date == today:
                        total_hours_today += entry_hours
                    if entry_date >= week_start:
                        total_hours_week += entry_hours
                except (ValueError, IndexError):
                    continue

    return total_hours_today, total_hours_week

def display_hours():
    total_hours_today, total_hours_week = calculate_hours()
    messagebox.showinfo("Total Hours", f"Total hours entered today: {total_hours_today:.2f}\nTotal hours entered this week: {total_hours_week:.2f}")

def prompt_for_data():
    while True:
        get_data()
        if not tk.messagebox.askyesno("Continue?", "Do you want to enter another entry?"):
            break

def clear_data_log():
    if messagebox.askyesno("Clear Data Log", "Are you sure you want to clear the data log? This action cannot be undone."):
        with open(csv_file_path, 'w', newline='') as file:
            pass  # Opening in 'w' mode with no content clears the file
        messagebox.showinfo("Data Log Cleared", "The data log has been cleared.")

def open_data_log():
    try:
        subprocess.Popen(['code', csv_file_path])
    except Exception as e:
        messagebox.showerror("Error", f"Failed to open file in VS Code: {e}")

def open_weekly_summary():
    try:
        subprocess.Popen(['code', summary_file_path])
    except Exception as e:
        messagebox.showerror("Error", f"Failed to open weekly summary in VS Code: {e}")

def show_todays_entries():
    today = datetime.now().date()
    entries = []

    if os.path.exists(csv_file_path):
        with open(csv_file_path, 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                try:
                    entry_date = datetime.strptime(row[3], '%Y-%m-%d %H:%M:%S').date()
                    if entry_date == today:
                        entries.append(row)
                except (ValueError, IndexError):
                    continue

    if entries:
        display_entries_table(entries)
    else:
        messagebox.showinfo("Today's Entries", "No entries found for today.")

def display_entries_table(entries):
    table_window = tk.Toplevel(root)
    table_window.title("Today's Entries")
    
    tree = ttk.Treeview(table_window, columns=("Client", "Task", "Hours", "Time"), show='headings')
    tree.heading("Client", text="Client")
    tree.heading("Task", text="Task")
    tree.heading("Hours", text="Hours")
    tree.heading("Time", text="Time")
    
    for entry in entries:
        tree.insert('', 'end', values=entry)
    
    tree.pack(expand=True, fill='both')

def generate_weekly_summary():
    weekly_summary = defaultdict(lambda: {'total_hours': 0.0, 'tasks': []})
    week_start = (datetime.now() - timedelta(days=datetime.now().weekday())).date()

    if os.path.exists(csv_file_path):
        with open(csv_file_path, 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                try:
                    entry_date = datetime.strptime(row[3], '%Y-%m-%d %H:%M:%S').date()
                    if entry_date >= week_start:
                        client_name = row[0]
                        task_description = row[1]
                        entry_hours = float(row[2])
                        key = (entry_date, client_name)

                        weekly_summary[key]['total_hours'] += entry_hours
                        weekly_summary[key]['tasks'].append(task_description)
                except (ValueError, IndexError):
                    continue

    with open(summary_file_path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Date', 'Client', 'Total Hours', 'Tasks'])

        for (date, client), data in weekly_summary.items():
            tasks = "; ".join(data['tasks'])
            writer.writerow([date, client, data['total_hours'], tasks])

    messagebox.showinfo("Weekly Summary", f"Weekly summary saved to {summary_file_path}")

def soft_lock():
    global root
    root = tk.Tk()
    root.geometry("400x400")
    root.title("Data Entry Required")

    def on_enter_data():
        prompt_for_data()
        display_hours()

    def on_end_script():
        root.destroy()
        sys.exit()

    label = tk.Label(root, text="Please enter the data to proceed.", font=("Arial", 14))
    label.pack(pady=30)

    enter_data_button = tk.Button(root, text="Enter Data", command=on_enter_data)
    enter_data_button.pack(pady=5)

    show_entries_button = tk.Button(root, text="Show Today's Entries", command=show_todays_entries)
    show_entries_button.pack(pady=5)
    
    clear_data_log_button = tk.Button(root, text="Clear Data Log", command=clear_data_log)
    clear_data_log_button.pack(pady=5)

    open_data_log_button = tk.Button(root, text="Open Data Log", command=open_data_log)
    open_data_log_button.pack(pady=5)

    summary_button = tk.Button(root, text="Generate Weekly Summary", command=generate_weekly_summary)
    summary_button.pack(pady=5)

    open_weekly_summary_button = tk.Button(root, text="Open Weekly Summary", command=open_weekly_summary)
    open_weekly_summary_button.pack(pady=5)

    end_script_button = tk.Button(root, text="End Script", command=on_end_script)
    end_script_button.pack(pady=5)

    root.mainloop()

if __name__ == "__main__":
    soft_lock()
