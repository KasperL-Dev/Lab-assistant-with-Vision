import os
import socket
import fileinput
import time
import re
from EasyModbusPy.modbusClient import ModbusClient   #pip install easymodbus
import struct
prev = [0, 0, 0, 0, 0, 0]

SP=100 #speed    
HOST='192.168.0.1'  #voorwaarde dat dit IP adres ingesteld is op de robot, dat se PC een vast IP-adres met alleen het laatse getal ander heeft, en dat de cobot opstart verbonden met de PC
#HOST = input('Geef IP adres: ') #Als er een wisselend adres is, bij opstart programma met modbusdevice/listen blok wordt het adres van de cobot gegeven in de comments
PORT=5890
#PORT = int(input('Geef port: ')) 
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
#try:
#    s.bind((HOST, PORT))
#except socket.error as e:
#    print(str(e))

s.connect((HOST, PORT))
#voor modbusconnectie
modbusclient = ModbusClient(HOST, 502)   #zelfde IP-adres, poort 502
modbusclient.connect()
holdingRegisters = modbusclient.read_holdingregisters(9000,2)#vreemd maar nodig
print("connected")
#print("Op dit moment veranderen chkStr(self,s): aanpassen als versie 1.68 op de cobbot (RDM)")
def is_number(s):
        try:
            float(s)
            return True
        except ValueError:
            return False
def boolList2String(lst):
    return ''.join(['1' if x else '0' for x in lst])  
class cobotconnect():
    def floater(self,x,y):
        t = (x,y) #31544,16632 => 7.765041351318359, 56191,49724 => -47.214351654052734
        packed_string = struct.pack("HH", *t)
        unpacked_float = struct.unpack("f", packed_string)[0]
        #print (unpacked_float)
        return unpacked_float
    #NB convert_registers_to_float(registers) en omgekeerde in easymodbus module """
    def DeleteBuffer(self):
        g = "StopAndClearBuffer()"

        data = b'xx'
        #stap = 0
        while not "OK" in data.decode():
            h = self.packetSender(g)  # 4verstuur de omgezette opdracht uit bestand
            s.send(h.encode())
            print(h)
            data = s.recv(64)  # antwoord als OK erin dan volgende opdracht
            # data = s.recv(1024)           #antwoord als OK erin dan volgende opdracht
            print('Received', repr(data))
            # stap = stap + 1  # bijhouden aantal pogingen
            # print(stap)
            time.sleep(0.1)  # 5anders herhalen na 1 s tot einde bestand
    def RunProg(self,progr):
        print(progr+'.prg')
        for line in fileinput.input(files=(progr+'.prg')): 
            pstxt=line[:-1]
            print(pstxt)
            self.sendCobotPos(pstxt)
            #elif (robo==1):
            #    rdk.sendCobotPos(pstxt)        
            time.sleep(1)                 #herhalen na 1 s
        fileinput.close()
        print("Finished")
    def DeleteBuffer(self):
        g = "StopAndClearBuffer()"

        data = b'xx'
        #stap = 0
        while not "OK" in data.decode():
            h = self.packetSender(g)  # 4verstuur de omgezette opdracht uit bestand
            s.send(h.encode())
            print(h)
            data = s.recv(64)  # antwoord als OK erin dan volgende opdracht
            # data = s.recv(1024)           #antwoord als OK erin dan volgende opdracht
            print('Received', repr(data))
            # stap = stap + 1  # bijhouden aantal pogingen
            # print(stap)
            time.sleep(0.1)  # 5anders herhalen na 1 s tot einde bestand
    def sendCobMove(self, arr_move, SP):
        if arr_move != prev:
            prev == arr_move

            for i in range(6):
                arr_move[i] = round(arr_move[i], 2)
                arr_move[i] = str(arr_move[i])
            [x, y, z, rx, ry, rz] = arr_move
            #print(arr_move)

            g="Move_PTP(\"TPP\"," + x + "," + y + "," + z + "," + rx + "," + ry + "," + rz + "," + str(SP) + ",500,100,true)"   #Cartesian

            data = b'xx'
            #stap = 0
            #while not "OK" in data.decode():
            h = self.packetSender(g)  # 4verstuur de omgezette opdracht uit bestand
            s.send(h.encode())
            print(h)
            data = s.recv(64)  # antwoord als OK erin dan volgende opdracht
            #data = s.recv(1024)           #antwoord als OK erin dan volgende opdracht
            print('Received', repr(data))
            #stap = stap + 1  # bijhouden aantal pogingen
            #print(stap)
            time.sleep(0.1)  # 5anders herhalen na 1 s tot einde bestand
    def sendCobotMove(self, pstxt, SP=50):
        g="Move_PTP(\"TPP\"," + pstxt + "," + str(SP) + ",200,0,false)"   # 500,100,true
        data = b'xx'
        #stap = 0
        #while not "OK" in data.decode():
        h = self.packetSender(g)  # 4verstuur de omgezette opdracht uit bestand
        s.send(h.encode())
        print(h)
        data = s.recv(64)  # antwoord als OK erin dan volgende opdracht
        #data = s.recv(1024)           #antwoord als OK erin dan volgende opdracht
        print('Received', repr(data))
        #stap = stap + 1  # bijhouden aantal pogingen
        #print(stap)
        time.sleep(0.1)  # 5anders herhalen na 1 s tot einde bestand
    def sendCobotPos(self,pstxt,SP=50):
        #############zenden naar cobot tot antwoord met "OK" terugontvangen, nodig als niet altijd in listen mode 
        ps=pstxt.split(",")
        g='0'
        if (is_number(ps[0])):
            g="PTP(\"CPP\"," + pstxt + "," + str(SP) + ",200,0,false)"   #Cartesian
        else:
            g=self.fromRoboDK(pstxt)
        if (g!='0'): 
            data=b'xx'
            #stap=0
            #while not "OK" in data.decode():
            h=self.packetSender(g)     #4verstuur de omgezette opdracht uit bestand
            s.send(h.encode())
            print(h)
            data = s.recv(64)           #antwoord als OK erin dan volgende opdracht
            #data = s.recv(1024)           #antwoord als OK erin dan volgende opdracht
            print('Received', repr(data))
            #    stap=stap+1   #bijhouden aantal pogingen
            #    print(stap)
            time.sleep(0.1)                 #anders herhalen na 1 s tot einde bestand
    def sendCobotJoint(self,pstxt,SP=50):
        #############zenden naar cobot tot antwoord met "OK" terugontvangen, nodig als niet altijd in listen mode 
            g="PTP(\"JPP\"," + pstxt + "," + str(SP) + ",200,0,false)"   #Cartesian
            data=b'xx'
            #stap=0
            #print(g)
            #while not "OK" in data.decode():
            h=self.packetSender(g)     #4verstuur de omgezette opdracht uit bestand
            s.send(h.encode())
            print(h)
            data = s.recv(64)           #antwoord als OK erin dan volgende opdracht
            #data = s.recv(1024)           #antwoord als OK erin dan volgende opdracht
            print('Received', repr(data))
            #    stap=stap+1   #bijhouden aantal pogingen
            #    print(stap)
            time.sleep(0.1)                 #anders herhalen na 1 s tot einde bestand
    #voor 3
    def waitCobotPos(self,pstxt,SP=50):
        self.sendCobotPos(pstxt)
        Q=[0.0,0.0,0.0,0.0,0.0,0.0]
        N=pstxt.split(',')
        Q[0]=float(N[0])
        Q[1]=float(N[1])
        Q[2]=float(N[2])
        Q[3]=float(N[3])
        Q[4]=float(N[4])
        Q[5]=float(N[5])
        #print(Q[2])
        while True:
            P=self.readPos()
            #print(P[0]-Q[0],',',P[1]-Q[1],',',P[2]-Q[2],',',P[3]-Q[3],',',P[4]-Q[4],',',P[5]-Q[5])
            if ((abs(P[0]-Q[0]) < 1.0) and (abs(P[1]-Q[1]) < 1.0) and (abs(P[2]-Q[2]) < 1.0) and ((abs(P[3]-Q[3]) < 1.0) or (abs(P[3]-Q[3]) > 359.0)) and ((abs(P[4]-Q[4]) < 1.0) or (abs(P[4]-Q[4]) > 359.0)) and ((abs(P[5]-Q[5]) < 1.0) or (abs(P[5]-Q[5]) > 359.0))):
                break  #NB ook hoek maar dan opletten -180/180
    def waitCobotJoint(self,pstxt,SP=50):
        self.sendCobotJoint(pstxt)
        Q=[0.0,0.0,0.0,0.0,0.0,0.0]
        N=pstxt.split(',')
        Q[0]=float(N[0])
        Q[1]=float(N[1])
        Q[2]=float(N[2])
        Q[3]=float(N[3])
        Q[4]=float(N[4])
        Q[5]=float(N[5])
        #print(Q[2])
        while True:
            P=self.readJoints()
            print(P)
            print(P[5]," ",Q[5])
            #print(P[0]-Q[0],',',P[1]-Q[1],',',P[2]-Q[2],',',P[3]-Q[3],',',P[4]-Q[4],',',P[5]-Q[5])
            if (((abs(P[0]-Q[0]) < 1.0) or (abs(P[0]-Q[0]) > 359.0)) and ((abs(P[1]-Q[1]) < 1.0) or (abs(P[1]-Q[1]) > 359.0)) and ((abs(P[2]-Q[2]) < 1.0) or (abs(P[2]-Q[2]) > 359.0)) and ((abs(P[3]-Q[3]) > 359.0) or (abs(P[3]-Q[3]) < 1.0)) and ((abs(P[4]-Q[4]) > 359.0) or (abs(P[4]-Q[4]) < 1.0)) and ((abs(P[5]-Q[5]) < 1.0) or (abs(P[5]-Q[5]) > 359.0))):
                break  #NB ook hoek maar dan opletten -180/180
    def stopListen(self):
        h = self.packetSender("ScriptExit()")
        s.send(h.encode())
        print(h)
    def Pause(self):
        h = self.packetSender("Pause()")
        s.send(h.encode())
        print(h)
    def Resume(self):
        h = self.packetSender("Resume()")
        s.send(h.encode())
        print(h)
    def Reset(self):
        h = self.packetSender("Reset()")
        s.send(h.encode())
        print(h)
        
    def ModReg(self,reg,val):
        modbusclient.write_single_register(reg, val)
    def ModRegRead(self,reg):
        val = modbusclient.read_holdingregisters(reg,1)    # (7001,2)
        print (val)
        #inputRegisters = modbusclient.read_inputregisters(7001, 2)
        #print("Read Multiple Registers")
        #print(inputRegisters)
        #print(float(65536*inputRegisters[0]+inputRegisters[1]))val=modbusclient.read_single_register(reg,1)
        return val
    def ModOut(self,s):
        coil=int(s[4])  
        if (s[7]=='T'):
            waarde=1
        else:
            waarde=0
        #Write a single coil to the Server – Coil number “1”
        print("write coil: " + str(coil) + ", waarde: " + str(waarde))
        modbusclient.write_single_coil(coil,waarde) #of moet True/False?
        #doet het maar staat daarna vast
        #print("g=" +g)
        return
    #niet nodig als coordinaten al apart
    def O_out(self,coil,waarde):
        print("write D0" + str(coil) + "="+ str(waarde))
        modbusclient.write_single_coil(coil,waarde) 
        #print("READY")
        #modbusclient.write_single_coil(coil,waarde) 
        time.sleep(0.1)  ###wachttij nodig anders vastlopen (kan vast wel sneller)
    def All_O_in(self):
        waarde=modbusclient.read_coils(0,16) #NB nog 4 bij adres 800 (DOE)
        strWaarde=boolList2String(waarde) 
        waarde=modbusclient.read_coils(800,4) #NB nog 4 bij adres 800 (DOE)
        strWaarde=strWaarde + "DOE" + boolList2String(waarde) 
        print("DO_all=" ,strWaarde)
        return strWaarde 
    def O_in(self,coil):
        waarde=modbusclient.read_coils(coil,1) 
        print("read DO" + str(coil),"=",waarde)
        #print("READY")
        #modbusclient.read_single_coil(coil,waarde) 
        time.sleep(0.1)  ###wachttij nodig anders vastlopen (kan vast wel sneller)            
        return waarde
    def All_I_in(self):
        waarde=modbusclient.read_discreteinputs(0,16)
        strWaarde=boolList2String(waarde) 
        print("DI_all=" ,strWaarde)
        return strWaarde 
    def I_in(self,coil):
        waarde=modbusclient.read_discreteinputs(coil,1) 
        print("read DI" + str(coil),"=",waarde)
        #print("READY")
        #modbusclient.read_single_coil(coil,waarde) 
        time.sleep(0.1)  ###wachttij nodig anders vastlopen (kan vast wel sneller)            
        return waarde
    def readTorque(self):
        T=[0.0,0.0,0.0,0.0,0.0,0.0]
        inputRegisters = modbusclient.read_inputregisters(7901, 2)
        T[0]=self.floater(inputRegisters[1],inputRegisters[0]) #x
        inputRegisters = modbusclient.read_inputregisters(7903, 2)
        T[1]=self.floater(inputRegisters[1],inputRegisters[0]) #y
        inputRegisters = modbusclient.read_inputregisters(7905, 2)
        T[2]=self.floater(inputRegisters[1],inputRegisters[0])#z
        inputRegisters = modbusclient.read_inputregisters(7907, 2)
        T[3]=self.floater(inputRegisters[1],inputRegisters[0]) #a in grd
        inputRegisters = modbusclient.read_inputregisters(7909, 2)
        T[4]=self.floater(inputRegisters[1],inputRegisters[0]) #b in grd
        inputRegisters = modbusclient.read_inputregisters(7911, 2)
        T[5]=self.floater(inputRegisters[1],inputRegisters[0]) #c in grd
        return T
    def readPos(self):
        P=[0.0,0.0,0.0,0.0,0.0,0.0]
        inputRegisters = modbusclient.read_inputregisters(7001, 2)
        P[0]=self.floater(inputRegisters[1],inputRegisters[0]) #x
        inputRegisters = modbusclient.read_inputregisters(7003, 2)
        P[1]=self.floater(inputRegisters[1],inputRegisters[0]) #y
        inputRegisters = modbusclient.read_inputregisters(7005, 2)
        P[2]=self.floater(inputRegisters[1],inputRegisters[0])#z
        inputRegisters = modbusclient.read_inputregisters(7007, 2)
        P[3]=self.floater(inputRegisters[1],inputRegisters[0]) #a in grd
        inputRegisters = modbusclient.read_inputregisters(7009, 2)
        P[4]=self.floater(inputRegisters[1],inputRegisters[0]) #b in grd
        inputRegisters = modbusclient.read_inputregisters(7011, 2)
        P[5]=self.floater(inputRegisters[1],inputRegisters[0]) #c in grd
        return P
    def stop(self):
        s.close() #detach()
    def readError(self):
        inputRegisters = modbusclient.read_inputregisters(7332, 1)
        errCode=inputRegisters[0]
        #print("foutcode ", errCode)
        switcher = {
            1: "Solid Red, fatal error.",
            3: "Solid Blue, standby in Auto Mode.",
            4: "Flashing Blue, project running in Auto Mode.",
            5: "Solid Green, standby in Manual Mode.",
            6: "Flashing Green, project running in Manual Mode.",
            9: "Alternating Blue&Red, Auto Mode error.",
            10: "Alternating Green&Red, Manual Mode error.",
            15: "Light Blue, safe activation mode.",
            18: "Flashing Green(9), project pause in Manual Mode.",
            19: "Flashing Blue(9), project pause in Auto Mode."
        }
        strerror=switcher.get(errCode, "No error")
        return strerror    
    def zesCoord(self,g):#niet nodig als coordinaten al apart
        g=g.lstrip('MOVJPLABCDEFXYZRPWS_T .')             #alleen de 6 waarden voor de '.'
        g=re.split(' ',g,12)
        print(g)
        g=g[0]+","+g[1].lstrip('ABCDEFXYZRPW')+","+g[2].lstrip('ABCDEFXYZRPW')+","+g[3].lstrip('ABCDEFXYZRPW')+","+g[4].lstrip('ABCDEFXYZRPW')+","+g[5].lstrip('ABCDEFXYZRPW') #+">"+g[6]
        return g
    def fromRoboDK(self,f):
        global SP
        if "MOVJ" in f:
            g="PTP(\"JPP\"," + self.zesCoord(f) + "," + str(SP) + ",200,0,false)"      #joint 100%snelheid/200ms tot top not blended
        else: 
            if "MOVL" in f:
                g="PTP(\"CPP\"," + self.zesCoord(f) + "," + str(SP) + ",200,0,false)"   #Cartesian
            else:
                if "BASE_FRAME" in f:
                    g="ChangeBase("+ self.zesCoord(f) + ")"
                else:
                    if "TOOL_FRAME" in f:
                        g="ChangeTCP("+ self.zesCoord(f) + ")"
                    else:
                        g="0"
                        if "SP" in f:
                            SP=int(float(f.lstrip('SP ')))
                            print("SPEED=" + str(SP))
                        if "OUT" in f:
                            ModOut(f)
        #print("g=" +g)
        return g
    #voor 3

    #voor 4
    def chkStr(self,s):
        #result="TMSCT," +  ",1," + s + "," #of ID=2?//str(len(s)) + 2 moet weg bij versie 1.68
        #result="TMSCT," + str(len(s)+2) + ",2," + s + "," #str(len(s)) + 2 nodig voor versie 1.76
        result = "TMSCT," + str(len(s)+2) + ",3," + s + ","
        return result
    def checksum(self,b):
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
    def packetSender(self,s):
        h=self.chkStr(s)
        b=bytearray(h,'utf-8')
        d=self.checksum(b)
        result="$" + h + "*" + d + "\r\n"
        return result
if __name__ == '__main__':
    cob = cobotconnect()
    print(cob.readPos())
