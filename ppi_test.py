import cv2

points = []

def click_event(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        points.append((x, y))
        if len(points) == 2:
            cv2.line(img, points[0], points[1], (0, 255, 0), 2)
            pixel_dist = ((points[0][0] - points[1][0])**2 + (points[0][1] - points[1][1])**2)**0.5
            print(f"Pixel distance: {pixel_dist:.2f} px")
            # Optional: calculate PPI
            inches = float(input("Enter real-world length in inches between the two points: "))
            ppi = pixel_dist / inches
            print(f"Estimated PPI: {ppi:.2f}")
            cv2.imshow("Image", img)

# Load image
img = cv2.imread(r"C:\Users\LAB-PC\Documents\FingerprintCapture\Fingerprint_Data\Raw\__Raw.png")
cv2.imshow("Image", img)
cv2.setMouseCallback("Image", click_event)
cv2.waitKey(0)
cv2.destroyAllWindows()
