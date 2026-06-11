# Demo script — cobot continuously positions itself above the closest dish.
import multiprocessing
multiprocessing.set_start_method("fork")

########### Imports

import time
import threading
import vision_pos
import control

########### Config

px_per_mm_x      = 1.9
px_per_mm_y      = 1.9

########### Shared state

latest_detections = []

########### Demo logic

def demo_thread():
    cx, cy = 1280 // 2, 720 // 2

    control.connect()
    control.home()

    print("Waiting for dishes...")
    vision_pos.robot_status = "SCANNING"
    while not latest_detections:
        time.sleep(0.1)

    print("Tracking closest dish. Press q in camera window to stop.")
    vision_pos.robot_status = "TRACKING"

    while True:
        time.sleep(0.1)

        if not latest_detections:
            continue

        # Pick the dish closest to camera center
        closest = min(latest_detections, key=lambda d: (d["x"] - cx)**2 + (d["y"] - cy)**2)
        vision_pos.target_id = closest["id"]

        dx_px = closest["x"] - cx
        dy_px = closest["y"] - cy
        dist  = (dx_px**2 + dy_px**2) ** 0.5

        if dist < 20:   # already centered, nothing to do
            continue

        dy_mm = dx_px / px_per_mm_x
        dx_mm = dy_px / px_per_mm_y
        control.move(dx=dx_mm, dy=dy_mm)
        time.sleep(2)   # wait for robot to arrive

########### Main

t = threading.Thread(target=demo_thread, daemon=True)
t.start()

for detections in vision_pos.run():
    latest_detections = detections