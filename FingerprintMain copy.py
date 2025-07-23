import cv2
from rembg import remove 
from rembg.bg import new_session
from time import sleep
import numpy as np
import os
from pynq_dpu import DpuOverlay
from SiameseHelper import *
overlay = DpuOverlay("dpu.bit")
FILE_PATH = "enrolled_fingerprints.json"

def process_image(inputImg,REMBG_session):
    # clahe = cv2.createCLAHE(clipLimit=2.0,tileGridSize=(8,8))
    # #! Opens image and crop + resize
    # targetImage = inputImg[1465:3065,575,1845] # 0:1663,480:2780
    # targetImage = cv2.resize(targetImage,(500,500))
    
    # #! Removing the background from the given Image 
    # targetImage = remove(targetImage,session=REMBG_session) 
    
    # #! Grayscale the fucker
    # GrayImage = cv2.cvtColor(targetImage, cv2.COLOR_BGR2GRAY)

    # #! Bitwise not to flip colors
    # resized_image = cv2.bitwise_not(GrayImage)
    # img = cv2.GaussianBlur(resized_image,(3,3),1)
    # Final = cv2.adaptiveThreshold(img,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,\
    #         cv2.THRESH_BINARY,17,1)
    # kernel = np.ones((1, 1), np.uint8)
    # dilated_image = cv2.dilate(Final, kernel, iterations=2)
    # final_eroded_image = cv2.erode(dilated_image, kernel, iterations=2)

    target = inputImg[1465:3065,575,1845]
    target = cv2.resize(target,(800,1000))

    # Grayscale image
    grayscaled = cv2.cvtColor(target,cv2.COLOR_BGR2GRAY)
   
    # Gaussian Blur to remove noise
    grayscaled = cv2.GaussianBlur(grayscaled,(3,3),1)

    # Erosion followed by dilation to further remove noise
    kernel = np.ones((5,5),np.uint8)
    opening = cv2.morphologyEx(grayscaled, cv2.MORPH_OPEN, kernel)
    
    # Contrast Limited Adaptive Histogram Equalization - sharpens image
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    cl1 = clahe.apply(opening)
  
    # Invert Colors
    inverted = cv2.bitwise_not(cl1)
  
    return inverted


def CaptureFingerPrint():
    # Main asyncio loop
    # Uses the last index of cameras, usually means the only camera connected
    clear()
    cap = cv2.VideoCapture(-1,cv2.CAP_V4L2)
    print(f"Is webcam open: {cap.isOpened()}")
    if not cap.isOpened():
        while True:
            clear()
            print("Retrying opening camera")
            cap.release()
            sleep(2)
            cap = cv2.VideoCapture(-1,cv2.CAP_V4L2)
            if cap.isOpened():
                break
            else:
                pass
        
    '''
    Setting the camera's resolution, FPS, ISO speed, Exposure, WhiteBalance
    '''
    
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 4645) # 3264
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 3496) # 2448
    cap.set(cv2.CAP_PROP_FPS, 15)
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    print(f"Current FPS: {fps}")
    cap.set(cv2.CAP_PROP_ISO_SPEED, 800)
    
    cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0) # manual mode
    cap.set(cv2.CAP_PROP_EXPOSURE,0)
    
    cap.set(cv2.CAP_PROP_AUTO_WB,0)  #Manual mode
    cap.set(cv2.CAP_PROP_WB_TEMPERATURE, 0)
    
    print("Settings Complete")
    width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

    print(f"Current resolution: {int(width)} x {int(height)}")
    #list_camera_resolutions(cap) #Shows current resolution
    print("Camera Ready")
    sleep(1)
    
    my_session = new_session("u2netp")
    
    FP_THRESHOLD = 0
    edge_count = 0
    try:
        while True:
            clear()
            print("Ready for next fingerprint",edge_count)
            for _ in range(5): #Flushing the buffer and discards 5 frames
                ret, frame = cap.read()
            if frame is not None and frame.size != 0:
                blurred = cv2.GaussianBlur(frame[0:1636,480:2780], (3, 3), 1)
                edges = cv2.Canny(blurred, 0, 150)
                edge_count = cv2.countNonZero(edges)
                print("Ready for next fingerprint",edge_count)
            
                if edge_count > FP_THRESHOLD:
                    clear()
                    print("Hold for 2 seconds")
                    sleep(1)
                    for _ in range(5): #Flushing the buffer and discards 5 frames
                        ret, frame = cap.read()
                    print("Processing! FingerOff")
                    break

        processed_img = process_image(frame,my_session)
        print("Done Processing")
        
        #! Debugging
        cv2.imwrite(f"./Processed_Out.jpg", processed_img)
        cv2.imwrite(f"./Processed_Raw.jpg", frame)
    except KeyboardInterrupt:
        print("KB intr, Capture terminated and cameras released")
    
    except Exception as e:
        print(f"Error Occured: {e}")
             
    print("Script done, Terminating Cameras")
    cap.release()
    
    overlay.load_model("feature_extractor_20c.xmodel")

    dpu = overlay.runner

    inputTensors = dpu.get_input_tensors()
    outputTensors = dpu.get_output_tensors()

    input_dim = tuple(inputTensors[0].dims)
    output_dim = tuple(outputTensors[0].dims)

    input_data = [np.empty(input_dim, dtype=np.float32, order='C')]
    output_data = [np.empty(output_dim, dtype=np.float32, order='C')]
    
    raw_img = cv2.resize(processed_img, (122, 122))

    raw_img = raw_img.reshape(1, 122, 122, 1).astype('float32')
    raw_img /= 255.0
    job_id = dpu.execute_async(raw_img, output_data)
    dpu.wait(job_id)

    vector_a = output_data[0]
    flat_vector = np.array(vector_a).flatten()
    #print(flat_vector)
    cap.release()
    return flat_vector

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')


if __name__ == "__main__":
    try:
        while True:
            clear()
            userInput = input(f"Enter Operational Mode: \n (1) Fingerprint Enrollment Mode \n (2) Fingerprint Matching Mode \n (3) Fingerprint Termination Mode \n Input: ")
            clear()
            if userInput == '1': #ENROLL
                flat_vector = CaptureFingerPrint()
                input("Press Enter to proceed to step 2...")
                print("Capturing Same Fingerprint Again")
                flat_vector2 = CaptureFingerPrint()
                if calculate_distance(flat_vector,flat_vector2) <= 8.0:
                    #! Enrollment Snippet   
                    save_feature_vector(flat_vector, FILE_PATH)
                else:
                    print("Fingerprint does not match")
                input("Press Enter to restart...")  
                    
            elif userInput == '2': #Verify
                matched = False
                flat_vector = CaptureFingerPrint()
                #! Verification snippet
                results = compare_feature_vector(flat_vector, FILE_PATH)
                for label, score in results.items():
                    print(f"Input vs '{label}': Distance Score = {score}")
                    if score <= 7.0:
                        matched = True
                        break
                print("Fingerprint Matched!!!") if matched else print("No Fingerprint Match...")
                input("Press Enter to go back...")
                    
            elif userInput == '3': #Delete
                matched = False
                flat_vector = CaptureFingerPrint()
                results = compare_feature_vector(flat_vector, FILE_PATH)
                for label, score in results.items():
                    print(f"Input vs '{label}': Distance Score = {score}")
                    if score <= 7.0:
                        matched = True
                        print("Fingerprint Matched in Database")
                        input("Press Enter to proceed to step 2..")
                        clear()
                        break
                if matched:
                    print("Capture Same Fingerprint Again to confirm termination")
                    flat_vector2 = CaptureFingerPrint()
                    if calculate_distance(flat_vector,flat_vector2) <= 8.0:
                        #! Termination Snippet   
                        terminate_feature_vector(label, FILE_PATH)
                        input("Press Enter to restart...")
                        clear()
                    else:
                        print("Fingerprint does not match")
                        input("Press Enter to restart...")
                        clear()
                else:
                    print("Fingerprint not detected in database")
                    input("Press Enter to restart...")
                    clear()
            else:
                clear()
                pass
    except KeyboardInterrupt:
        print("Detected Keyboard interrupt, Terminating Program")