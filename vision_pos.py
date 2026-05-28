"""
Vision script for Cobot control, the IO of this script is standardised, so it can be exchanged with other vision scripts.

This script can be used standalone, but it is designed to be used as a module in the main script. 
"""

########## Imports ##########

from ultralytics import YOLO
import cv2

########## Config ##########

model = YOLO("models/petri_v2n.pt")         # Path to prediction model.
confidence = 0.8                            # Filter detections below 0.8
radius = 80                                 # Maximum difference between locations to keep same id
memory = 60                                 # Amount of frames to wait before dropping id

########## Initialise ##########

tracked  = {}   # { id: { id, class, sx, sy, missing_frames } }
next_id  = 1    # increments each time a new object is found, never reused

########## Module ##########

def find_or_create(class_name, x, y):
    global next_id

    best      = None
    best_dist = float("inf")

    for obj in tracked.values():
        if obj["class"] != class_name:
            continue
        dist = ((obj["x"] - x) ** 2 + (obj["y"] - y) ** 2) ** 0.5
        if dist < radius and dist < best_dist:
            best_dist = dist
            best      = obj

    if best is not None:
        best["x"]             = x
        best["y"]             = y
        best["missing_frames"] = 0
        return best
    else:
        new_obj = { "id": next_id, "class": class_name, "x": x, "y": y, "missing_frames": 0 }
        tracked[next_id] = new_obj
        next_id += 1
        return new_obj


def run(source=0):
    for result in model(source=source, show=True, conf=confidence, stream=True, verbose=False):

        # Mark all objects as missing
        for obj in tracked.values():
            obj["missing_frames"] += 1

        # Match detections to tracked objects
        detections = []
        for box in result.boxes:
            x1, y1, x2, y2 = (float(v) for v in box.xyxy[0])
            class_name      = result.names[int(box.cls[0])]
            x, y            = (x1 + x2) / 2, (y1 + y2) / 2

            obj = find_or_create(class_name, x, y)
            detections.append({ "id": obj["id"], "x": obj["x"], "y": obj["y"] })

        # Remove objects missing too long
        for obj_id in [k for k, v in tracked.items() if v["missing_frames"] > memory]:
            del tracked[obj_id]

        yield detections


########## Main ##########

if __name__ == "__main__":

# Ask to list available camera id's.
    list_cam = input("Do you want to list available camera's? (y/n) ")

# List available camera id's.
    if list_cam == "y":
        for i in range(10):
            cap = cv2.VideoCapture(i)
            if cap.read()[0]:
                print(f"Camera {i}: available")
            cap.release()

# Select camera for prediction.
    cam = int(input("Select a camera: "))

# Prediction.
    for detections in run(source=cam):
        for d in detections:
            print(f"ID {d['id']}  x={d['x']:.0f}  y={d['y']:.0f}")
        print()