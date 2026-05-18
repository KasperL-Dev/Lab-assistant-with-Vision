#https://gist.github.com/bradmontgomery/2219997
#JSON server program
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import time
import sys
import numpy as np
import cv2
from PIL import Image
import datetime
#from ultralytics import YOLO
#import supervision as sv
import os

hostName = "192.168.0.10"  ###IP adres van de Eigen PC (staat ook in External Detextion)
hostPort = 6189

def send():
    x2 = { "annotations" : [ { "box_cx" : 0, "box_cy" : 0, "box_h" : 0, "box_w" : 0, "label" : "picture taken", "rotation" : 0, "score" : 1.0 } ], "message" : "success" }
    #x2 = { "annotations" : [ { "box_cx" : 550, "box_cy" : 550, "box_h" : 100, "box_w" : 100, "label" : "car", "rotation" : 0, "score" : 1.0 } ], "message" : "success" }
    msg=json.dumps(x2)
    print(msg)
    return msg
def foto():
    ##############voorbeeld om iets met foto te doen
    time.sleep(1) ##zeker weten dat foto gesaved
    img=Image.open("c:\\users\\public\\foto.png").convert('RGB')
    cvImg=np.array(img)
    cvImg=cvImg[:, :, ::-1].copy()
    cv2.imshow("voorbeeld",cvImg)
    cv2.waitKey(1)
    ###hierna xF, yF bepaald uit foto
    #stel xF=600 yF=-400 gevonden
    xF=200
    yF=100
    x0=600  #robot coordinaten onderhoek
    y0=-400
    schaal= 0.2 #mm/pixel (afhankelijk van resolutie en hoogte camera)
    x=x0+xF*schaal
    y=y0+yF*schaal
    return x,y
    
def listen():
    global cob
    ##############voorbeeld om iets met foto te doen
    x,y=foto()
    ###voorbeeld acties met beweging
    P=cob.readPos() 
    print("De huidige positie is x,y,z,a,b,c= ",P[0],P[1],P[2],P[3],P[4],P[5])
    positie=str(x)+ ','+ str(y) + ','+ "350,0,180,90"
    print(positie)
    cob.sendCobotPos(positie,100)  #speed is 100% van de waarde ingesteld op de robot.
    time.sleep(2)
    cob.stopListen()

def make_png(post_data):
    dt = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    #dtype = np.dtype('uint8')#('B')
    #try:
    numpy_data = bytearray(post_data)
    dt = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    nx=bytearray(numpy_data) 
    i=0
    j=0
    x=0
    start=0
    finish=0
    while(finish==0):
        if (x==0) and (numpy_data[i]==137):
            j=i
            start=1
        if ((x>0) and (numpy_data[i]==66)) and ((numpy_data[i+1]==96) and (numpy_data[i+2]==130)):
            nx[x]=66
            nx[x+1]=96
            nx[x+2]=130
            start=0
            finish=1
            numpy_d=nx[0:x+2]
            ####als de foto's bewaard moeten blijven
            #filenaam='C:\\Users\\Public\\Pictures\\' + dt + '.png' ######Public eventueel  vervangen door eigen naam
            ###als steeds dezelfde foto gebruikt
            #filenaam="c:\\users\\public\\foto.png"
            filenaam="foto.png"
            
            print(filenaam, "gesaved")
            with open(filenaam, 'wb') as f2:  #w =overwrite file if exists b=binair
                f2.write(numpy_d) 
            f2.close()
            time.sleep(1.0)#1 seconde voor saven file
            #sys.exit()    
        if (start==1):
            nx[x]=numpy_data[j+x]
            #print(nx[x])
            x+=1  # tot 137 wegfilteren
        i+=1  
    print(j)
    print(x+2)
    #except IOError:
    #    print('Error While Opening the file!')

class MyServer(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
#   POST is for submitting data.
    def do_POST(self):
        global teller
        print( "incomming http: ", self.path )
        self._set_headers()
        #parsed_path = urlparse(self.path)
        #request_id = parsed_path.path
        content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
        post_data = self.rfile.read(content_length) # <--- Gets the data itself
        make_png(post_data) ########################antwoord sturen kan afhankelijk (positie/voorwerp)
        self.send_response(200)
        self.wfile.write(send().encode())
        time.sleep(1)
        listen()##########hier de procedure aanroepen voor het interpreteren van de foto en het doen van de bewegingen (eventueel meerder functies)
        
 
def main():
    global cob
    from EasyModbusPy.cobotconnect19216801 import cobotconnect #voorwaarde verbinding met cobot
    cob=cobotconnect()
    cob.stopListen()
    #print("test")
    myServer = HTTPServer((hostName, hostPort), MyServer)
    print(time.asctime(), "Server Starts - %s:%s" % (hostName, hostPort))
    try:
        myServer.serve_forever() #als er een foto gestuurd is door VISION/ExternalDetection wordt doPOST() aangeroepen
    except KeyboardInterrupt:
        print("server stopt")
    myServer.server_close()
    print(time.asctime(), "Server Stops - %s:%s" % (hostName, hostPort))
if __name__ == '__main__':  
    main()
