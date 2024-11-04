import os
import sys
import subprocess
from PIL import Image, ImageTk, ImageFont, ImageDraw
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# Check Pillow version for Resampling compatibility
try:
    from PIL import Resampling
    resampling_method = Resampling.LANCZOS
except ImportError:
    # For older Pillow versions
    resampling_method = Image.LANCZOS

class ImageResizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Resizer by Mehmet Sensoy")
        self.root.geometry("600x500")
        self.root.resizable(False, False)
        
        self.image_paths = []
        self.original_width = None
        self.original_height = None
        self.aspect_ratio = None
        self.is_proportionate_checked = tk.BooleanVar(value=True)
        self.is_updating_size = False  # Flag to prevent recursive calls

        # Initialize style and themes
        self.style = ttk.Style()
        self.available_themes = ["Default", "Dark", "Light Blue", "Custom 1", "Custom 2"]
        self.current_theme = tk.StringVar(value="Default")

        # Apply default theme
        self.apply_theme("Default")

        # Title Label
        title_label = tk.Label(root, text="Image Resizer Tool", font=("Helvetica", 16, "bold"))
        title_label.pack(pady=10)

        # Theme Selection Frame
        theme_frame = tk.Frame(root)
        theme_frame.pack(pady=5)

        theme_label = tk.Label(theme_frame, text="Select Theme:")
        theme_label.pack(side=tk.LEFT, padx=5)

        self.theme_dropdown = ttk.Combobox(theme_frame, textvariable=self.current_theme, values=self.available_themes, state="readonly", width=20)
        self.theme_dropdown.bind("<<ComboboxSelected>>", self.change_theme)
        self.theme_dropdown.pack(side=tk.LEFT, padx=5)

        # Directory Selection Frame
        dir_frame = tk.Frame(root)
        dir_frame.pack(pady=5)

        self.select_folder_button = tk.Button(dir_frame, text="Select Folder", command=self.select_folder)
        self.select_folder_button.pack(side=tk.LEFT, padx=5)

        self.directory_label = tk.Label(dir_frame, text="No folder selected", wraplength=400)
        self.directory_label.pack(side=tk.LEFT, padx=5)

        # Image Info Label
        self.info_label = tk.Label(root, text="", wraplength=450)
        self.info_label.pack(pady=5)

        # Resize Options Frame
        options_frame = tk.Frame(root)
        options_frame.pack(pady=10)

        options_label = tk.Label(options_frame, text="Select Resize Option:")
        options_label.pack(side=tk.LEFT, padx=5)

        self.resize_options = [
            "2X Downscale", "2X Upscale",
            "3X Downscale", "3X Upscale",
            "4X Downscale", "4X Upscale",
            "1.5X Downscale", "1.5X Upscale",
            "5X Downscale", "5X Upscale",
            "Custom"
        ]
        self.resize_var = tk.StringVar(value=self.resize_options[0])
        self.resize_dropdown = ttk.Combobox(options_frame, textvariable=self.resize_var, values=self.resize_options, state="readonly", width=20)
        self.resize_dropdown.bind("<<ComboboxSelected>>", self.on_resize_option_change)
        self.resize_dropdown.pack(side=tk.LEFT, padx=5)

        # Custom Size Frame
        self.custom_size_frame = tk.Frame(root)
        self.custom_size_frame.pack(pady=5)

        self.custom_width_label = tk.Label(self.custom_size_frame, text="Width:")
        self.custom_width_label.grid(row=0, column=0, padx=5, pady=5)

        self.custom_width_var = tk.StringVar()
        self.custom_width_var.trace('w', self.on_width_change)
        self.custom_width_entry = ttk.Entry(self.custom_size_frame, textvariable=self.custom_width_var, width=10)
        self.custom_width_entry.grid(row=0, column=1, padx=5, pady=5)

        self.custom_height_label = tk.Label(self.custom_size_frame, text="Height:")
        self.custom_height_label.grid(row=0, column=2, padx=5, pady=5)

        self.custom_height_var = tk.StringVar()
        self.custom_height_var.trace('w', self.on_height_change)
        self.custom_height_entry = ttk.Entry(self.custom_size_frame, textvariable=self.custom_height_var, width=10)
        self.custom_height_entry.grid(row=0, column=3, padx=5, pady=5)

        self.proportional_checkbox = tk.Checkbutton(self.custom_size_frame, text="Proportional", variable=self.is_proportionate_checked)
        self.proportional_checkbox.grid(row=0, column=4, padx=5, pady=5)

        # Hide the custom size frame initially
        self.custom_size_frame.pack_forget()

        # Progress Bar
        self.progress_bar = ttk.Progressbar(root, orient="horizontal", mode="determinate", length=400)
        self.progress_bar.pack(pady=10)

        # Button Frame
        self.button_frame = tk.Frame(root)
        self.ok_button = tk.Button(self.button_frame, text="OK", command=self.process_images, state=tk.DISABLED, width=10)
        self.ok_button.pack(side=tk.LEFT, padx=20)
        self.cancel_button = tk.Button(self.button_frame, text="CANCEL", command=root.quit, width=10)
        self.cancel_button.pack(side=tk.LEFT, padx=20)
        self.button_frame.pack(pady=10)
        
    def select_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.image_paths = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.lower().endswith(('png', 'jpg', 'jpeg'))]
            if self.image_paths:
                self.directory_label.config(text=f"Selected Folder: {folder_path}")
                self.display_image_info(self.image_paths[0])
                self.ok_button.config(state=tk.NORMAL)
            else:
                messagebox.showerror("Error", "No images found in the selected folder.")

    def display_image_info(self, first_image_path):
        with Image.open(first_image_path) as img:
            self.original_width, self.original_height = img.size
        self.aspect_ratio = self.original_width / self.original_height
        self.info_label.config(text=f"Total images: {len(self.image_paths)}\nFirst image size: {self.original_width}x{self.original_height}")

    def on_resize_option_change(self, event=None):
        """ Show or hide custom size inputs based on the selected option """
        if self.resize_var.get() == "Custom":
            self.custom_size_frame.pack(pady=5)
            self.custom_width_var.set(str(self.original_width))
            self.custom_height_var.set(str(self.original_height))
        else:
            self.custom_size_frame.pack_forget()

    def on_width_change(self, *args):
        if not self.is_proportionate_checked.get():
            return
        if self.is_updating_size:
            return  # Prevent recursive calls
        self.is_updating_size = True
        try:
            width_text = self.custom_width_var.get()
            if width_text.isdigit() and int(width_text) > 0:
                new_width = int(width_text)
                new_height = int(new_width / self.aspect_ratio)
                self.custom_height_var.set(str(new_height))
        except ValueError:
            pass
        self.is_updating_size = False

    def on_height_change(self, *args):
        if not self.is_proportionate_checked.get():
            return
        if self.is_updating_size:
            return  # Prevent recursive calls
        self.is_updating_size = True
        try:
            height_text = self.custom_height_var.get()
            if height_text.isdigit() and int(height_text) > 0:
                new_height = int(height_text)
                new_width = int(new_height * self.aspect_ratio)
                self.custom_width_var.set(str(new_width))
        except ValueError:
            pass
        self.is_updating_size = False
    def process_images(self):
        scale_factor = 1
        preset_name = self.resize_var.get()
        
        if preset_name == "Custom":
            try:
                new_width = int(self.custom_width_var.get())
                new_height = int(self.custom_height_var.get())
                if new_width <= 0 or new_height <= 0:
                    raise ValueError("Width and Height must be positive integers.")
            except ValueError as e:
                messagebox.showerror("Error", f"Invalid custom size: {e}")
                return
            output_folder_name = f"Resized_{new_width}x{new_height}"
        else:
            output_folder_name = f"Resized_{preset_name.replace(' ', '_')}"

        output_folder = os.path.join(os.path.dirname(self.image_paths[0]), output_folder_name)
        os.makedirs(output_folder, exist_ok=True)

        # Map presets to scale factors
        preset_scale_factors = {
            "2X Downscale": 0.5,
            "2X Upscale": 2,
            "3X Downscale": 1/3,
            "3X Upscale": 3,
            "4X Downscale": 0.25,
            "4X Upscale": 4,
            "5X Downscale": 0.2,
            "5X Upscale": 5,
            "1.5X Downscale": 2/3,
            "1.5X Upscale": 1.5,
        }

        if preset_name in preset_scale_factors:
            scale_factor = preset_scale_factors[preset_name]

        for index, image_path in enumerate(self.image_paths, start=1):
            with Image.open(image_path) as img:
                if preset_name == "Custom":
                    new_size = (new_width, new_height)
                else:
                    new_size = (
                        int(img.width * scale_factor), int(img.height * scale_factor))
                    
                resized_img = img.resize(new_size, resampling_method)
                base_filename = os.path.basename(image_path)
                resized_img.save(os.path.join(output_folder, base_filename))

            self.update_progress(index / len(self.image_paths) * 100)
        
        messagebox.showinfo("Success", f"Images have been resized and saved to {output_folder}")
        self.progress_bar['value'] = 0  # Reset progress bar

        # Open the output folder
        self.open_output_folder(output_folder)
    def update_progress(self, value):
        self.progress_bar['value'] = value
        self.root.update_idletasks()

    def change_theme(self, event=None):
        selected_theme = self.current_theme.get()
        self.apply_theme(selected_theme)

    def apply_theme(self, theme_name):
        # Reset to default style
        self.style.theme_use('default')

        if theme_name == "Default":
            self.root.configure(bg='SystemButtonFace')
            fg_color = 'black'
            self.style.configure('.', background='SystemButtonFace', foreground=fg_color)
        elif theme_name == "Dark":
            bg_color = '#2e2e2e'
            fg_color = 'white'
            self.root.configure(bg=bg_color)
            self.style.configure('.', background=bg_color, foreground=fg_color)
            self.style.map('TButton', background=[('active', bg_color)], foreground=[('active', fg_color)])
        elif theme_name == "Light Blue":
            bg_color = '#e6f2ff'
            fg_color = 'black'
            self.root.configure(bg=bg_color)
            self.style.configure('.', background=bg_color, foreground=fg_color)
        elif theme_name == "Custom 1":
            # Example of a custom theme
            bg_color = '#ffe6e6'
            fg_color = 'black'
            self.root.configure(bg=bg_color)
            self.style.configure('.', background=bg_color, foreground=fg_color)
        elif theme_name == "Custom 2":
            bg_color = '#e6ffe6'
            fg_color = 'black'
            self.root.configure(bg=bg_color)
            self.style.configure('.', background=bg_color, foreground=fg_color)

        # Update all widgets
        for widget in self.root.winfo_children():
            self.update_widget_style(widget, fg_color, bg_color)

    def update_widget_style(self, widget, fg_color, bg_color):
        if isinstance(widget, tk.Frame):
            widget.configure(bg=bg_color)
            for child in widget.winfo_children():
                self.update_widget_style(child, fg_color, bg_color)
        elif isinstance(widget, tk.Label):
            widget.configure(bg=bg_color, fg=fg_color)
        elif isinstance(widget, tk.Button):
            widget.configure(bg=bg_color, fg=fg_color)
        elif isinstance(widget, ttk.Combobox):
            widget.configure(style='Custom.TCombobox')
            self.style.configure('Custom.TCombobox', fieldbackground=bg_color, background=bg_color, foreground=fg_color)
        elif isinstance(widget, ttk.Entry):
            widget.configure(style='Custom.TEntry')
            self.style.configure('Custom.TEntry', fieldbackground=bg_color, background=bg_color, foreground=fg_color)
        elif isinstance(widget, tk.Checkbutton):
            widget.configure(bg=bg_color, fg=fg_color, activebackground=bg_color, selectcolor=bg_color)
        elif isinstance(widget, ttk.Progressbar):
            self.style.configure('TProgressbar', background=fg_color)
        elif isinstance(widget, ttk.Button):
            widget.configure(style='Custom.TButton')
            self.style.configure('Custom.TButton', background=bg_color, foreground=fg_color)

    def open_output_folder(self, folder_path):
        # Open the output folder in the file explorer
        if os.name == 'nt':  # Windows
            os.startfile(folder_path)
        elif os.name == 'posix':  # macOS or Linux
            try:
                if sys.platform.startswith('darwin'):
                    subprocess.Popen(['open', folder_path])
                else:
                    subprocess.Popen(['xdg-open', folder_path])
            except Exception as e:
                messagebox.showerror("Error", f"Could not open the folder: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageResizerApp(root)
    root.mainloop()
