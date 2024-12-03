import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.ttk import Progressbar

# Path to ExifTool; replace it with your actual ExifTool path
EXIFTOOL_PATH = r"C:\exiftool\exiftool.exe"
SUPPORTED_FORMATS = (".jpg", ".png", ".tiff", ".psd")  # Add more formats if needed


def log_message(message, log_box, color="black"):
    """
    Append messages to the log box with color-coding for status (errors and successes).
    """
    log_box.config(state=tk.NORMAL)
    log_box.insert(tk.END, message + "\n", color)
    log_box.tag_config("red", foreground="red")      # Errors
    log_box.tag_config("green", foreground="green")  # Successes
    log_box.tag_config("black", foreground="black")  # Neutral messages
    log_box.see(tk.END)  # Auto-scroll
    log_box.config(state=tk.DISABLED)


def process_metadata(txt_file, image_file, log_box, metadata):
    """
    Process metadata from input .txt file and user-provided fields.
    Applies the data to the image file using ExifTool.
    """
    try:
        log_message(f"Processing '{os.path.basename(image_file)}' with metadata from '{os.path.basename(txt_file)}'", log_box)

        # Read the metadata from the TXT file
        with open(txt_file, "r") as f:
            lines = f.readlines()

        # Extract metadata fields
        title = next((line.split(":", 1)[1].strip() for line in lines if line.lower().startswith("title:")), "")
        description = next((line.split(":", 1)[1].strip() for line in lines if line.lower().startswith("description:")), "")
        keywords = next((line.split(":", 1)[1].strip().split(",") for line in lines if line.lower().startswith("keywords:")), [])

        # Prepare ExifTool commands
        commands = [EXIFTOOL_PATH]

        # Title and Title Prefix
        if metadata["title_prefix"] or title:
            full_title = f"{metadata['title_prefix']} {title}".strip()
            commands.extend([
                f"-XMP-dc:Title={full_title}",  # Title in XMP namespace
                f"-photoshop:Headline={full_title}"  # Headline for Photoshop metadata
            ])

        # Description
        if description:
            commands.append(f"-XMP-dc:Description={description}")

        # Keywords
        for keyword in keywords + metadata["additional_keywords"].split(","):
            if keyword.strip():
                commands.append(f"-XMP-dc:Subject={keyword.strip()}")

        # Author Name
        if metadata["author_name"]:
            commands.append(f"-XMP-dc:Creator={metadata['author_name']}")

        # Author Title
        if metadata["author_title"]:
            commands.append(f"-XMP-photoshop:AuthorsPosition={metadata['author_title']}")

        # Copyright Information
        if metadata["copyright_status"]:
            if metadata["copyright_info"]:
                commands.extend([
                    f"-IPTC:CopyrightNotice={metadata['copyright_info']}",
                    f"-XMP-dc:Rights={metadata['copyright_info']}"
                ])
            else:
                commands.append(f"-IPTC:CopyrightNotice=Copyrighted")

        # Copyright URL
        if metadata["copyright_url"]:
            commands.append(f"-XMP-xmpRights:WebStatement={metadata['copyright_url']}")

        # Rating
        if metadata["rating"]:
            commands.append(f"-XMP-xmp:Rating={metadata['rating']}")  # Rating (1–5)

        # Overwrite the file
        commands.extend(["-overwrite_original", image_file])

        # Run ExifTool command
        result = subprocess.run(commands, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # Handle ExifTool output
        if result.returncode == 0:
            log_message(f"✔️ Metadata successfully applied to '{os.path.basename(image_file)}'", log_box, "green")
            return True
        else:
            log_message(f"Error: {result.stderr}", log_box, "red")
            return False
    except Exception as e:
        log_message(f"Error processing '{image_file}': {e}", log_box, "red")
        return False


def process_folder(folder, metadata, progress_var, progress_bar, log_box):
    """
    Process all .txt and corresponding image files in the folder.
    """
    txt_files = [f for f in os.listdir(folder) if f.endswith(".txt")]
    if not txt_files:
        log_message("No .txt files found in the selected folder.", log_box, "red")
        return

    progress_bar["maximum"] = len(txt_files)
    processed, errors = 0, 0

    for idx, txt_file in enumerate(txt_files):
        txt_path = os.path.join(folder, txt_file)
        base_name = os.path.splitext(txt_file)[0]

        # Find the matching image file
        image_file = next(
            (os.path.join(folder, f"{base_name}{ext}") for ext in SUPPORTED_FORMATS if os.path.exists(os.path.join(folder, f"{base_name}{ext}"))),
            None
        )

        if image_file:
            success = process_metadata(txt_path, image_file, log_box, metadata)
            if success:
                processed += 1
            else:
                errors += 1
        else:
            log_message(f"No matching image found for '{txt_file}'. Skipping.", log_box, "red")
            errors += 1

        # Update progress bar
        progress_var.set(idx + 1)
        progress_bar.update_idletasks()

    messagebox.showinfo("Processing Complete", f"Processed {processed} files successfully with {errors} errors.")


def main():
    root = tk.Tk()
    root.title("Image Metadata Processor")
    root.geometry("900x620")

    metadata = {
        "title_prefix": tk.StringVar(),
        "additional_keywords": tk.StringVar(),
        "author_name": tk.StringVar(),
        "author_title": tk.StringVar(),
        "copyright_status": tk.IntVar(),
        "copyright_info": tk.StringVar(),
        "copyright_url": tk.StringVar(),
        "rating": tk.IntVar(),
    }

    # Folder selection
    tk.Label(root, text="Selected Folder:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
    folder_path = tk.StringVar()
    tk.Entry(root, textvariable=folder_path, state="readonly", width=60).grid(row=0, column=1, padx=10, pady=5)
    tk.Button(root, text="Browse", command=lambda: browse_folder(folder_path)).grid(row=0, column=2, padx=10, pady=5)

    # Input fields
    input_fields = [
        ("Title Prefix:", "title_prefix"),
        ("Additional Keywords (comma-separated):", "additional_keywords"),
        ("Author Name:", "author_name"),
        ("Author Title:", "author_title"),
        ("Copyright Notice:", "copyright_info"),
        ("Copyright URL:", "copyright_url"),
        ("Rating (1-5):", "rating"),
    ]
    for idx, (label, field) in enumerate(input_fields, start=1):
        tk.Label(root, text=label).grid(row=idx, column=0, padx=10, pady=5, sticky="w")
        tk.Entry(root, textvariable=metadata[field]).grid(row=idx, column=1, padx=10, pady=5, sticky="w")

    # Copyright checkbox
    tk.Checkbutton(root, text="Copyrighted", variable=metadata["copyright_status"]).grid(row=5, column=2, padx=10, pady=5)

    # Progress bar and log box
    progress_var = tk.IntVar()
    progress_bar = Progressbar(root, orient="horizontal", length=750, mode="determinate", variable=progress_var)
    progress_bar.grid(row=10, column=0, columnspan=2, padx=10, pady=10)
    log_box = tk.Text(root, height=15, state="disabled")
    log_box.grid(row=11, column=0, columnspan=2, padx=10, pady=10)

    # Buttons
    def run_process():
        folder = folder_path.get()
        if not folder:
            messagebox.showerror("Error", "Please select a folder to process.")
            return
        process_folder(folder, {key: var.get() for key, var in metadata.items()}, progress_var, progress_bar, log_box)

    tk.Button(root, text="Run", command=run_process).grid(row=12, column=1, padx=10, pady=10, sticky="w")
    tk.Button(root, text="Exit", command=root.quit).grid(row=12, column=2, padx=10, pady=10, sticky="w")

    root.mainloop()


def browse_folder(folder_path_var):
    """
    Browse for a folder and set the selected path.
    """
    folder = filedialog.askdirectory(title="Select Folder")
    if folder:
        folder_path_var.set(folder)


if __name__ == "__main__":
    main()