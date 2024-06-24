import cv2
import numpy as np

# Initialize video capture
cap = cv2.VideoCapture('video1.avi')

# Initialize a list to store tracked objects
tracked_objects = []

# Define a simple function to calculate distance between points
def distance(pt1, pt2):
    return ((pt1[0] - pt2[0]) ** 2 + (pt1[1] - pt2[1]) ** 2) ** 0.5

# Define a threshold for object disappearance
disappearance_threshold = 30

# Read the first frame
ret, prev_frame = cap.read()
if not ret:
    raise Exception("Failed to read video")

# Convert the first frame to grayscale
prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Convert the current frame to grayscale
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Apply Gaussian blur to reduce noise
    blurred_frame = cv2.GaussianBlur(gray_frame, (5, 5), 0)

    # Compute the absolute difference between the current frame and the previous frame
    frame_diff = cv2.absdiff(prev_gray, blurred_frame)

    # Apply a binary threshold to get the foreground mask
    _, fgmask = cv2.threshold(frame_diff, 25, 255, cv2.THRESH_BINARY)

    # Apply morphological operations to remove noise and fill gaps
    kernel = np.ones((5, 5), np.uint8)
    fgmask = cv2.morphologyEx(fgmask, cv2.MORPH_CLOSE, kernel)
    fgmask = cv2.morphologyEx(fgmask, cv2.MORPH_OPEN, kernel)

    # Find contours in the mask
    contours, _ = cv2.findContours(fgmask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Copy frames for display purposes
    preprocessed_frame = cv2.cvtColor(fgmask, cv2.COLOR_GRAY2BGR)
    contour_frame = frame.copy()

    # Mark all objects as not updated
    for obj in tracked_objects:
        obj['updated'] = False

    for contour in contours:
        if cv2.contourArea(contour) < 500:
            continue

        # Get bounding box for the contour
        x, y, w, h = cv2.boundingRect(contour)

        # Track the object
        object_center = (x + w // 2, y + h // 2)
        matched = False

        for obj in tracked_objects:
            if distance(obj['position'], object_center) < 50:
                obj['position'] = object_center
                obj['stationary'] = distance(obj['initial_position'], object_center) < 20
                obj['disappearance_count'] = 0
                obj['updated'] = True
                matched = True
                break

        if not matched:
            tracked_objects.append({
                'position': object_center,
                'initial_position': object_center,
                'stationary': True,
                'disappearance_count': 0,
                'updated': True
            })

    # Update disappearance count and remove disappeared objects
    tracked_objects = [obj for obj in tracked_objects if obj['updated'] or obj['disappearance_count'] < disappearance_threshold]
    for obj in tracked_objects:
        if not obj['updated']:
            obj['disappearance_count'] += 1

    # Draw the results on the contour frame
    for obj in tracked_objects:
        color = (0, 255, 0) if obj['stationary'] else (0, 0, 255)
        cv2.circle(contour_frame, obj['position'], 5, color, -1)

    # Concatenate the original frame, preprocessed frame, and contour frame
    combined_frame = cv2.hconcat([frame, preprocessed_frame, contour_frame])

    # Display the combined frame
    cv2.imshow('Combined Frame', combined_frame)
    if cv2.waitKey(30) & 0xFF == 27:
        break

    # Update the previous frame
    prev_gray = blurred_frame.copy()

cap.release()
cv2.destroyAllWindows()
