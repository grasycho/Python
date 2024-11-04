import subprocess
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
import os

def check_and_install_package(package_name):
    """Check if a package is installed, and install it if it is not."""
    try:
        __import__(package_name)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])

def convert_to_exe():
    file_path = filedialog.askopenfilename(
        title="Select Python Script",
        filetypes=(("Python files", "*.py"), ("All files", "*.*"))
    )

    if not file_path:
        messagebox.showerror("Error", "No file selected")
        return

    check_and_install_package('pyinstaller')

    is_windowed = messagebox.askyesno(
        "Choose Application Type",
        "Would you like to create a windowed application (No console window)?"
    )

    pyinstaller_cmd = [
        sys.executable, "-m", "PyInstaller",
        '--onefile',
        '--windowed' if is_windowed else '--console',
        file_path
    ]

    try:
        completed_process = subprocess.run(
            pyinstaller_cmd, check=True, text=True, capture_output=True, shell=True
        )

        messagebox.showinfo("Success", f"Executable created successfully!\n\nOutput:\n{completed_process.stdout}")

    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"An error occurred:\n\n{e.stderr}")

def main():
    root = tk.Tk()
    root.title("Python to EXE Converter")
    root.geometry("400x300")

    instructions = tk.Label(
        root,
        text="Click 'Select Script' to choose the Python script you want to convert into an executable.",
        wraplength=350,
        justify="center"
    )
    instructions.pack(pady=20)

    select_btn = tk.Button(root, text="Select Script", command=convert_to_exe)
    select_btn.pack(pady=20)

    root.mainloop()

if __name__ == "__main__":
    main()