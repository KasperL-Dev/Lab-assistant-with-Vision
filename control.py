# Control script for Cobot control. This handles all communication with the cobot,
# and will be called by the main script.

########### Config

cobot_ip = "192.168.0.1"
speed = 100

########### Imports

import sys
sys.path.append("libraries")
from EasyModbusPy.cobotconnect1 import cobotconnect
cob = cobotconnect(host=cobot_ip)

########### Main

if __name__ == "__main__":
    pos = input("lees huidig of Geef positie. x,y,z,a,b,c of home: ")

    if pos == "huidig":
        P=cob.readPos() 
        print("Positie x,y,z,a,b,c= ",P[0],P[1],P[2],P[3],P[4],P[5])

    elif pos == "home":
        pos = "550,-150,450,180,0,90"
        cob.sendCobotPos(pos,speed) 

    else:
        cob.sendCobotPos(pos,speed) 

########### Module