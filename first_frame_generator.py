import cv2

# Path to the video file
video_path = 'AVSS_E2.avi'

# Initialize the video capture object
cap = cv2.VideoCapture(video_path)

# Check if the video opened successfully
if not cap.isOpened():
    print("Error: Could not open video.")
    exit()

# Read the first frame
ret, frame = cap.read()

# Check if the frame was read correctly
if ret:
    # Save the frame as an image file
    cv2.imwrite('first_frame.jpg', frame)
    print("First frame saved as 'first_frame.jpg'")
else:
    print("Error: Could not read the first frame.")

# Release the video capture object
cap.release()
