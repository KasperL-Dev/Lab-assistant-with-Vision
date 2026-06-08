# Main script for Cobot control.
import multiprocessing
multiprocessing.set_start_method("fork")    # avoids macOS spawn reimporting main.py

########### Config

center_tolerance = 20                       # pixels: how close to center counts as "arrived"
stable_frames    = 5                        # frames dish must be near center before picking
frame_w, frame_h = 1280, 720               # camera resolution
move_delay       = 3                        # seconds to wait after a move command

########### Imports

import time
import threading
import vision_pos
import control

########### Shared state

latest_detections = []
target_id         = None

########### Cobot logic (runs in background thread)

def cobot_thread():
    global target_id

    cx, cy = frame_w // 2, frame_h // 2

    control.connect()
    control.home()

    def get_target():
        return next((d for d in latest_detections if d["id"] == target_id), None)

    def is_centered(det):
        dist = ((det["x"] - cx) ** 2 + (det["y"] - cy) ** 2) ** 0.5
        return dist < center_tolerance

    # ── Calibration ───────────────────────────────────────────────────────────
    cal = control.load_calibration()
    if cal is None:
        ans = input("No calibration found. Run calibration now? (y/n): ")
        if ans.lower() == "y":
            cal = control.calibrate(
                get_detections=lambda: latest_detections,
                move_delay=move_delay
            )
        else:
            print("Using fallback pixels_per_mm = 2.0 for both axes.")
            cal = (2.0, 2.0)

    px_per_mm_x, px_per_mm_y = cal

    # ── Step 1: wait for stable detections ───────────────────────────────────
    print("Waiting for dishes to appear...")
    vision_pos.robot_status = "SCANNING"
    while not latest_detections:
        time.sleep(0.1)
    time.sleep(1)   # let tracker stabilise

    # ── Step 2: ask user which dish to pick ──────────────────────────────────
    print("\nFound dishes:")
    for d in latest_detections:
        print(f"  ID {d['id']}  x={d['x']:.0f}  y={d['y']:.0f}")

    target_id               = int(input("Enter ID to pick: "))
    vision_pos.target_id    = target_id
    vision_pos.robot_status = "MOVING"

    # ── Step 3: move to dish, retry until centered ────────────────────────────
    centered_count = 0
    while True:
        time.sleep(0.1)
        target = get_target()

        if target is None:
            print("Target not visible, waiting...")
            centered_count = 0
            continue

        if is_centered(target):
            centered_count += 1
            print(f"On target ({centered_count}/{stable_frames})...")
            if centered_count >= stable_frames:
                break
        else:
            centered_count = 0
            dy_mm = (target["x"] - cx) / px_per_mm_x
            dx_mm = (target["y"] - cy) / px_per_mm_y
            control.move(dx=dx_mm, dy=dy_mm)
            time.sleep(move_delay)

    # ── Step 4: pick ──────────────────────────────────────────────────────────
    vision_pos.robot_status = "PICKING"
    vision_pos.target_id    = None
    control.command("pick")
    time.sleep(1)

    # ── Step 5: place ─────────────────────────────────────────────────────────
    vision_pos.robot_status = "PLACING"
    print(f"Placing at {control.place_position}...")
    control.command("place")

    vision_pos.robot_status = "IDLE"
    print("Done. Press q in the camera window to exit.")

########### Main (vision runs here, on the main thread)

# Start cobot logic in background
t = threading.Thread(target=cobot_thread, daemon=True)
t.start()

# Vision loop runs on main thread (required on macOS)
for detections in vision_pos.run():
    latest_detections = detections