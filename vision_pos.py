"""
Vision script for Cobot control, the IO of this script is standardised, so it can be exchanged with other vision scripts.
This script can be used standalone, but it is designed to be used as a module in the main script. 
"""
########## Imports ##########
from ultralytics import YOLO
import cv2
import numpy as np
import time

########## Config ##########
model      = YOLO("models/petri_v2n.pt")    # Path to prediction model.
source     = 0                              # Camera index or video path
confidence = 0.6                            # Filter detections below 0.8
radius     = 80                             # Maximum difference between locations to keep same id
memory     = 10                             # Amount of frames to wait before dropping id

########## Initialise ##########
tracked       = {}      # { id: { id, class, x, y, missing_frames } }
next_id       = 1       # increments each time a new object is found, never reused
last_time     = time.time()
fps           = 0.0
target_id     = None    # set from main.py to highlight the target dish
robot_status  = "IDLE"  # set from main.py to show robot state in overlay
latest_frame  = None    # most recent clean (pre-annotation) frame; read by vision_class

overlay_items = [
    { "label": "FPS",    "value": lambda: f"{fps:.1f}",    "color": (0, 255, 0)   },
    { "label": "Robot",  "value": lambda: robot_status,    "color": (0, 255, 255) },
    # ← add more items here, see instructions above
]

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
        best["x"]              = x
        best["y"]              = y
        best["missing_frames"] = 0
        return best
    else:
        new_obj = { "id": next_id, "class": class_name, "x": x, "y": y, "missing_frames": 0 }
        tracked[next_id] = new_obj
        next_id += 1
        return new_obj

def draw_overlay(frame):
    padding = 6
    x_start = 10
    y_start = 10
    font       = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.55
    thickness  = 1

    for item in overlay_items:
        value = item["value"]() if callable(item["value"]) else item["value"]
        text  = f"{item['label']}: {value}"
        color = item.get("color", (255, 255, 255))

        (tw, th), baseline = cv2.getTextSize(text, font, font_scale, thickness)
        cv2.rectangle(frame,
                      (x_start - 2, y_start - 2),
                      (x_start + tw + padding, y_start + th + padding),
                      (0, 0, 0), -1)
        cv2.putText(frame, text,
                    (x_start + padding // 2, y_start + th),
                    font, font_scale, color, thickness, cv2.LINE_AA)
        y_start += th + padding + 4

def draw_crosshair(frame, x, y, size=20, color=(0, 255, 255), thickness=1):
    """Draw a crosshair at (x, y)."""
    cv2.line(frame, (x - size, y), (x + size, y), color, thickness)
    cv2.line(frame, (x, y - size), (x, y + size), color, thickness)
    cv2.circle(frame, (x, y), 4, color, thickness)

def draw_annotations(frame, result, detections):
    h, w = frame.shape[:2]
    cx, cy = w // 2, h // 2

    draw_crosshair(frame, cx, cy, size=24, color=(0, 255, 255), thickness=1)

    for box, det in zip(result.boxes, detections):
        x1, y1, x2, y2 = (int(float(v)) for v in box.xyxy[0])
        conf            = float(box.conf[0])
        class_name      = result.names[int(box.cls[0])]
        dx, dy          = det["x"], det["y"]
        obj_id          = det["id"]

        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 200, 0), 2)
        cv2.circle(frame, (int(dx), int(dy)), 5, (0, 0, 255), -1)

        label = f"ID:{obj_id} {class_name} {conf:.2f}"
        (tw, th), baseline = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 1)
        label_y = max(y1 - 6, th + 4)
        cv2.rectangle(frame, (x1, label_y - th - 4), (x1 + tw + 4, label_y + baseline), (0, 200, 0), -1)
        cv2.putText(frame, label, (x1 + 2, label_y - 2), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 0), 1, cv2.LINE_AA)

        if obj_id == target_id:
            cv2.line(frame, (cx, cy), (int(dx), int(dy)), (0, 100, 255), 2)

    return frame

def run():
    global tracked, last_time, fps, latest_frame

    for result in model(source=source, show=False, conf=confidence, stream=True, verbose=False):
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

        # Update FPS
        now       = time.time()
        fps       = 1.0 / (now - last_time) if (now - last_time) > 0 else 0.0
        last_time = now

        # Store clean frame for classification before drawing annotations on it
        latest_frame = result.orig_img.copy()

        # Draw annotations and show
        frame = latest_frame.copy()
        frame = draw_annotations(frame, result, detections)
        draw_overlay(frame)
        cv2.imshow("Vision", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

        yield detections

    cv2.destroyAllWindows()

########## Main ##########
if __name__ == "__main__":
    list_cam = input("Do you want to list available camera's? (y/n) ")

    if list_cam == "y":
        for i in range(10):
            cap = cv2.VideoCapture(i)
            if cap.read()[0]:
                print(f"Camera {i}: available")
            cap.release()

    source = int(input(f"Select a camera (current: {source}): ") or source)

    for detections in run():
        for d in detections:
            print(f"ID {d['id']}  x={d['x']:.0f}  y={d['y']:.0f}")
        print()