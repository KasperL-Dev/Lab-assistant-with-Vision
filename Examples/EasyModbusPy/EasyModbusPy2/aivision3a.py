#!/usr/bin/env python3
#in submap van c:\users\kemjt\appdata\local\temp\easymodbuspy omdat anders deze library niet gevonden 
######Laat elke keer een beeld zien, toets=> volgende beeld, q=> stoppen
######
# # Type help("robolink") or help("robodk") for more information
# Press F5 to run the script
# Documentation: https://robodk.com/doc/en/RoboDK-API.html
# Reference:     https://robodk.com/doc/en/PythonAPI/index.html
# Note: It is not required to keep a copy of this file, your python script is saved with the station
from robolink import *    # RoboDK API
from robodk import *      # Robot toolbox
RDK = Robolink()

# import the necessary packages
import numpy as np
import argparse
import time
import cv2
import os
import socket
import fileinput
import time
import re
from easymodbus.modbusClient import ModbusClient
import struct
##global SP #beginwaarde 100%

#1. wachten starten "listen1"
#2. elke seconde een regel van bestand sturen totdat antwoord met OK
#3. regel van robodk omzetten naar juiste vorm (let op beperkingen)
#4. regel van bestand omzetten met Packetsender()
#5. volgende regel tot EOF
#6. scriptexit versturen
#1. wachten starten "listen1"
#2. elke seconde een regel van bestand sturen totdat antwoord met OK
#3. regel van robodk omzetten naar juiste vorm (let op beperkingen)
#4. regel van bestand omzetten met Packetsender()
#5. volgende regel tot EOF
#6. scriptexit versturen

#voor 3
def ModOut(s):
    coil=int(s[4])  
    if (s[7]=='T'):
        waarde=1
    else:
        waarde=0
    #Write a single coil to the Server – Coil number “1”
    print("write coil: " + str(coil) + ", waarde: " + str(waarde))
    modbusclient.write_single_coil(coil,waarde) #of moet True/False?
    #doet het maar staat daarna vast
    print("g=" +g)
    return
  
def zesCoord(g):
    g=g.lstrip('MOVJPLABCDEFXYZRPWS_T .')             #alleen de 6 waarden voor de '.'
    g=re.split(' ',g,12)
    print(g)
    g=g[0]+","+g[1].lstrip('ABCDEFXYZRPW')+","+g[2].lstrip('ABCDEFXYZRPW')+","+g[3].lstrip('ABCDEFXYZRPW')+","+g[4].lstrip('ABCDEFXYZRPW')+","+g[5].lstrip('ABCDEFXYZRPW') #+">"+g[6]
    return g

def fromRoboDK(f):
    global SP
    if "MOVJ" in f:
        g="PTP(\"JPP\"," + zesCoord(f) + "," + str(SP) + ",200,0,false)"      #joint 100%snelheid/200ms tot top not blended
    else: 
        if "MOVL" in f:
            g="PTP(\"CPP\"," + zesCoord(f) + "," + str(SP) + ",200,0,false)"   #Cartesian
        else:
            if "BASE_FRAME" in f:
                g="ChangeBase("+ zesCoord(f) + ")"
            else:
                if "TOOL_FRAME" in f:
                    g="ChangeTCP("+ zesCoord(f) + ")"
                else:
                    g="0"
                    if "SP" in f:
                        SP=int(float(f.lstrip('SP ')))
                        print("SPEED=" + str(SP))
                    if "OUT" in f:
                        ModOut(f)
                        print("g=" +g)
    return g
#voor 3

#voor 4
def chkStr(s):
    result="TMSCT," +  ",1," + s + "," #1=ID//str(len(s)) + moet weg
    return result
def checksum(b):
    result = b[0]
    for i in range(1, len(b)):
        result = result ^ b[i]
    c=result
    #print(c)    
    if (c < 16):
        d=str(hex(c)).upper()
        d="0" +d[-1:]
    else:
        d=str(hex(c).upper())
        d=d[-2:]
    return d
def packetSender(s):
    h=chkStr(s)
    b=bytearray(h,'utf-8')
    d=checksum(b)
    result="$" + h + "*" + d + "\r\n"
    return result    
#voor 4
#voor modbusconnectie
SP=100 #speed
HOST = input('Geef IP adres: ') #robot
PORT=5890
#PORT = int(input('Geef port: ')) #test
#HOST='127.0.0.1' #5890
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
try:
    s.bind((HOST, PORT))
except socket.error as e:
    print(str(e))
s.connect((HOST, PORT))
print("connected")
#voor modbusconnectie

# construct the argument parse and parse the arguments
###ap = argparse.ArgumentParser()
###ap.add_argument("-i", "--image", required=True,
###	help="path to input image")
###ap.add_argument("-y", "--yolo", required=True,
###	help="base path to YOLO directory")
###ap.add_argument("-c", "--confidence", type=float, default=0.5,
###	help="minimum probability to filter weak detections")
###ap.add_argument("-t", "--threshold", type=float, default=0.3,
###	help="threshold when applyong non-maxima suppression")
###args = vars(ap.parse_args())

#######robot referentiepositie
robot = RDK.Item('', ITEM_TYPE_ROBOT)
target_ref = robot.Pose()
pos_ref = target_ref.Pos()
print("move to array of points")
print(Pose_2_TxyzRxyz(target_ref))
# It is important to provide the reference frame and the tool frames when generating programs offline
robot.setPoseFrame(robot.PoseFrame())
robot.setPoseTool(robot.PoseTool())
robot.setZoneData(10) # Set the rounding parameter (Also known as: CNT, APO/C_DIS, ZoneData, Blending radius, cornering, ...)
robot.setSpeed(200) # Set linear speed in mm/s
target_i = Mat(target_ref)
pos_i = target_i.Pos()
target_i.setPos(pos_i)
robot.MoveL(target_i)
#######robot referentiepositie

# load the COCO class labels our YOLO model was trained on
###labelsPath = os.path.sep.join([args["yolo"], "coco.names"])
labelsPath = r"C:\Users\Public\Documents\yolo-object-detection\yolo-object-detection\yolo-coco\coco.names"

LABELS = open(labelsPath).read().strip().split("\n")

# initialize a list of colors to represent each possible class label
np.random.seed(42)
COLORS = np.random.randint(0, 255, size=(len(LABELS), 3),
	dtype="uint8")

# derive the paths to the YOLO weights and model configuration
###weightsPath = os.path.sep.join([args["yolo"], "yolov3.weights"])
###configPath = os.path.sep.join([args["yolo"], "yolov3.cfg"])
weightsPath = r"C:\Users\Public\Documents\yolo-object-detection\yolo-object-detection\yolo-coco\yolov3.weights"
configPath = r"C:\Users\Public\Documents\yolo-object-detection\yolo-object-detection\yolo-coco\yolov3.cfg"

# load our YOLO object detector trained on COCO dataset (80 classes)
print("[INFO] loading YOLO from disk...")
net = cv2.dnn.readNetFromDarknet(configPath, weightsPath)

# load our input image and grab its spatial dimensions
###image = cv2.imread(args["image"])
#key = cv2. waitKey(1)
webcam = cv2.VideoCapture(1)
pause(1)
i=1 
while True:
	try:
		check, image = webcam.read()
		print(check) #prints true as long as the webcam is running
		#print(image) #prints matrix values of each framecd 
		cv2.imshow("Capturing", image)
		(H, W) = image.shape[:2]
		ln = net.getLayerNames()
		ln = [ln[i[0] - 1] for i in net.getUnconnectedOutLayers()]
		# construct a blob from the input image and then perform a forward
		# pass of the YOLO object detector, giving us our bounding boxes and
		# associated probabilities
		blob = cv2.dnn.blobFromImage(image, 1 / 255.0, (416, 416),
			swapRB=True, crop=False)
		net.setInput(blob)
		start = time.time()
		layerOutputs = net.forward(ln)
		end = time.time()
		# show timing information on YOLO
		print("[INFO] YOLO took {:.6f} seconds".format(end - start))
		# initialize our lists of detected bounding boxes, confidences, and
		# class IDs, respectively
		boxes = []
		confidences = []
		classIDs = []
		# loop over each of the layer outputs
		for output in layerOutputs:
			# loop over each of the detections
			for detection in output:
				# extract the class ID and confidence (i.e., probability) of
				# the current object detection
				scores = detection[5:]
				classID = np.argmax(scores)
				confidence = scores[classID]
				# filter out weak predictions by ensuring the detected
				# probability is greater than the minimum probability
				if confidence > 0.5: ##args["confidence"]: is eigenlijk variabele
					# scale the bounding box coordinates back relative to the
					# size of the image, keeping in mind that YOLO actually
					# returns the center (x, y)-coordinates of the bounding
					# box followed by the boxes' width and height
					box = detection[0:4] * np.array([W, H, W, H])
					(centerX, centerY, width, height) = box.astype("int")
					# use the center (x, y)-coordinates to derive the top and
					# and left corner of the bounding box
					x = int(centerX - (width / 2))
					y = int(centerY - (height / 2))
					# update our list of bounding box coordinates, confidences,
					# and class IDs
					boxes.append([x, y, int(width), int(height)])
					confidences.append(float(confidence))
					classIDs.append(classID)
		if LABELS[classIDs[classID]] == "apple":
			print("appel")
			pos_i[0]=-200 # 30 mm in z
			print("x_midden: ",centerX,"y_midden: ",centerY, "afm: ",width)
			modbusclient.write_single_register(9000,1)
		if LABELS[classIDs[classID]] == "banana":
			print("banaan")
			pos_i[0]=200 # 30 mm in z
			print("x_midden: ",centerX,"y_midden: ",centerY, "afm: ",width)
			modbusclient.write_single_register(9000,2)
		if LABELS[classIDs[classID]] == "orange":
			print("sinasappel")
			pos_i[0]=0 # 30 mm in z
			print("x_midden: ",centerX,"y_midden: ",centerY, "afm: ",width)	
			modbusclient.write_single_register(9000,3)
		while not "OK" in data.decode():
                    ##########zesCoord hier x,y,z,a,b,c postie fruit?????????????       
                    f=0.5*centerX+100,0.5*centerY+100,0.5*width+100,0,90,0 #0.5 is schaal 100 verschuiving
                    g="PTP(\"CPP\"," + zesCoord(f) + "," + str(SP) + ",200,0,false)"   #Cartesian
                    h=packetSender(g)     #4verstuur de omgezette opdracht uit bestand
                    s.send(h.encode())
                    print(h)
                    data = s.recv(1024)           #antwoord als OK erin dan volgende opdracht
                    print('Received', repr(data))
                    stap=stap+1
                    print(stap)
                    time.sleep(1)                 #5anders herhalen na 1 s tot einde bestand 	
                    #########voor versturen tijdens listen (tot OK)
                    print(LABELS[classIDs[classID]])
                    target_i.setPos(pos_i)
                    robot.MoveL(target_i)
                    # apply non-maxima suppression to suppress weak, overlapping bounding
                    # boxes
                    ###idxs = cv2.dnn.NMSBoxes(boxes, confidences, args["confidence"],
                    ###	args["threshold"])
                    idxs = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.3)
                    #ensure at least one detection exists
                    if len(idxs) > 0:
                        # loop over the indexes we are keeping
                        for i in idxs.flatten():
                            # extract the bounding box coordinates
                            (x, y) = (boxes[i][0], boxes[i][1])
                            (w, h) = (boxes[i][2], boxes[i][3])
                            # draw a bounding box rectangle and label on the image
                            color = [int(c) for c in COLORS[classIDs[i]]]
                            cv2.rectangle(image, (x, y), (x + w, y + h), color, 2)
                            text = "{}: {:.4f}".format(LABELS[classIDs[i]], confidences[i])
                            cv2.putText(image, text, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX,
                            0.5, color, 2)
		cv2.imshow("Capturing",image)
	except(KeyboardInterrupt):
		print(" off")
	# determine only the *output* layer names that we need from YOLO
	key = cv2.waitKey(0)
	if key == ord('q'):
		print("end") 
		#cv2.imwrite(filename='saved_img.jpg', img=frame)
		webcam.release()
        
