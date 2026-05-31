# Control script for Cobot control. This handles all communication with the cobot,
# and will be called by the main script.

########### Config

cobot_ip         = "192.168.0.1"
speed            = 100
pick_dip         = 50                       # mm to lower for a pick operation
suction_DO       = 0                        # digital output number for suction
mock             = True                     # Set False when connected to the real cobot
calibration_dist = 50                       # mm the robot moves during calibration
home_position    = "550,-150,450,180,0,90"  # home/calibration height
place_position   = "400,-150,450,180,0,90"  # where picked dishes are placed

########### Imports

import sys
import json
import time
sys.path.append("libraries")

if mock:
    print("[MOCK] Cobot connection skipped.")
    class _MockCob:
        def readPos(self):               return [0, 0, 0, 180, 0, 90]
        def sendCobotPos(self, p, s):    print(f"[MOCK] Move to {p} at speed {s}")
        def O_out(self, do, val):        print(f"[MOCK] DO{do} = {val}")
    cob = _MockCob()
else:
    from EasyModbusPy.cobotconnect1 import cobotconnect
    cob = cobotconnect(host=cobot_ip)

########### Calibration

CALIBRATION_FILE = "calibration.json"

def load_calibration():
    try:
        with open(CALIBRATION_FILE) as f:
            data = json.load(f)
        print(f"Calibration loaded: x={data['px_per_mm_x']:.3f} px/mm  y={data['px_per_mm_y']:.3f} px/mm")
        return data["px_per_mm_x"], data["px_per_mm_y"]
    except FileNotFoundError:
        return None

def save_calibration(px_per_mm_x, px_per_mm_y):
    with open(CALIBRATION_FILE, "w") as f:
        json.dump({"px_per_mm_x": px_per_mm_x, "px_per_mm_y": px_per_mm_y}, f, indent=2)
    print(f"Calibration saved to {CALIBRATION_FILE}")

def calibrate(get_detections, move_delay=3):
    print("=== Calibration ===")
    print(f"Moving to home position for consistent camera height...")
    cob.sendCobotPos(home_position, speed)
    time.sleep(move_delay)

    # Wait until a dish is visible
    detections = []
    while not detections:
        detections = get_detections()
        time.sleep(0.1)

    # Use the dish closest to center as reference (assumes one dish near center)
    ref = min(detections, key=lambda d: d["x"]**2 + d["y"]**2)
    ref_id = ref["id"]
    print(f"Using dish ID {ref_id} as reference at ({ref['x']:.0f}, {ref['y']:.0f})")

    def get_ref():
        return next((d for d in get_detections() if d["id"] == ref_id), None)

    # ── Measure X axis ────────────────────────────────────────────────────────
    print(f"Moving +{calibration_dist} mm in X...")
    move(dx=calibration_dist)
    time.sleep(move_delay)

    after_x = get_ref()
    if after_x is None:
        raise RuntimeError("Lost dish during X calibration — try a larger move_delay or reposition dish.")

    px_per_mm_x = abs(after_x["x"] - ref["x"]) / calibration_dist
    print(f"X: moved {abs(after_x['x'] - ref['x']):.1f} px → {px_per_mm_x:.3f} px/mm")

    # Move back
    move(dx=-calibration_dist)
    time.sleep(move_delay)

    # ── Measure Y axis ────────────────────────────────────────────────────────
    print(f"Moving +{calibration_dist} mm in Y...")
    move(dy=calibration_dist)
    time.sleep(move_delay)

    after_y = get_ref()
    if after_y is None:
        raise RuntimeError("Lost dish during Y calibration — try a larger move_delay or reposition dish.")

    px_per_mm_y = abs(after_y["y"] - ref["y"]) / calibration_dist
    print(f"Y: moved {abs(after_y['y'] - ref['y']):.1f} px → {px_per_mm_y:.3f} px/mm")

    # Move back
    move(dy=-calibration_dist)
    time.sleep(move_delay)

    save_calibration(px_per_mm_x, px_per_mm_y)
    print("=== Calibration done ===")
    return px_per_mm_x, px_per_mm_y

########### Module

def move(dx=0, dy=0, dz=0):
    """Move relative to the current position. All values in mm."""
    parts = []
    if dx: parts.append(f"x{dx:+.1f}")
    if dy: parts.append(f"y{dy:+.1f}")
    if dz: parts.append(f"z{dz:+.1f}")
    print(f"Cobot moving {', '.join(parts) if parts else 'nowhere'}")
    P = cob.readPos()
    x, y, z, a, b, c = P[0], P[1], P[2], P[3], P[4], P[5]
    cob.sendCobotPos(f"{x+dx},{y+dy},{z+dz},{a},{b},{c}", speed)

def command(cmd):
    """
    Execute a named command.
    Available commands:
      "pick"  – lower pick_dip mm, enable suction, raise back up
    """
    if cmd == "pick":
        move(dz=+pick_dip)
        cob.O_out(suction_DO, 1)    # suction on
        move(dz=-pick_dip)
    else:
        raise ValueError(f"Unknown command: '{cmd}'")

########### Main

if __name__ == "__main__":
    pos = input("lees huidig of Geef positie. x,y,z,a,b,c of home: ")

    if pos == "huidig":
        P = cob.readPos()
        print("Positie x,y,z,a,b,c= ", P[0], P[1], P[2], P[3], P[4], P[5])
    elif pos == "home":
        pos = "550,-150,450,180,0,90"
        cob.sendCobotPos(pos, speed)
    else:
        cob.sendCobotPos(pos, speed)