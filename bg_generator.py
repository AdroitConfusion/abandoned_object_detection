import cv2
from os import path

# Path to the video file
video_folder = 'examples/example 3'
video_path = path.join(video_folder, 'video.avi')
bg_path = path.join(video_folder, 'bg.png')

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
    cv2.imwrite(bg_path, frame)
    print("First frame saved as 'bg.png'")
else:
    print("Error: Could not read the first frame.")

# Release the video capture object
cap.release()
