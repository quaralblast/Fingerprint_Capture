
import tkinter as tki
from tkinter import font
from tkinter import ttk
import cv2
from PIL import Image, ImageTk
import subprocess
#import RPi.GPIO as GPIO
import threading
import datetime
import os
import numpy as np

DATA_FILEPATH = r"C:\Users\LAB-PC\Documents\code\python\Fingerprint\Fingerprint_Data"
LOG_FILEPATH = r"C:\Users\LAB-PC\Documents\code\python\Fingerprint\fingerprint_log.csv"
FILE_EXTENSION = '.png'

VIDEO_RES = (640, 480)
PICTURE_RES = (4645, 3496)
FPS = 15

class MyGUI():
    def __init__(self):
        # Create main window
        self.root = tki.Tk()

        # Set window size and title
        self.root.geometry('1350x720') 
        self.root.title(string='Fingerprint Capture')

        # Fonts
        self.button_font = font.Font(family='Helvetica', size=35, weight='bold')
        self.top_button_font = font.Font(family='Helvetica', size=8)

        # Open Camera (Second argument describes backend)
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW) # cv2.CAP_V4L2 for linux, cv2.CAP_DSHOW for windows testing
        if not self.cap.isOpened():
            print('Could not find Camera.')

        self.preview_running = True # Determines if preview is playing or not

        # Set Camera settings
        self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, VIDEO_RES[0]) 
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, VIDEO_RES[1]) 
        self.cap.set(cv2.CAP_PROP_FPS, FPS)

        ## Top Frame ##
        self.top_frame = tki.Frame(self.root)
        self.top_frame.pack(side='top',anchor='w', padx=20,pady=10)
        
        self.name_label = tki.Label(self.top_frame, text="Name")
        self.name_entry = tki.Entry(self.top_frame, width=20)

        self.name_label.grid(row=0,column=0,sticky='w')
        self.name_entry.grid(row=0,column=1)

        self.id_label = tki.Label(self.top_frame, text='ID')
        self.id_entry = tki.Entry(self.top_frame, width=20)
        self.next_id = tki.Button(self.top_frame,
                                  text='Next Free',
                                  font=self.top_button_font,
                                  command=self.next_free
                                  )

        self.id_label.grid(row=1,column=0,sticky='w')
        self.id_entry.grid(row=1,column=1)
        self.next_id.grid(row=1,column=2)

        self.finger_options = ['','R_Thumb','R_Index','R_Middle','R_Ring','R_Little','L_Thumb','L_Index','L_Middle','L_Ring','L_Little']
        self.finger_label = tki.Label(self.top_frame, text="Finger")
        self.finger_cb = ttk.Combobox(self.top_frame, values=self.finger_options)
        self.finger_next = tki.Button(self.top_frame,
                                      text='Next Finger',
                                      font=self.top_button_font,
                                      command=self.next_finger
                                      )
        
        self.finger_label.grid(row=2,column=0,sticky='w')
        self.finger_cb.grid(row=2,column=1)
        self.finger_next.grid(row=2,column=2)

        ## Middle Frame ##
        self.middle_frame = tki.Frame(self.root)
        self.middle_frame.pack(side='top', pady=10)

        self.camera_frame = tki.Frame(self.middle_frame)
        self.camera_frame.pack(side='left',padx=20)
        self.camera_label = tki.Label(self.camera_frame,text='Camera feed',width=640,height=480)
        self.camera_label.pack()
        
        self.image_frame = tki.Frame(self.middle_frame)
        self.image_frame.pack(side='left',padx=20)
        self.image_label = tki.Label(self.image_frame)
        self.image_label.pack()

        ## Bottom Frame ##
        self.bottom_frame = tki.Frame(self.root)
        self.bottom_frame.pack(side='top',pady=10)

        self.capture_button = tki.Button(self.bottom_frame,
                                         text='Capture',
                                         font=self.button_font,
                                         command=lambda: threading.Thread(target=self.take_photo).start()
                                         )
        self.capture_button.grid(row = 0, column=0,padx=40)

        self.metric_label = tki.Label(self.bottom_frame,font=self.button_font,width=20,anchor='w', text='NFIQ SCORE: --')
        self.metric_label.grid(row=0,column=1,padx=40)

        # Open Camera and turn on LEDs
        self.open_camera()
        # self.toggleLED(1) # Only works on Linux (uses raspberry pi gpio pins)
        
        self.root.protocol('WM_DELETE_WINDOW',self.on_closing)
        tki.mainloop()

    def open_camera(self):

        # Will pause preview
        if not self.preview_running:
            return
        self.cap.set(cv2.CAP_PROP_AUTOFOCUS,0)
        self.cap.set(cv2.CAP_PROP_FOCUS,1023)
        # subprocess.run(['v4l2-ctl', '-d', '/dev/video0', '-c', 'focus_automatic_continuous=0']) # Only works on linux
        # subprocess.run(['v4l2-ctl', '-d', '/dev/video0', '-c', 'focus_absolute=1023']) # Only works on linux
        
        # Read frame
        _, frame = self.cap.read()

        # Process frame to be shown
        opencv_image = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
        captured_image = Image.fromarray(opencv_image)
        photo_image = ImageTk.PhotoImage(image=captured_image)

        # Put it on the label
        self.camera_label.photo_image = photo_image
        self.camera_label.configure(image=photo_image)

        # Repeat after 10 ms
        self.camera_label.after(10, self.open_camera)

    def take_photo(self):
        # Pause Preview
        self.preview_running = False
        
        # Set Camera to 4k to take picture
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, PICTURE_RES[0]) 
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, PICTURE_RES[1]) 
        
        # Take frame (flush 4 keep last)
        for _ in range(5):
            # subprocess.run(['v4l2-ctl', '-d', '/dev/video0', '-c', 'focus_automatic_continuous=0']) # Only works on linux
            # subprocess.run(['v4l2-ctl', '-d', '/dev/video0', '-c', 'focus_absolute=1023']) # Only works on linux
            self.cap.set(cv2.CAP_PROP_AUTOFOCUS,0)
            self.cap.set(cv2.CAP_PROP_FOCUS,1023)
            ret, frame = self.cap.read()

        self.capture_button.configure(text='Processing...')
        # Set Camera to preview resolution
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, VIDEO_RES[0]) 
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, VIDEO_RES[1]) 
        
        # Turn preview back on
        self.preview_running = True
        self.open_camera()
        
        # Preprocess
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = self.process(frame)
        
        name = self.name_entry.get()
        id = str(self.id_entry.get())
        finger = self.finger_cb.get()

        # Show Image on Screen
        image = Image.fromarray(frame)
        image = image.resize((640,480))
        imagetk = ImageTk.PhotoImage(image=image)
        self.image_label.configure(image=imagetk)
        self.image_label.photo_image = imagetk
        self.capture_button.configure(text='Capture')

        # Get and show NFIQ2 Score
        nfiq2_path = "C:\\Program Files\\NFIQ 2\\bin\\nfiq2.exe"
        image_path = os.path.join(DATA_FILEPATH, id, id + '_' + finger + FILE_EXTENSION)

        result = subprocess.run(
            [nfiq2_path, image_path],
            capture_output=True,
            text=True,
        )

        if not 'Error' in result.stdout:
            self.metric_label.configure(text=f'NFIQ2 SCORE: {result.stdout.strip()}')
        else:
            self.metric_label.configure(text='NFIQ2 SCORE: ERROR')

        # Save processed image
        cv2.imwrite(os.path.join(DATA_FILEPATH,id,id+'_'+finger+FILE_EXTENSION),frame)

        # Log Data to CSV
        try:
            with open(LOG_FILEPATH, 'a') as appendfile:
                appendfile.write(f'\n{datetime.datetime.now()},{name},{id},{finger}')
        except FileNotFoundError:
            print('Data Was Not Logged. Could Not Locate Log File.')

    # def toggleLED(self, status):
    #     firstPin , secondPin , thirdPin = 17,27,22

    #     GPIO.setmode(GPIO.BCM)
    #     GPIO.setup(firstPin,GPIO.OUT)
    #     GPIO.setup(secondPin,GPIO.OUT)
    #     GPIO.setup(thirdPin,GPIO.OUT)
        
    #     if status == 1:
    #             GPIO.output(firstPin,GPIO.HIGH)
    #             GPIO.output(secondPin,GPIO.HIGH)
    #             GPIO.output(thirdPin,GPIO.HIGH)
    #     elif status == 0:
    #             GPIO.output(firstPin,GPIO.LOW)
    #             GPIO.output(secondPin,GPIO.LOW)
    #             GPIO.output(thirdPin,GPIO.LOW)

    # Gets the next free ID
    def next_free(self):
        id = 0

        for _, subfolders, __ in os.walk(DATA_FILEPATH):
            if subfolders != []:
                id += 1
        
        self.id_entry.delete(0,tki.END)
        self.id_entry.insert(0,id)

    # Gets the next finger
    def next_finger(self):
        content = self.finger_cb.get()
        index = 0
        for i in self.finger_options:
            if content == i:
                break
            index += 1
        if index == (len(self.finger_options) - 1):
            new_finger = ''
        else:
            new_finger = self.finger_options[index + 1]

        self.finger_cb.delete(0,tki.END)
        self.finger_cb.insert(0,new_finger)
    
    def process(self, inputIMG):
        # Resizing if applicable
        target = inputIMG[575:1845,1465:3065] # 1465:3065,575:1845

        # Grayscale image
        grayscaled = cv2.cvtColor(target,cv2.COLOR_BGR2GRAY)
        
        # Save image for NFIQ2 score
        resized = cv2.resize(grayscaled, (640, 640))
        id = str(self.id_entry.get())
        finger = self.finger_cb.get()
        if not os.path.exists(os.path.join(DATA_FILEPATH,id)): os.makedirs(os.path.join(DATA_FILEPATH,id))
        cv2.imwrite(os.path.join(DATA_FILEPATH,id,id+'_'+finger+FILE_EXTENSION),resized)
        img = Image.open(os.path.join(DATA_FILEPATH,id,id+'_'+finger+FILE_EXTENSION))
        img.save(os.path.join(DATA_FILEPATH,id,id+'_'+finger+FILE_EXTENSION), dpi=(500, 500))

        # Gaussian Blur to remove noise
        grayscaled = cv2.GaussianBlur(grayscaled,(3,3),1)

        # Erosion followed by dilation to further remove noise
        kernel = np.ones((2,2),np.uint8)
        opening = cv2.morphologyEx(grayscaled, cv2.MORPH_OPEN, kernel)
        
        # Contrast Limited Adaptive Histogram Equalization - sharpens image
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        cl1 = clahe.apply(opening)
    
        # Invert Colors
        inverted = cv2.bitwise_not(cl1)
        
        return inverted
    
    def on_closing(self):
        #self.toggleLED(0)
        self.root.destroy()

if __name__ == '__main__':
    gui = MyGUI()
    

