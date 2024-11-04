import os
import sys
import numpy as np
from tkinter import Tk, filedialog, Label, Button, Entry, IntVar, StringVar, messagebox
from tkinter.ttk import Progressbar
from PIL import Image

def select_file():
    file_path = filedialog.askopenfilename(
        filetypes=[("Image files", "*.png *.jpg *.bmp *.gif")])
    if file_path:
        img = Image.open(file_path)
        img_width, img_height = img.size
        filepath_var.set(file_path)
        dimensions_var.set(f"Dimensions: {img_width}x{img_height}")
        img.close()
        print(f"Selected file: {file_path} with dimensions {img_width}x{img_height}")

def detect_tile_size(image_array, axis):
    # Collapse the image array along the specified axis by taking the mean
    projection = np.mean(image_array, axis=axis)
    
    # Perform Fourier Transform
    f_transform = np.fft.rfft(projection)
    
    # Get the magnitudes of the frequencies
    magnitudes = np.abs(f_transform)
    
    # Identify the peak (ignoring the zero frequency component)
    peak_index = np.argmax(magnitudes[1:]) + 1
    
    # Convert the peak frequency into a wavelength
    tile_size = len(projection) / peak_index
    return tile_size

def auto_detect_tiles():
    file_path = filepath_var.get()
    if not file_path:
        messagebox.showerror("Error", "No file selected!")
        return

    try:
        img = Image.open(file_path).convert('RGBA')
        img_width, img_height = img.size

        # Convert the image to a NumPy array and extract the alpha channel
        image_array = np.array(img)[:, :, 3]  # Use alpha channel for transparency

        # Detect tile sizes horizontally and vertically
        x_tile_size = detect_tile_size(image_array, axis=0)  # Collapse rows
        y_tile_size = detect_tile_size(image_array, axis=1)  # Collapse columns

        x_tiles = round(img_width / x_tile_size)
        y_tiles = round(img_height / y_tile_size)
        
        x_tiles_var.set(x_tiles)
        y_tiles_var.set(y_tiles)

        total_images_var.set(f"Total Images: {x_tiles * y_tiles}")
        dimensions_var.set(f"Detected Tiles: {x_tiles} x {y_tiles}")
        img.close()
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred during auto-detection: {e}")

def process_sprites():
    file_path = filepath_var.get()
    if not file_path:
        messagebox.showerror("Error", "No file selected!")
        return

    x_tiles = x_tiles_var.get()
    y_tiles = y_tiles_var.get()
    
    if x_tiles <= 0 or y_tiles <= 0:
        messagebox.showerror("Error", "Number of tiles must be greater than zero!")
        return

    try:
        img = Image.open(file_path)
        img_width, img_height = img.size

        print(f"Sliced Image with dimensions {img_width}x{img_height}")
        print(f"Tiles: {x_tiles}x{y_tiles}")

        # Calculate tile dimensions
        tile_width = img_width // x_tiles
        tile_height = img_height // y_tiles

        base_name = os.path.basename(file_path)
        dir_name = os.path.dirname(file_path)
        name_part = os.path.splitext(base_name)[0]
        dest_folder = os.path.join(dir_name, f"{name_part}_XTiles{x_tiles}YTiles{y_tiles}_TotalImages{x_tiles*y_tiles}")

        if not os.path.exists(dest_folder):
            os.mkdir(dest_folder)

        total_images = x_tiles * y_tiles

        for y in range(y_tiles):
            for x in range(x_tiles):
                left = x * tile_width
                upper = y * tile_height
                right = left + tile_width
                lower = upper + tile_height
                
                sprite = img.crop((left, upper, right, lower))
                sprite_filename = f"{name_part}_{x}_{y}.png"
                sprite.save(os.path.join(dest_folder, sprite_filename))
                
                progress_bar["value"] = ((y * x_tiles) + x + 1) / total_images * 100
                root.update_idletasks()

        messagebox.showinfo("Success", f"Sprites have been successfully extracted and saved in {dest_folder}.")
        
        if sys.platform.startswith('darwin'):
            os.system(f'open "{dest_folder}"')
        elif os.name == 'nt':
            os.startfile(dest_folder)
        elif os.name == 'posix':
            os.system(f'xdg-open "{dest_folder}"')
        
        img.close()
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

root = Tk()
root.title("Sprite Sheet Extractor")

filepath_var = StringVar()
dimensions_var = StringVar()
total_images_var = StringVar()
x_tiles_var = IntVar()
y_tiles_var = IntVar()

Label(root, text="Selected File:").grid(row=0, column=0)
Label(root, textvariable=filepath_var).grid(row=0, column=1)

Button(root, text="Select File", command=select_file).grid(row=1, column=0, columnspan=2)

Label(root, textvariable=dimensions_var).grid(row=2, column=0, columnspan=2)

Button(root, text="Auto-Detect Tiles", command=auto_detect_tiles).grid(row=3, column=0, columnspan=2)

Label(root, text="X Tiles:").grid(row=4, column=0)
Entry(root, textvariable=x_tiles_var).grid(row=4, column=1)

Label(root, text="Y Tiles:").grid(row=5, column=0)
Entry(root, textvariable=y_tiles_var).grid(row=5, column=1)

Label(root, textvariable=total_images_var).grid(row=6, column=0, columnspan=2)

progress_bar = Progressbar(root, orient="horizontal", mode="determinate")
progress_bar.grid(row=7, column=0, columnspan=2, sticky='ew')

Button(root, text="Process", command=process_sprites).grid(row=8, column=0, columnspan=2)

print("Starting the application...")
root.mainloop()