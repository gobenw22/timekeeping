import tkinter as tk
from tkinter import simpledialog, messagebox
import csv
import os
import sys
import subprocess
from datetime import datetime, timedelta

# Define the absolute path to the CSV file
csv_file_path = r'C:\Users\Benjamin Wildmon\Desktop\data_log.csv'

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

def soft_lock():
    global root
    root = tk.Tk()
    root.geometry("400x300")
    root.title("Data Entry Required")

    def on_enter_data():
        prompt_for_data()
        display_hours()

    def on_end_script():
        root.destroy()
        sys.exit()

    label = tk.Label(root, text="Please enter the data to proceed.", font=("Arial", 14))
    label.pack(pady=50)

    enter_data_button = tk.Button(root, text="Enter Data", command=on_enter_data)
    enter_data_button.pack(pady=10)

    clear_data_log_button = tk.Button(root, text="Clear Data Log", command=clear_data_log)
    clear_data_log_button.pack(pady=10)

    open_data_log_button = tk.Button(root, text="Open Data Log", command=open_data_log)
    open_data_log_button.pack(pady=10)

    end_script_button = tk.Button(root, text="End Script", command=on_end_script)
    end_script_button.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    soft_lock()
