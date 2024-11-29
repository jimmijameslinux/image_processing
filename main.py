import cv2
import numpy as np
import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os
import subprocess
import sys
import pkg_resources

# Function to check if the required libraries are installed
def are_requirements_met():
    try:
        with open('requirements.txt', 'r') as req_file:
            required_libraries = req_file.readlines()
            for lib in required_libraries:
                package = lib.strip()
                try:
                    # Check if the package is installed
                    pkg_resources.get_distribution(package)
                except pkg_resources.DistributionNotFound:
                    print(f"'{package}' is not installed.")
                    return False
        return True
    except FileNotFoundError:
        print("'requirements.txt' not found. Skipping installation.")
        return True  # No file to check, so we'll skip the installation step

# Function to install missing libraries
def install_requirements():
    if os.path.exists('requirements.txt'):
        # If libraries are not met, install from the requirements.txt
        if not are_requirements_met():
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            except subprocess.CalledProcessError as e:
                print(f"Error occurred while installing dependencies: {e}")
                sys.exit(1)
        else:
            print("All required libraries are already installed.")

# Install the requirements if needed
install_requirements()



# Function to apply edge detection
def apply_edge_detection(image, method, order):
    if order == "First Order":
        if method == "Sobel":
            # Sobel Edge Detection (First-Order Derivative)
            sobel_x = cv2.Sobel(image, cv2.CV_64F, 1, 0, ksize=3)
            sobel_y = cv2.Sobel(image, cv2.CV_64F, 0, 1, ksize=3)
            return cv2.magnitude(sobel_x, sobel_y)

        elif method == "Prewitt":
            # Prewitt Edge Detection (First-Order Derivative)
            kernel_x = np.array([[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]])  # Horizontal kernel
            kernel_y = np.array([[1, 1, 1], [0, 0, 0], [-1, -1, -1]])  # Vertical kernel
            prewitt_x = cv2.filter2D(image, cv2.CV_64F, kernel_x)
            prewitt_y = cv2.filter2D(image, cv2.CV_64F, kernel_y)
            return cv2.magnitude(prewitt_x, prewitt_y)

    elif order == "Second Order":
        if method == "Laplacian":
            # Laplacian Edge Detection (Second-Order Derivative)
            return cv2.Laplacian(image, cv2.CV_64F)

        elif method == "LoG":
            # Laplacian of Gaussian (LoG) Edge Detection
            blurred_image = cv2.GaussianBlur(image, (5, 5), 0)
            return cv2.Laplacian(blurred_image, cv2.CV_64F)
        
    return image

# Function to convert image to display in CustomTkinter
def cv2_to_tkimage(cv_img):
    cv_img = cv2.convertScaleAbs(cv_img)
    if len(cv_img.shape) == 2:
        image_pil = Image.fromarray(cv_img)
    else:
        color_converted = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        image_pil = Image.fromarray(color_converted)
    return ImageTk.PhotoImage(image_pil)

# Function to open image file dialog and load image
def load_image():
    global original_image
    file_path = filedialog.askopenfilename(title="Select Image", filetypes=[("Image files", "*.jpg;*.jpeg;*.png;*.bmp;*.tiff")])
    if file_path:
        img = cv2.imread(file_path)
        if img is None:
            messagebox.showerror("Error", "Error loading image!")
        else:
            original_image = img
            display_original_image(img)

# Function to display the original image in the CustomTkinter window
def display_original_image(img):
    global canvas_image
    original_tk = cv2_to_tkimage(img)
    canvas_result.create_image(0, 0, anchor=ctk.NW, image=original_tk)
    canvas_result.config(width=img.shape[1], height=img.shape[0])
    canvas_result.image = original_tk

# Function to apply edge detection and display the result
def convert_image():
    if original_image is None:
        messagebox.showerror("Error", "No image loaded!")
        return
    gray_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2GRAY)
    selected_method = method_combobox.get()
    selected_order = order_combobox.get()
    result_image = apply_edge_detection(gray_image, selected_method, selected_order)
    result_tk = cv2_to_tkimage(result_image)
    canvas_result.create_image(0, 0, anchor=ctk.NW, image=result_tk)
    canvas_result.config(width=result_image.shape[1], height=result_image.shape[0])
    canvas_result.image = result_tk

# Set up the main window using CustomTkinter
ctk.set_appearance_mode("System")  # Modes: "System" (default), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (default), "green", "dark-blue"

root = ctk.CTk()
root.title("Edge Detection Application")
root.geometry("1000x700")

original_image = None

# Add controls frame
controls_frame = ctk.CTkFrame(root)
controls_frame.pack(pady=10, padx=10)

load_button = ctk.CTkButton(controls_frame, text="Load Image", command=load_image, width=150)
load_button.grid(row=0, column=0, padx=10, pady=5)

convert_button = ctk.CTkButton(controls_frame, text="Convert", command=convert_image, width=150)
convert_button.grid(row=0, column=1, padx=10, pady=5)

order_label = ctk.CTkLabel(controls_frame, text="Select Order:")
order_label.grid(row=1, column=0, padx=5, pady=5)
order_combobox = ctk.CTkComboBox(controls_frame, values=["First Order", "Second Order"], state="readonly", width=150,command=lambda e: update_methods(e))
order_combobox.set("First Order")
order_combobox.grid(row=1, column=1, padx=5, pady=5)
order_combobox.bind("<<ComboboxSelected>>", lambda e: update_methods(e))
# pickup_frame.canvas.bind('<Button-1>', lambda e: print('with CKT FRAME'))

# Function to update available edge detection methods based on selected order
def update_methods(selected_order):
    selected_order = order_combobox.get()
    # print("update_methods triggered with event:", event)
    if selected_order == "First Order":
        method_combobox.configure(values=["Sobel", "Prewitt"])
        method_combobox.set("Sobel")
    elif selected_order == "Second Order":
        method_combobox.configure(values=["Laplacian", "LoG"])
        method_combobox.set("Laplacian")

method_label = ctk.CTkLabel(controls_frame, text="Select Method:")
method_label.grid(row=2, column=0, padx=5, pady=5)
method_combobox = ctk.CTkComboBox(controls_frame, values=["Sobel", "Prewitt"], state="readonly", width=150)
method_combobox.set("Sobel")
method_combobox.grid(row=2, column=1, padx=5, pady=5)

# Add canvas frame
canvas_frame = ctk.CTkFrame(root)
canvas_frame.pack(pady=10)
canvas_result = ctk.CTkCanvas(canvas_frame, width=600, height=400)
canvas_result.pack()

# Run the CustomTkinter event loop
root.mainloop()