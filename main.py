# Main script for Cobot control, this will call functions for vision, and controlling the cobot, this also houses the interface.

########### Config



########### Imports

import vision_pos

########### Main

for detections in vision_pos.run(source=1):
    for d in detections:
        print(d["id"], d["x"], d["y"])
