import os
import shutil
import glob
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter.ttk import Progressbar

def copy_to_ae_folder(selected_version, selected_items, progress):
    user_home = os.path.expanduser('~')
    dest_path = os.path.join(user_home, 'AppData', 'Roaming', 'Adobe', 'After Effects', selected_version, 'Scripts', 'ScriptUI Panels')

    if not os.path.exists(dest_path):
        messagebox.showerror("Error", f"Destination path does not exist: {dest_path}")
        return

    num_items = len(selected_items)
    progress['maximum'] = num_items

    for index, item in enumerate(selected_items):
        item_name = os.path.basename(item)
        target_path = os.path.join(dest_path, item_name)

        try:
            if os.path.isfile(item):
                shutil.copy2(item, target_path)
            elif os.path.isdir(item):
                if os.path.exists(target_path):
                    shutil.rmtree(target_path)
                shutil.copytree(item, target_path)

            progress['value'] = index + 1
            root.update_idletasks()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy {item_name}: {e}")
            continue

    messagebox.showinfo("Success", "Selected files/folders copied successfully.")
    update_current_files(selected_version)

def get_ae_versions():
    user_home = os.path.expanduser('~')
    ae_base_path = os.path.join(user_home, 'AppData', 'Roaming', 'Adobe', 'After Effects')
    return [os.path.basename(d) for d in glob.glob(os.path.join(ae_base_path, '*')) if os.path.isdir(d)]

def select_files_and_folders(listbox):
    # Start with an empty list
    items = []

    # Multi-selection of files and folders by running two dialogs sequentially
    selected_files = filedialog.askopenfilenames(title="Select Files")
    selected_dirs = filedialog.askdirectory(title="Select Folders")

    # Gather all selected items
    items.extend(selected_files)

    # Add directories if selected
    if selected_dirs:
        items.append(selected_dirs)
    
    # Clear and update the listbox with new selections
    listbox.delete(0, tk.END)
    for item in items:
        listbox.insert(tk.END, item)
        
    return items

def update_current_files(version):
    user_home = os.path.expanduser('~')
    path = os.path.join(user_home, 'AppData', 'Roaming', 'Adobe', 'After Effects', version, 'Scripts', 'ScriptUI Panels')

    if os.path.exists(path):
        current_files_listbox.delete(0, tk.END)
        for item in os.listdir(path):
            current_files_listbox.insert(tk.END, item)
    else:
        current_files_listbox.delete(0, tk.END)
        current_files_listbox.insert(tk.END, "Directory does not exist")

def on_version_change(event):
    selected_version = version_dropdown.get()
    update_current_files(selected_version)

def main():
    global root, version_dropdown, current_files_listbox
    root = tk.Tk()
    root.title("Copy Scripts to After Effects Version")
    root.geometry("600x500")

    available_versions = get_ae_versions()
    if not available_versions:
        messagebox.showerror("Error", "No After Effects versions found.")
        return

    tk.Label(root, text="Select After Effects Version:").pack(pady=10)

    selected_version = tk.StringVar()
    version_dropdown = ttk.Combobox(root, textvariable=selected_version, values=available_versions)
    version_dropdown.pack(pady=5)
    version_dropdown.current(0)
    version_dropdown.bind("<<ComboboxSelected>>", on_version_change)

    tk.Label(root, text="Selected Files/Folders:").pack(pady=5)
    
    listbox = tk.Listbox(root, selectmode=tk.MULTIPLE, width=80, height=10)
    listbox.pack(pady=5)

    selected_items = []  # Initialize here

    def open_file_dialog():
        nonlocal selected_items
        selected_items = select_files_and_folders(listbox)

    browse_btn = tk.Button(root, text="Browse", command=open_file_dialog)
    browse_btn.pack(pady=5)

    progress = Progressbar(root, orient='horizontal', mode='determinate', length=400)
    progress.pack(pady=20)

    copy_btn = tk.Button(root, text="Copy Files/Folders", command=lambda: copy_to_ae_folder(version_dropdown.get(), selected_items, progress))
    copy_btn.pack(pady=5)

    tk.Label(root, text="Current Files/Folders:").pack(pady=5)

    current_files_listbox = tk.Listbox(root, selectmode=tk.MULTIPLE, width=80, height=10)
    current_files_listbox.pack(pady=5)

    update_current_files(version_dropdown.get())

    root.mainloop()

if __name__ == "__main__":
    main()