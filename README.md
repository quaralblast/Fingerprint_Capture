Fingerprint Capture - a GUI software built for simple fingerprint data collection. 
To download, go to releases and select Fingerprint_Capture_Setup.exe to download. This application is only supported for windows at the moment.



How to use:
A camera must be connected for the app to open. If the app opens with the wrong camera, go to the camera dropdown, 
select the appropriate camera and click connect.

Fill out the fields on the top left. The name category is optional but ID and finger are mandantory. If you are collecting data 
for a new person, select next free. Only in the event that you are collecting for a person who's id already exists should you type 
the id in the entry field.

Select a finger to capture from the dropdown or select next finger to select the finger for capture. If you would like to take multiple 
pictures with the same id and finger, you must select the "allow duplicate photos" checkbox

A live feed of the camera is always shown on the left of the screen. To capture a photo press the 'capture' button. After the picture has been
captured and process, it will save to your computer and appear on the righthand side of the screen. The NFIQ2 score will also appear below the image.
To retake, simply press capture again.

The images are saved in Documents in a folder called 'FingerprintCapture'. Each ID is given its own folder, and within each ID folder are 3 more folders-
real, raw, and NFIQ. The raw folder contains the raw image taken by the scanner. The real folder contains the image after preprocessing (the one shown on the
righthand side of the screen). The NFIQ folder contains the image that was submitted to NFIQ2 for quality assurance. Those images are set to 500ppi as this is  
required by NFIQ. 

The source code can be found in the 'Fingerprint_application_win.pyw' file.
