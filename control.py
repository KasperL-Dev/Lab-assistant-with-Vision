# Control script for Cobot control. This handles all communication with the cobot,
# and will be called by the main script.

########### Config

cobot_ip         = "192.168.0.1"
speed            = 100
pick_dip         = 100                       # mm to lower for a pick operation
focus_dip        = 260
camera_offset_x  = 170
camera_offset_y  = 30
suction_DO       = 7                         # digital output number for suction
mock             = False                     # Set True when not connected to the real cobot
calibration_dist = 50                        # mm the robot moves during calibration
home_position    = "500,0,400,180,0,90"   # home/calibration height

# Place positions per dish colour (Dutch names matching vision_class.py class_names).
# ↓ Adjust x,y,z coordinates for each colour to match your physical tray layout.
place_positions = {
    "leeg":  "400,-585,47,180,0,90",   # empty dish
    "blauw": "500,-585,47,180,0,90",   # blue
    "geel":  "600,-585,47,180,0,90",   # yellow
    "groen": "700,-585,47,180,0,90",   # green
    "roze":  "800,-585,47,180,0,90",   # pink
}

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
                print(f"[SUBPROCESS] O_out coil={args[0]} value={args[1]}")
                cob.O_out(args[0], args[1])
                result_queue.put(("ok", None))
            elif cmd == "stop":
                break
        except Exception as e:
            print(f"[SUBPROCESS] Exception: {e}")
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

########### Module

def home():
    """Move robot to home position."""
    _send("sendPos", (home_position, speed))
    time.sleep(10)

def move(dx=0, dy=0, dz=0):
    """Move relative to current position. All values in mm."""
    parts = []
    if dx: parts.append(f"x{dx:+.1f}")
    if dy: parts.append(f"y{dy:+.1f}")
    if dz: parts.append(f"z{dz:+.1f}")
    print(f"Cobot moving {', '.join(parts) if parts else 'nowhere'}")
    _send("move", (dx, dy, dz))

def command(cmd, place_pos=None):
    """
    Execute a named command.
    Available commands:
      "pick"  – lower pick_dip mm, turn suction on, raise back up
      "place" – move to place_pos (or 'leeg' fallback), turn suction off, return home
    """
    if cmd == "pick":
        move(dx=+camera_offset_x)
        time.sleep(5)
        move(dy=-camera_offset_y)
        time.sleep(2)
        move(dz=-pick_dip)
        _send("O_out", (suction_DO, False))     # suction on
        time.sleep(5)
        move(dz=+pick_dip)
    
    elif cmd == "focus":
        move(dz=-focus_dip)
        time.sleep(5)

    elif cmd == "place":
        pos = place_pos if place_pos is not None else place_positions["leeg"]
        _send("sendPos", (pos, speed))
        time.sleep(12)                           # wait for robot to fully arrive
        _send("O_out", (suction_DO, True))      # suction off
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