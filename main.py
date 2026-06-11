# Main script for Cobot control.
import multiprocessing
multiprocessing.set_start_method("fork")    # avoids macOS spawn reimporting main.py

########### Config

center_tolerance = 20                       # pixels: how close to center counts as "arrived"
stable_frames    = 5                        # frames dish must be near center before picking
frame_w, frame_h = 1280, 720               # camera resolution
move_delay       = 3                        # seconds to wait after a move command
px_per_mm_x      = 1.9
px_per_mm_y      = 1.9

########### Imports

import time
import threading
import vision_pos
import vision_class
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
    
    # Track whether the user has enabled automatic sorting
    auto_mode = False

    def get_target():
        return next((d for d in latest_detections if d["id"] == target_id), None)

    def is_centered(det):
        dist = ((det["x"] - cx) ** 2 + (det["y"] - cy) ** 2) ** 0.5
        return dist < center_tolerance

    # Infinite loop to keep sorting dishes
    while True:
        # Home the robot at the start of the loop to clear the camera view
        control.home()
        vision_pos.robot_status = "IDLE"

        # ── Step 1: wait for stable detections ───────────────────────────────────
        print("\nWaiting for dishes to appear...")
        vision_pos.robot_status = "SCANNING"
        while not latest_detections:
            time.sleep(0.1)
        time.sleep(1)   # let tracker stabilise

        # ── Step 2: choose which dish to pick ──────────────────────────────────
        print("\nFound dishes:")
        for d in latest_detections:
            print(f"  ID {d['id']}  x={d['x']:.0f}  y={d['y']:.0f}")

        if not auto_mode:
            user_input = input("Enter ID to pick (or 'auto'): ").strip().lower()
            if user_input == 'auto':
                auto_mode = True
            else:
                try:
                    target_id = int(user_input)
                except ValueError:
                    print("Invalid input. Please enter a valid ID or 'auto'.")
                    continue
        
        if auto_mode:
            # Calculate squared distance to the center (cx, cy) for all detections
            # and return the dish with the minimum distance.
            closest_dish = min(
                latest_detections, 
                key=lambda d: (d["x"] - cx)**2 + (d["y"] - cy)**2
            )
            target_id = closest_dish["id"]
            print(f"\n[Auto Mode] Selected closest dish ID: {target_id}")

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

        # ── Step 3.5: classify the dish ───────────────────────────────────────────
        control.command("focus")
        vision_pos.robot_status = "CLASSIFYING"
        frame = vision_pos.latest_frame

        if frame is not None:
            color, confidence = vision_class.classify_frame(frame)
            print(f"\n┌─ Classification result ──────────────────")
            print(f"│  Colour    : {color}")
            print(f"│  Confidence: {confidence * 100:.1f}%")
            print(f"└──────────────────────────────────────────\n")
        else:
            color = "leeg"
            print("Warning: no camera frame available for classification, defaulting to 'leeg'.")

        place_pos = control.place_positions.get(color, control.place_positions["leeg"])
        print(f"Place position: {place_pos}")

        # ── Step 4: pick ──────────────────────────────────────────────────────────
        vision_pos.robot_status = "PICKING"
        vision_pos.target_id    = None
        control.command("pick")
        time.sleep(1)

        # ── Step 5: place ─────────────────────────────────────────────────────────
        vision_pos.robot_status = "PLACING"
        print(f"Placing '{color}' dish at {place_pos}...")
        control.command("place", place_pos=place_pos)
        
        print("\nDish sorted! Starting next cycle...")

########### Main (vision runs here, on the main thread)

# Start cobot logic in background
t = threading.Thread(target=cobot_thread, daemon=True)
t.start()

print("Press 'q' in the camera window to exit.")

# Vision loop runs on main thread (required on macOS)
for detections in vision_pos.run():
    latest_detections = detections