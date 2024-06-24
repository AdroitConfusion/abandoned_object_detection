import math
import time

class ObjectTracker:
    def __init__(self):
        self.center_points = {}
        self.id_count = 0
        self.abandoned_temp = {}
        self.time_stamps = {}

    def update(self, objects_rect):
        objects_bbs_ids = []
        abandoned_objects = []

        current_time = time.time()

        # Get center point of new object
        for rect in objects_rect:
            x, y, w, h = rect
            cx = (x + x + w) / 2
            cy = (y + y + h) / 2

            # Find out if that object was detected already
            same_object_detected = False
            for id, pt in self.center_points.items():
                distance = math.hypot(cx - pt[0], cy - pt[1])

                if distance < 25:
                    self.center_points[id] = (cx, cy)
                    objects_bbs_ids.append([x, y, w, h, id, distance])
                    same_object_detected = True

                    if id in self.abandoned_temp:
                        if distance < 1:
                            if (current_time - self.time_stamps[id]) > 10:  # 10 seconds threshold
                                abandoned_objects.append([id, x, y, w, h, distance])
                            else:
                                self.abandoned_temp[id] += 1
                        else:
                            self.time_stamps[id] = current_time  # Reset timestamp if the object moves
                    else:
                        self.abandoned_temp[id] = 1
                        self.time_stamps[id] = current_time  # Initialize timestamp for the new object

                    break

            if not same_object_detected:
                self.center_points[self.id_count] = (cx, cy)
                self.abandoned_temp[self.id_count] = 1
                self.time_stamps[self.id_count] = current_time
                objects_bbs_ids.append([x, y, w, h, self.id_count, None])
                self.id_count += 1

        # Clean the dictionary by center points to remove IDS not used anymore
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

        return objects_bbs_ids, abandoned_objects