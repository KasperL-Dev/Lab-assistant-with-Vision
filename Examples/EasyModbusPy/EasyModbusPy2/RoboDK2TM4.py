#!/usr/bin/env python3

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

#1
stap=0
SP=100
modbusclient = ModbusClient('169.254.220.130', 502)   #('169.254.220.130', 502)
modbusclient.connect()
holdingRegisters = modbusclient.read_holdingregisters(9000,2)#vreemd maar nodig
x=""
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
#2
data=b'xx'
for line in fileinput.input(files=('prog.txt')): 
    print(line[:-1])
    g=fromRoboDK(line[:-1])
    print(g)
    ##modbusclient.write_single_coil(0,0)
    if g!="0":
        while not "OK" in data.decode():       
            h=packetSender(g)     #4verstuur de omgezette opdracht uit bestand
            s.send(h.encode())
            print(h)
            data = s.recv(1024)           #antwoord als OK erin dan volgende opdracht
            print('Received', repr(data))
            stap=stap+1
            print(stap)
            time.sleep(1)                 #5anders herhalen na 1 s tot einde bestand 
    data=b'xx'        
while not "OK" in data.decode():       
    s.send(b'$TMSCT,,1,ScriptExit(),*62\r\n')                        #6 afsluiten
    print("END")
    data = s.recv(1024)           #antwoord als OK erin dan volgende opdracht
    print('Received', repr(data))
    #data=b'xx'
    time.sleep(1)                 #anders herhalen na 1 s
s.close    
