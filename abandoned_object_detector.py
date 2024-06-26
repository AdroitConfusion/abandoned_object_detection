import numpy as np
import cv2
from tracker import *
from os import path
import argparse

# Function to put text on an image
def put_text(image, text, position=(30, 100)):
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1
    font_color = (255, 255, 255)
    thickness = 2
    cv2.putText(image, text, position, font, font_scale, font_color, thickness, cv2.LINE_AA)

def apply_train_mask(frame):
    train_mask = np.zeros(frame.shape[:2], dtype = "uint8")
    pts = np.array([[280, 80], [0, 300], [0, 500], [700, 500], [700, 80]], np.int32)
    cv2.polylines(frame, [pts], True, (255, 0, 0), thickness=2)
    cv2.fillPoly(train_mask,[pts],255,1)
    masked = cv2.bitwise_and(frame, frame, mask=train_mask)
    return masked

if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Toggle train mask on and off.')
    parser.add_argument('--train-mask', action='store_true', help='Enable train mask if set')
    args = parser.parse_args()


    # Calculate paths
    example_no = 'example 2'
    base_path = 'examples'
    background_path = path.join(base_path, example_no, 'bg.png')
    video_path = path.join(base_path, example_no, 'video.avi')
    output_path = path.join(base_path, example_no, 'output.mp4')

    # Preprocess background image
    background = cv2.imread(background_path)
    if args.train_mask:
        background = apply_train_mask(background)
    background_gray = cv2.cvtColor(background, cv2.COLOR_BGR2GRAY)
    background_hist = cv2.equalizeHist(background_gray)
    background_blur = cv2.GaussianBlur(background_hist, (7, 7), 0)
    preproc_background = cv2.medianBlur(background_blur, 5) 

    
    # Set up video reader
    cap = cv2.VideoCapture(video_path)
    ret, frame = cap.read()
    if not ret:
        print("Error: Could not open video.")
        exit()
    frame_height, frame_width, _ = frame.shape

    # Set up video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, 20.0, (frame_width * 3, frame_height * 2))
    tracker = ObjectTracker()

    while (cap.isOpened()):
        ret, frame = cap.read()
        if not ret:
            break
        
        if args.train_mask:
            frame = apply_train_mask(frame)
        
        frame_height, frame_width, _ = frame.shape

        # Convert to grayscale
        frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Histogram Equalization
        frame_hist = cv2.equalizeHist(frame_gray)

        # Blur
        frame_blur = cv2.GaussianBlur(frame_hist, (7, 7), 0)
        preproc_frame = cv2.medianBlur(frame_blur, 5)     

        # Background Subtraction
        frame_diff = cv2.absdiff(preproc_background, preproc_frame)
        
        # Threshold
        _, thresh = cv2.threshold(frame_diff, 80, 255, cv2.THRESH_BINARY)
        # thresh = cv2.adaptiveThreshold(frame_blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)

        # Morphological Operations
        kernel_open = np.ones((5, 5), np.uint8)
        kernel_close = np.ones((5, 5), np.uint8)
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel_open, iterations=1)
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel_close, iterations=1)

        # Find contours in the edge-detected image
        stencil_edges = cv2.Canny(thresh, 50, 200)
        stencil_contours, _ = cv2.findContours(stencil_edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Specify the fill color (white)
        fill_color = [255, 255, 255]

        # Create a stencil (mask) with zeros
        stencil = np.zeros(thresh.shape).astype(thresh.dtype)

        # Fill the contours in the stencil
        cv2.fillPoly(stencil, stencil_contours, fill_color)

        # Apply the stencil to the original image
        stencil_img = cv2.bitwise_or(thresh, stencil)
        
        # Edge Detection
        edges = cv2.Canny(stencil_img, 50, 200) 
        
        # Contour Detection
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)

        # Draw contours
        image_contours  = np.zeros((frame_height, frame_width, 3), dtype=np.uint8)
        cv2.drawContours(image_contours, contours, -1, (255, 0, 0), 3)

        # Detect abandoned objects
        detections = []
        count = 0
        for cnt in contours:
            contour_area = cv2.contourArea(cnt)
            
            if 1000 < contour_area < 100000:
                count += 1

                (x, y, w, h) = cv2.boundingRect(cnt)

                detections.append([x, y, w, h])

        _, abandoned_objects = tracker.update(detections)
        
        # if abandoned_objects:
        #     print(abandoned_objects)
        
        # Draw bounding boxes on abandoned objects
        for objects in abandoned_objects:
            _, x2, y2, w2, h2, _ = objects
            
            cv2.putText(frame, "Abandoned Object", (x2, y2 - 10), cv2.FONT_HERSHEY_PLAIN, 1.2, (0, 0, 255), 2)
            cv2.rectangle(frame, (x2, y2), (x2 + w2, y2 + h2), (0, 0, 255), 2)

        # Convert 2D images to 3D
        diff_3d = cv2.cvtColor(frame_diff, cv2.COLOR_GRAY2BGR)
        blur_3d = cv2.cvtColor(preproc_frame, cv2.COLOR_GRAY2BGR)
        thresh_3d = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)
        edges_3d = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)

        # Put text on each image
        put_text(frame, "Original with Bounding Boxes")
        put_text(diff_3d, "Background Subtraction")
        put_text(blur_3d, "Blur")
        put_text(thresh_3d, "Threshold")
        put_text(edges_3d, "Edges")
        put_text(image_contours, "Contours")

        # Show combined image
        row_one = np.hstack((frame, diff_3d, blur_3d))
        row_two = np.hstack((thresh_3d, edges_3d, image_contours))
        combined_image = np.vstack((row_one, row_two))
        # print("Frame dimensions:", frame.shape[:2])
        # print("Combined image dimensions:", combined_image.shape[:2])

        cv2.imshow('Combined Image', combined_image)
        out.write(combined_image)
        

        if cv2.waitKey(15) == ord('q'):
            break

    cap.release()
    out.release()
    cv2.destroyAllWindows()

