import math
import time

class ObjectTracker:
    def __init__(self):
        self.center_points = {}  # Dictionary to store the center points of detected objects
        self.id_count = 0  # Counter for assigning unique IDs to objects
        self.abandoned_temp = {}  # Temporary storage to count frames an object remains stationary
        self.time_stamps = {}  # Dictionary to store the timestamps for objects

    def update(self, objects_rect):
        objects_bbs_ids = []  # List to store bounding box coordinates and IDs
        abandoned_objects = []  # List to store information about detected abandoned objects

        current_time = time.time()  # Current time for timestamping

        # Process each detected object's bounding box
        for rect in objects_rect:
            x, y, w, h = rect
            cx = (x + x + w) / 2  
            cy = (y + y + h) / 2 

            same_object_detected = False

            # Check if the object was previously detected
            for id, pt in self.center_points.items():
                distance = math.hypot(cx - pt[0], cy - pt[1])  # Calculate the distance between centers

                if distance < 25:  # Threshold for determining if it's the same object
                    self.center_points[id] = (cx, cy)  # Update the center point
                    objects_bbs_ids.append([x, y, w, h, id, distance])  # Append bounding box and ID to list
                    same_object_detected = True

                    if id in self.abandoned_temp:
                        if distance < 1:  # Check if the object has moved less than 1 unit
                            if (current_time - self.time_stamps[id]) > 10:  # Check if object has been stationary for more than 10 seconds
                                abandoned_objects.append([id, x, y, w, h, distance])  # Mark object as abandoned
                            else:
                                self.abandoned_temp[id] += 1  # Increment the stationary frame count
                        else:
                            self.time_stamps[id] = current_time  # Reset stationary frame count if the object moves
                    else:
                        self.abandoned_temp[id] = 1  # Initialize the stationary frame count
                        self.time_stamps[id] = current_time  # Initialize timestamp for the new object

                    break

            if not same_object_detected:
                # Assign new ID to the newly detected object
                self.center_points[self.id_count] = (cx, cy)
                self.abandoned_temp[self.id_count] = 1
                self.time_stamps[self.id_count] = current_time
                objects_bbs_ids.append([x, y, w, h, self.id_count, None])
                self.id_count += 1

        # Clean dictionary by removing the IDs of objects that aren't in frame anymore

        # new_center_points = {}
        # new_abandoned_temp = {}
        # new_time_stamps = {}
        
        # for obj_bb_id in objects_bbs_ids:
        #     _, _, _, _, object_id, _ = obj_bb_id
        #     center = self.center_points[object_id]
            
        #     new_center_points[object_id] = center

        #     if object_id in self.abandoned_temp:
        #         counts = self.abandoned_temp[object_id]
        #         new_abandoned_temp[object_id] = counts
        #         new_time_stamps[object_id] = self.time_stamps[object_id]

        # self.center_points = new_center_points
        # self.abandoned_temp = new_abandoned_temp
        # self.time_stamps = new_time_stamps

        return objects_bbs_ids, abandoned_objects  # Return the list of object bounding boxes with IDs and the list of abandoned objects
