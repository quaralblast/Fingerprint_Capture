
import tkinter as tki
from tkinter import font
from tkinter import ttk
from tkinter import messagebox
import cv2
from pygrabber.dshow_graph import FilterGraph
from PIL import Image, ImageTk
import subprocess
import threading
import queue
import datetime
import time
import os
import numpy as np
from rembg import remove
from rembg.bg import new_session
import sys


DATA_FILEPATH = os.path.join(os.environ["USERPROFILE"], "Documents", "FingerprintCapture", "Fingerprint_Data")
LOG_FILEPATH = os.path.join(os.environ["USERPROFILE"], "Documents", "FingerprintCapture", "fingerprint_log.csv") # date,name,id,finger '
FILE_EXTENSION = '.png'

VIDEO_RES = (640, 480)
PICTURE_RES = (4645, 3496)
FPS = 10

'''
dependencies: rembg[cpu] numpy opencv-python pillow
'''

class MyGUI():
    def __init__(self):
        # Create main window
        self.root = tki.Tk()

        # Set window size and title
        self.root.geometry('1350x770') 
        self.root.title(string='Fingerprint Capture')

        # Fonts
        self.button_font = font.Font(family='Helvetica', size=35, weight='bold')
        self.top_button_font = font.Font(family='Helvetica', size=8)

        # Create a thread for capturing images and changing camera
        self.worker_running = True
        self.task_queue = queue.Queue()
        self.worker_thread = threading.Thread(target=self.worker, daemon=True)
        self.worker_thread.start()

        # Creates a list of Camera names
        self.graph = FilterGraph()
        self.cameras = self.graph.get_input_devices()
        
        # Open Camera (Second argument describes backend)
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW) # cv2.CAP_V4L2 for linux, cv2.CAP_DSHOW for windows testing
        if not self.cap.isOpened():
            print('Could not find Camera.')
        else:
            self.current_camera = 0

        self.preview_running = True # Determines if preview is playing or not
        self.duplicate = False

        # Set Camera settings
        self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, PICTURE_RES[0]) 
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, PICTURE_RES[1]) 
        self.cap.set(cv2.CAP_PROP_FPS, FPS)
        self.cap.set(cv2.CAP_PROP_AUTOFOCUS,0)
        self.cap.set(cv2.CAP_PROP_FOCUS,1023)

        # Start rembg session
        self.initialize_rembg()

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

        self.camera_options_label = tki.Label(self.top_frame,text="Set Camera")
        self.camera_options_cb = ttk.Combobox(self.top_frame, values=self.cameras)
        self.connect_button = tki.Button(self.top_frame,
                                         text='Connect',
                                         font=self.top_button_font,
                                         command=lambda: self.task_queue.put('set_camera')
                                         )
        
        self.camera_options_label.grid(row=3,column=0,sticky='w')
        self.camera_options_cb.grid(row=3,column=1)
        self.connect_button.grid(row=3,column=2)

        self.duplicate_var = tki.BooleanVar()
        self.duplicate_checkbox = tki.Checkbutton(self.top_frame, text="Allow duplicate finger pictures",variable=self.duplicate_var,onvalue=1,offvalue=0)
        self.duplicate_checkbox.grid(row=4,column=0)


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
                                         command=lambda: self.task_queue.put('take_photo')
                                         )
        self.capture_button.grid(row = 0, column=0,padx=40,sticky='w')

        self.metric_label = tki.Label(self.bottom_frame,font=self.button_font,text='')
        self.metric_label.grid(row=0,column=1,padx=40,pady=20)

        # Open Camera and turn on LEDs
        self.open_camera()
        
        self.root.protocol('WM_DELETE_WINDOW',self.on_closing)
        self.root.mainloop()

    def open_camera(self):

        # Will pause preview
        if not self.preview_running:
            return
        
        if self.cap.get(cv2.CAP_PROP_FOCUS) != 1023:
            self.cap.set(cv2.CAP_PROP_FOCUS, 1023)

        # Read frame
        _, frame = self.cap.read()

        # Process frame to be shown
        opencv_image = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
        captured_image = Image.fromarray(opencv_image)
        photo_image = ImageTk.PhotoImage(image=captured_image)

        small_image = captured_image.copy()

        small_image.thumbnail(VIDEO_RES, Image.Resampling.LANCZOS)
        photo_image = ImageTk.PhotoImage(small_image)
        # cv2.imshow("balls", np.array(small_image))
        # cv2.waitKey(0)

        # Put it on the label
        self.camera_label.photo_image = photo_image
        self.camera_label.configure(image=photo_image)

        # Repeat after 10 ms
        self.camera_label.after(10, self.open_camera)

    def take_photo(self):
        self.capture_button.configure(command=self.do_nothing)


        # Pause Preview
        photo_s = time.perf_counter()
        self.preview_running = False
        
        
        # Take frame (flush 4 keep last)
        for _ in range(5):
            self.cap.set(cv2.CAP_PROP_AUTOFOCUS,0)
            self.cap.set(cv2.CAP_PROP_FOCUS,1023)
            ret, frame = self.cap.read()
        photo_e = time.perf_counter()
        print(f'photo capture: {photo_e - photo_s}')
        
        self.capture_button.configure(text='Processing...')
        
        # Turn preview back on
        self.preview_running = True
        self.open_camera()


        name = self.name_entry.get()
        id = str(self.id_entry.get())
        finger = self.finger_cb.get()

        os.makedirs(os.path.join(DATA_FILEPATH,id), exist_ok=True)
        os.makedirs(os.path.join(DATA_FILEPATH,id,'Real'),exist_ok=True)
        os.makedirs(os.path.join(DATA_FILEPATH,id,'NFIQ'),exist_ok=True)
        os.makedirs(os.path.join(DATA_FILEPATH,id,'Raw'),exist_ok=True)

        if self.duplicate_var.get():
            self.duplicate_number = 0
            for files in os.listdir(os.path.join(DATA_FILEPATH, id,'Real')):

                if os.path.join(DATA_FILEPATH,id,'Real',id+'_'+finger) in os.path.join(DATA_FILEPATH, id,'Real', files):
                    self.duplicate_number += 1
                    self.duplicate = True
            self.duplicate_number = str(self.duplicate_number)      

        # Preprocess
        frame = self.process(frame)
        

        # Show Image on Screen
        image = Image.fromarray(frame)
        image = image.resize((640,480))
        imagetk = ImageTk.PhotoImage(image=image)
        self.image_label.configure(image=imagetk)
        self.image_label.photo_image = imagetk
        self.capture_button.configure(text='Capture')
        
        # Get and show NFIQ2 Score
        if os.path.exists("C:\\Program Files\\NFIQ 2\\bin\\nfiq2.exe"):
            nfiq2_path = "C:\\Program Files\\NFIQ 2\\bin\\nfiq2.exe"
            if not self.duplicate:
                image_path = os.path.join(DATA_FILEPATH, id,'Real', id + '_' + finger + FILE_EXTENSION)
            else:
                image_path = os.path.join(DATA_FILEPATH, id,'Real', id + '_' + finger+'_'+self.duplicate_number + FILE_EXTENSION)

            result = subprocess.run(
                [nfiq2_path, image_path],
                input='y',
                capture_output=True,
                text=True,
            )

            if not 'Error' in result.stdout:
                nfiq2_score = result.stdout.strip()
                self.root.after(0, lambda: self.metric_label.configure(text=f'NFIQ2 SCORE: {nfiq2_score[-2:]}'))
            else:
                nfiq2_score = 'na'
                self.root.after(0,lambda: self.metric_label.configure(text='NFIQ2 SCORE: ERROR'))
        else:
            nfiq2_score = 'na'
            self.root.after(0,lambda: self.metric_label.configure(text='NFIQ2 SCORE: NOT FOUND'))
        

        # Save processed image
        if not self.duplicate:
            cv2.imwrite(os.path.join(DATA_FILEPATH,id,'Real',id+'_'+finger+FILE_EXTENSION),frame)
        else:
            cv2.imwrite(os.path.join(DATA_FILEPATH,id,'Real',id+'_'+finger+'_'+self.duplicate_number+FILE_EXTENSION),frame)

        # Log Data to CSV
        if os.path.exists(LOG_FILEPATH):
            logfile_exists = True
        else:
            logfile_exists = False

        with open(LOG_FILEPATH, 'a') as csvfile:
            if not logfile_exists:
                csvfile.write(f'date,name,id,finger,nfiq')

            
            csvfile.write(f'\n{datetime.datetime.now()},{name},{id},{finger},{nfiq2_score[-2:].strip()}')
        
        self.duplicate = False
        self.root.after(0,self.capture_button.configure(command=lambda: threading.Thread(target=self.take_photo).start()))

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
        total_s = time.perf_counter()
        id = str(self.id_entry.get())
        finger = self.finger_cb.get()

        ## SAVES RAW IMAGE ##
        if not self.duplicate:
            cv2.imwrite(os.path.join(DATA_FILEPATH,id,'Raw',id+'_'+finger+'_Raw'+FILE_EXTENSION),inputIMG)
        else:
            cv2.imwrite(os.path.join(DATA_FILEPATH,id,'Raw',id+'_'+finger+'_Raw'+'_'+self.duplicate_number+FILE_EXTENSION),inputIMG)

        width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

        # Crops to fingerprint area
        target = inputIMG[round(height * (25/152)) : round(height * (1845/3496)) , 
                          round(width * (1465/4645)) : round(width * (3065/4656))] # 1465:3065,575:1845
        
        # Remove Background
        rembg_s = time.perf_counter()
        try:
            bg_removed = remove(target, session=self.rembg_session)
        except Exception as e:
            messagebox.showinfo("Remove Background Failed", f"Remove Background Failed: {e}")
            bg_removed = target
        rembg_e = time.perf_counter()
        print(f'rembg: {rembg_e - rembg_s}')
        
        # Grayscale image
        gray_s =  time.perf_counter()
        grayscaled = cv2.cvtColor(bg_removed,cv2.COLOR_RGB2GRAY)
        gray_e = time.perf_counter()
        print(f'grayscale: {gray_e - gray_s}')

        # Gaussian Blur to remove noise
        blur_s = time.perf_counter()
        grayscaled = cv2.GaussianBlur(grayscaled,(3,3),1)
        blur_e = time.perf_counter()
        print(f'Blur: {blur_e - blur_s}')
        
        # Erosion followed by dilation to further remove noise
        # op_s = time.perf_counter()
        # kernel = np.ones((2,2),np.uint8)
        # opening = cv2.morphologyEx(grayscaled, cv2.MORPH_OPEN, kernel)
        # op_e = time.perf_counter()
        # print(f'Opening: {op_e - op_s}')
        
        # Contrast Limited Adaptive Histogram Equalization - sharpens image
        clahe_s = time.perf_counter()
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(15,15))
        cl1 = clahe.apply(grayscaled)
        clahe_e = time.perf_counter()
        print(f'Clahe: {clahe_e - clahe_s}')
        
        # Threshold to remove grey pixels in-between ridges
        thresh_s = time.perf_counter()
        _, threshold = cv2.threshold(cl1, thresh=100, maxval=255, type=cv2.THRESH_TOZERO) # 100
        thresh_e = time.perf_counter()
        print(f'Threshold: {thresh_e - thresh_s}')

        #Invert Colors
        invert_s = time.perf_counter()
        inverted = cv2.bitwise_not(threshold)
        invert_e = time.perf_counter()
        print(f'Invert: {invert_e - invert_s}')
    
    
        #Save image for NFIQ2 score
        nfiq_s = time.perf_counter()
        resized = cv2.resize(inverted, (640, 640))
        

        if not self.duplicate:
            cv2.imwrite(os.path.join(DATA_FILEPATH,id,'Real',id+'_'+finger+FILE_EXTENSION),resized)
        else:
            cv2.imwrite(os.path.join(DATA_FILEPATH,id,'Real',id+'_'+finger+'_'+self.duplicate_number+FILE_EXTENSION),resized)

        if not self.duplicate:
            cv2.imwrite(os.path.join(DATA_FILEPATH,id,'NFIQ',id+'_'+finger + '_NFIQ' +FILE_EXTENSION),resized)
        else:
            cv2.imwrite(os.path.join(DATA_FILEPATH,id,'NFIQ',id+'_'+finger + '_NFIQ' +'_'+self.duplicate_number+FILE_EXTENSION),resized)

        if not self.duplicate:
            img = Image.open(os.path.join(DATA_FILEPATH,id,'Real',id+'_'+finger+FILE_EXTENSION))
        else:
            img = Image.open(os.path.join(DATA_FILEPATH,id,'Real',id+'_'+finger+'_'+self.duplicate_number+FILE_EXTENSION))
        
        if img.mode != 'RGB':
            img = img.convert('RGB')

        if not self.duplicate:
            img.save(os.path.join(DATA_FILEPATH,id,'Real',id+'_'+finger+FILE_EXTENSION), dpi=(500, 500))
        else:
            img.save(os.path.join(DATA_FILEPATH,id,'Real',id+'_'+finger+'_'+self.duplicate_number+FILE_EXTENSION), dpi=(500, 500))
        nfiq_e = time.perf_counter()
        print(f'nfiq: {nfiq_e - nfiq_s}')
        
        total_e = time.perf_counter()
        print(f'Total Time: {total_e - total_s}')
        return inverted
    
    def set_camera(self):
        camera = self.camera_options_cb.get()
        for i in range(len(self.cameras)):
            if self.cameras[i] == camera:
                camera_index = i

        if camera_index == self.current_camera:
            return
        
        if 'Virtual' in self.cameras[camera_index]:
            messagebox.showinfo("Invalid Camera", "Please select a valid Camera.")
            return
        
        self.preview_running = False
        self.cap.release()
        self.cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
        
        if not self.cap.isOpened():
            messagebox.showinfo("Camera not found", "The selected Camera has not been found.")
        else:
            self.current_camera = camera_index
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, PICTURE_RES[1]) 
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, PICTURE_RES[0]) 
        
        self.preview_running = True
        self.open_camera()
    
    def worker(self):
        while self.worker_running:
            try:
                task = self.task_queue.get(timeout=0.2)
            except queue.Empty:
                continue
            if task == 'take_photo':
                self.take_photo()
            elif task == 'set_camera':
                self.set_camera()
            self.task_queue.task_done()
    
    def initialize_rembg(self):
        if sys.stderr is None:
            sys.stderr = open(os.devnull, 'w')

        # Ensure rembg uses the bundled .u2net directory for the model
        if hasattr(sys, "_MEIPASS"):
            u2net_path = os.path.join(sys._MEIPASS, ".u2net")
        else:
            u2net_path = os.path.join(os.getcwd(), ".u2net")

        os.environ["U2NET_HOME"] = u2net_path

        self.rembg_session = new_session("u2netp")

    def do_nothing(self):
        pass

    def on_closing(self):

        # Release Camera
        if hasattr(self, 'cap'):
            self.cap.release()

        # Release worker thread
        self.worker_running = False
        self.worker_thread.join()

        # Close window    
        self.root.destroy()
        sys.exit()


if __name__ == '__main__':
    os.makedirs(DATA_FILEPATH, exist_ok=True)

    gui = MyGUI()

    
    
    

