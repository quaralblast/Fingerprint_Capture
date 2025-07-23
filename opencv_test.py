# Python program to open the
# camera in Tkinter
# Import the libraries,
# tkinter, cv2, Image and ImageTk

from tkinter import *
import cv2
from PIL import Image, ImageTk

# Define a video capture object
vid = cv2.VideoCapture(0)

# Declare the width and height in variables
width, height = 800, 600

# Set the width and height
vid.set(cv2.CAP_PROP_FRAME_WIDTH, width)
vid.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

# Create a GUI app
app = Tk()

# Bind the app with Escape keyboard to
# quit app whenever pressed
app.bind('<Escape>', lambda e: app.quit())

# Create a label and display it on app
label_widget = Label(app)
label_widget.pack()

# Create a function to open camera and
# display it in the label_widget on app


def open_camera():

    # Capture the video frame by frame
    _, frame = vid.read()

    # Convert image from one color space to other
    opencv_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)

    # Capture the latest frame and transform to image
    captured_image = Image.fromarray(opencv_image)

    # Convert captured image to photoimage
    photo_image = ImageTk.PhotoImage(image=captured_image)

    # Displaying photoimage in the label
    label_widget.photo_image = photo_image

    # Configure image in the label
    label_widget.configure(image=photo_image)

    # Repeat the same process after every 10 seconds
    label_widget.after(10, open_camera)


# Create a button to open the camera in GUI app
# button1 = Button(app, text="Open Camera", command=open_camera)
# button1.pack()
open_camera()

# Create an infinite loop for displaying app on screen
app.mainloop()

import tkinter as tk
from tkinter import ttk
import cv2
import pyudev


def get_real_cameras():
    context = pyudev.Context()
    cameras = []

    for device in context.list_devices(subsystem='video4linux'):
        name = device.get('ID_V4L_PRODUCT')
        devnode = device.device_node
        if name and devnode and 'posbe' not in name.lower() and 'gevc' not in name.lower():
            cameras.append((name, devnode))
    return cameras


class CameraApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Camera Selector")

        self.cameras = get_real_cameras()
        self.device_map = {name: devnode for name, devnode in self.cameras}

        self.combo = ttk.Combobox(root, values=list(self.device_map.keys()))
        self.combo.pack(pady=10)

        self.button = ttk.Button(root, text="Connect", command=self.connect_camera)
        self.button.pack(pady=10)

        self.cap = None

    def connect_camera(self):
        selected_name = self.combo.get()
        if not selected_name:
            print("No camera selected.")
            return
        device = self.device_map[selected_name]
        self.cap = cv2.VideoCapture(device)

        if not self.cap.isOpened():
            print(f"Failed to open {device}")
            return

        print(f"Connected to {device}")
        self.show_frame()

    def show_frame(self):
        ret, frame = self.cap.read()
        if ret:
            cv2.imshow("Camera Feed", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            self.cap.release()
            cv2.destroyAllWindows()
            return
        self.root.after(10, self.show_frame)


root = tk.Tk()
app = CameraApp(root)
root.mainloop()
