# Control script for Cobot control. This handles all communication with the cobot,
# and will be called by the main script.

########### Config

cobot_ip         = "192.168.0.1"
speed            = 80
pick_dip         = 260                       # mm to lower for a pick operation
suction_DO       = 7                        # digital output number for suction
mock             = False                    # Set True when not connected to the real cobot
calibration_dist = 50                       # mm the robot moves during calibration
home_position    = "650,-150,300,180,0,90"  # home/calibration height
place_position   = "433,-585,47,180,0,90"  # where picked dishes are placed

########### Imports

import sys
import json
import time
import multiprocessing
sys.path.append("libraries")

########### Cobot subprocess

def _cobot_process(command_queue, result_queue, cobot_ip, speed):
    sys.path.append("libraries")
    from EasyModbusPy.cobotconnect1 import cobotconnect
    cob = cobotconnect(host=cobot_ip)
    result_queue.put(("ready", None))

    while True:
        cmd, args = command_queue.get()
        try:
            if cmd == "move":
                dx, dy, dz = args
                P = cob.readPos()
                x, y, z, a, b, c = P[0], P[1], P[2], P[3], P[4], P[5]
                pos = f"{x+dx:.2f},{y+dy:.2f},{z+dz:.2f},{a:.2f},{b:.2f},{c:.2f}"
                print(f"Sending position: {pos}")
                cob.sendCobotPos(pos, speed)
                result_queue.put(("ok", None))
            elif cmd == "readPos":
                result_queue.put(("ok", cob.readPos()))
            elif cmd == "sendPos":
                cob.sendCobotPos(args[0], args[1])
                result_queue.put(("ok", None))
            elif cmd == "O_out":
                print(f"[SUBPROCESS] O_out coil={args[0]} value={args[1]}")  # ← here
                cob.O_out(args[0], args[1])
                result_queue.put(("ok", None))
            elif cmd == "stop":
                break
        except Exception as e:
            print(f"[SUBPROCESS] Exception: {e}")  # ← and here, to catch silent failures
            result_queue.put(("error", str(e)))

########### Connection

_command_queue = None
_result_queue  = None
_process       = None

def _send(cmd, args=None):
    if mock:
        if cmd == "move":
            dx, dy, dz = args
            parts = []
            if dx: parts.append(f"x{dx:+.1f}")
            if dy: parts.append(f"y{dy:+.1f}")
            if dz: parts.append(f"z{dz:+.1f}")
            print(f"[MOCK] Cobot moving {', '.join(parts) if parts else 'nowhere'}")
        elif cmd == "readPos":
            return [0, 0, 0, 180, 0, 90]
        elif cmd == "sendPos":
            print(f"[MOCK] Move to {args[0]} at speed {args[1]}")
        elif cmd == "O_out":
            print(f"[MOCK] DO{args[0]} = {args[1]}")
    else:
        _command_queue.put((cmd, args))
        status, result = _result_queue.get()
        if status == "error":
            raise RuntimeError(f"Cobot error: {result}")
        return result

def connect():
    """Start the cobot subprocess. Call once before any cobot commands."""
    global _command_queue, _result_queue, _process
    if mock:
        print("[MOCK] Cobot connection skipped.")
        return
    _command_queue = multiprocessing.Queue()
    _result_queue  = multiprocessing.Queue()
    _process       = multiprocessing.Process(
        target=_cobot_process,
        args=(_command_queue, _result_queue, cobot_ip, speed),
        daemon=True
    )
    _process.start()
    status, _ = _result_queue.get(timeout=10)
    if status != "ready":
        raise RuntimeError("Cobot process failed to connect.")

########### Calibration

CALIBRATION_FILE = "calibration.json"

def load_calibration():
    """Load px_per_mm_x and px_per_mm_y from file. Returns None if not found."""
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

def calibrate(get_detections, move_delay=5):
    """
    Camera calibration for a wrist-mounted camera (camera moves with robot).
    Place a dish anywhere in view before calling — closest to center is used.
    Robot moves calibration_dist mm in X then Y and measures pixel displacement.
    Returns (px_per_mm_x, px_per_mm_y) and saves to calibration.json.
    """
    print("=== Calibration ===")
    print("Moving to home position...")
    _send("sendPos", (home_position, speed))
    time.sleep(move_delay)

    detections = []
    while not detections:
        detections = get_detections()
        time.sleep(0.1)

    ref    = min(detections, key=lambda d: d["x"]**2 + d["y"]**2)
    ref_id = ref["id"]
    print(f"Reference dish ID {ref_id} at pixel ({ref['x']:.0f}, {ref['y']:.0f})")

    def get_ref():
        return next((d for d in get_detections() if d["id"] == ref_id), None)

    # ── Measure X ─────────────────────────────────────────────────────────────
    print(f"Moving +{calibration_dist} mm in X...")
    move(dx=calibration_dist)
    time.sleep(move_delay)
    after_x = get_ref()
    if after_x is None:
        raise RuntimeError("Lost dish during X calibration. Try smaller calibration_dist or longer move_delay.")
    pixel_shift_x = after_x["x"] - ref["x"]
    px_per_mm_x   = abs(pixel_shift_x) / calibration_dist
    print(f"X: dish shifted {pixel_shift_x:+.1f} px → {px_per_mm_x:.3f} px/mm")
    if px_per_mm_x < 0.1:
        raise RuntimeError(f"X result ({px_per_mm_x:.3f} px/mm) too low — increase move_delay.")
    move(dx=-calibration_dist)
    time.sleep(move_delay)

    # ── Measure Y ─────────────────────────────────────────────────────────────
    print(f"Moving +{calibration_dist} mm in Y...")
    move(dy=calibration_dist)
    time.sleep(move_delay)
    after_y = get_ref()
    if after_y is None:
        raise RuntimeError("Lost dish during Y calibration. Try smaller calibration_dist or longer move_delay.")
    pixel_shift_y = after_y["y"] - ref["y"]
    px_per_mm_y   = abs(pixel_shift_y) / calibration_dist
    print(f"Y: dish shifted {pixel_shift_y:+.1f} px → {px_per_mm_y:.3f} px/mm")
    if px_per_mm_y < 0.1:
        raise RuntimeError(f"Y result ({px_per_mm_y:.3f} px/mm) too low — increase move_delay.")
    move(dy=-calibration_dist)
    time.sleep(move_delay)

    save_calibration(px_per_mm_x, px_per_mm_y)
    print("=== Calibration done ===")
    return px_per_mm_x, px_per_mm_y

########### Module

def home():
    """Move robot to home position."""
    _send("sendPos", (home_position, speed))

def move(dx=0, dy=0, dz=0):
    """Move relative to current position. All values in mm."""
    parts = []
    if dx: parts.append(f"x{dx:+.1f}")
    if dy: parts.append(f"y{dy:+.1f}")
    if dz: parts.append(f"z{dz:+.1f}")
    print(f"Cobot moving {', '.join(parts) if parts else 'nowhere'}")
    _send("move", (dx, dy, dz))

def command(cmd):
    """
    Execute a named command.
    Available commands:
      "pick"  – lower pick_dip mm, turn suction on, raise back up
      "place" – move to place position, turn suction off
    """
    if cmd == "pick":
        move(dz=-pick_dip)
        _send("O_out", (suction_DO, False))     # suction on
        move(dz=+pick_dip)

    elif cmd == "place":
        _send("sendPos", (place_position, speed))
        time.sleep(7)               # wait for robot to fully arrive
        _send("O_out", (suction_DO, True))
        _send("sendPos", (home_position, speed))
    else:
        raise ValueError(f"Unknown command: '{cmd}'")

########### Main

if __name__ == "__main__":
    import multiprocessing
    multiprocessing.set_start_method("fork")
    connect()
    pos = input("lees huidig of Geef positie. x,y,z,a,b,c of home: ")

    if pos == "huidig":
        P = _send("readPos")
        print("Positie x,y,z,a,b,c= ", P[0], P[1], P[2], P[3], P[4], P[5])
    elif pos == "home":
        home()
    else:
        _send("sendPos", (pos, speed))