import os
import socket
import fileinput
import time
import re
from easymodbus.modbus_client import ModbusClient
import struct

SP   = 100
prev = [0, 0, 0, 0, 0, 0]

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def boolList2String(lst):
    return ''.join(['1' if x else '0' for x in lst])


class cobotconnect():

    def __init__(self, host='192.168.0.1', port=5890):
        global s, modbusclient
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        modbusclient = ModbusClient(host, 502)
        modbusclient.connect()
        modbusclient.read_holdingregisters(9000, 2)
        print("connected to", host)

    def floater(self, x, y):
        t = (x, y)
        packed_string = struct.pack("HH", *t)
        unpacked_float = struct.unpack("f", packed_string)[0]
        return unpacked_float

    def DeleteBuffer(self):
        g = "StopAndClearBuffer()"
        data = b'xx'
        while not "OK" in data.decode():
            h = self.packetSender(g)
            s.send(h.encode())
            print(h)
            data = s.recv(64)
            print('Received', repr(data))
            time.sleep(0.1)

    def RunProg(self, progr):
        print(progr + '.prg')
        for line in fileinput.input(files=(progr + '.prg')):
            pstxt = line[:-1]
            print(pstxt)
            self.sendCobotPos(pstxt)
            time.sleep(1)
        fileinput.close()
        print("Finished")

    def sendCobMove(self, arr_move, SP):
        if arr_move != prev:
            prev == arr_move
            for i in range(6):
                arr_move[i] = round(arr_move[i], 2)
                arr_move[i] = str(arr_move[i])
            [x, y, z, rx, ry, rz] = arr_move
            g = "Move_PTP(\"TPP\"," + x + "," + y + "," + z + "," + rx + "," + ry + "," + rz + "," + str(SP) + ",500,100,true)"
            data = b'xx'
            h = self.packetSender(g)
            s.send(h.encode())
            print(h)
            data = s.recv(64)
            print('Received', repr(data))
            time.sleep(0.1)

    def sendCobotMove(self, pstxt, SP=50):
        g = "Move_PTP(\"TPP\"," + pstxt + "," + str(SP) + ",200,0,false)"
        data = b'xx'
        h = self.packetSender(g)
        s.send(h.encode())
        print(h)
        data = s.recv(64)
        print('Received', repr(data))
        time.sleep(0.1)

    def sendCobotPos(self, pstxt, SP=50):
        ps = pstxt.split(",")
        g = '0'
        if is_number(ps[0]):
            g = "PTP(\"CPP\"," + pstxt + "," + str(SP) + ",200,0,false)"
        else:
            g = self.fromRoboDK(pstxt)
        if g != '0':
            data = b'xx'
            h = self.packetSender(g)
            s.send(h.encode())
            print(h)
            data = s.recv(64)
            print('Received', repr(data))
            time.sleep(0.1)

    def sendCobotJoint(self, pstxt, SP=50):
        g = "PTP(\"JPP\"," + pstxt + "," + str(SP) + ",200,0,false)"
        data = b'xx'
        h = self.packetSender(g)
        s.send(h.encode())
        print(h)
        data = s.recv(64)
        print('Received', repr(data))
        time.sleep(0.1)

    def waitCobotPos(self, pstxt, SP=50):
        self.sendCobotPos(pstxt)
        Q = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        N = pstxt.split(',')
        for i in range(6):
            Q[i] = float(N[i])
        while True:
            P = self.readPos()
            if ((abs(P[0]-Q[0]) < 1.0) and (abs(P[1]-Q[1]) < 1.0) and (abs(P[2]-Q[2]) < 1.0) and
               ((abs(P[3]-Q[3]) < 1.0) or (abs(P[3]-Q[3]) > 359.0)) and
               ((abs(P[4]-Q[4]) < 1.0) or (abs(P[4]-Q[4]) > 359.0)) and
               ((abs(P[5]-Q[5]) < 1.0) or (abs(P[5]-Q[5]) > 359.0))):
                break

    def waitCobotJoint(self, pstxt, SP=50):
        self.sendCobotJoint(pstxt)
        Q = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        N = pstxt.split(',')
        for i in range(6):
            Q[i] = float(N[i])
        while True:
            P = self.readJoints()
            print(P)
            if (((abs(P[0]-Q[0]) < 1.0) or (abs(P[0]-Q[0]) > 359.0)) and
               ((abs(P[1]-Q[1]) < 1.0) or (abs(P[1]-Q[1]) > 359.0)) and
               ((abs(P[2]-Q[2]) < 1.0) or (abs(P[2]-Q[2]) > 359.0)) and
               ((abs(P[3]-Q[3]) < 1.0) or (abs(P[3]-Q[3]) > 359.0)) and
               ((abs(P[4]-Q[4]) < 1.0) or (abs(P[4]-Q[4]) > 359.0)) and
               ((abs(P[5]-Q[5]) < 1.0) or (abs(P[5]-Q[5]) > 359.0))):
                break

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

    def ModReg(self, reg, val):
        modbusclient.write_single_register(reg, val)

    def ModRegRead(self, reg):
        val = modbusclient.read_holdingregisters(reg, 1)
        print(val)
        return val

    def ModOut(self, s):
        coil = int(s[4])
        waarde = 1 if s[7] == 'T' else 0
        print("write coil: " + str(coil) + ", waarde: " + str(waarde))
        modbusclient.write_single_coil(coil, waarde)

    def O_out(self, coil, waarde):
        print("write D0" + str(coil) + "=" + str(waarde))
        modbusclient.write_single_coil(coil, waarde)
        time.sleep(0.1)

    def All_O_in(self):
        waarde = modbusclient.read_coils(0, 16)
        strWaarde = boolList2String(waarde)
        waarde = modbusclient.read_coils(800, 4)
        strWaarde = strWaarde + "DOE" + boolList2String(waarde)
        print("DO_all=", strWaarde)
        return strWaarde

    def O_in(self, coil):
        waarde = modbusclient.read_coils(coil, 1)
        print("read DO" + str(coil), "=", waarde)
        time.sleep(0.1)
        return waarde

    def All_I_in(self):
        waarde = modbusclient.read_discreteinputs(0, 16)
        strWaarde = boolList2String(waarde)
        print("DI_all=", strWaarde)
        return strWaarde

    def I_in(self, coil):
        waarde = modbusclient.read_discreteinputs(coil, 1)
        print("read DI" + str(coil), "=", waarde)
        time.sleep(0.1)
        return waarde

    def readTorque(self):
        T = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        for i, reg in enumerate([7901, 7903, 7905, 7907, 7909, 7911]):
            r = modbusclient.read_inputregisters(reg, 2)
            T[i] = self.floater(r[1], r[0])
        return T

    def readPos(self):
        P = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        for i, reg in enumerate([7001, 7003, 7005, 7007, 7009, 7011]):
            r = modbusclient.read_inputregisters(reg, 2)
            P[i] = self.floater(r[1], r[0])
        return P

    def stop(self):
        s.close()

    def readError(self):
        inputRegisters = modbusclient.read_inputregisters(7332, 1)
        errCode = inputRegisters[0]
        switcher = {
            1:  "Solid Red, fatal error.",
            3:  "Solid Blue, standby in Auto Mode.",
            4:  "Flashing Blue, project running in Auto Mode.",
            5:  "Solid Green, standby in Manual Mode.",
            6:  "Flashing Green, project running in Manual Mode.",
            9:  "Alternating Blue&Red, Auto Mode error.",
            10: "Alternating Green&Red, Manual Mode error.",
            15: "Light Blue, safe activation mode.",
            18: "Flashing Green(9), project pause in Manual Mode.",
            19: "Flashing Blue(9), project pause in Auto Mode."
        }
        return switcher.get(errCode, "No error")

    def zesCoord(self, g):
        g = g.lstrip('MOVJPLABCDEFXYZRPWS_T .')
        g = re.split(' ', g, 12)
        print(g)
        g = g[0] + "," + g[1].lstrip('ABCDEFXYZRPW') + "," + g[2].lstrip('ABCDEFXYZRPW') + "," + g[3].lstrip('ABCDEFXYZRPW') + "," + g[4].lstrip('ABCDEFXYZRPW') + "," + g[5].lstrip('ABCDEFXYZRPW')
        return g

    def fromRoboDK(self, f):
        global SP
        if "MOVJ" in f:
            g = "PTP(\"JPP\"," + self.zesCoord(f) + "," + str(SP) + ",200,0,false)"
        elif "MOVL" in f:
            g = "PTP(\"CPP\"," + self.zesCoord(f) + "," + str(SP) + ",200,0,false)"
        elif "BASE_FRAME" in f:
            g = "ChangeBase(" + self.zesCoord(f) + ")"
        elif "TOOL_FRAME" in f:
            g = "ChangeTCP(" + self.zesCoord(f) + ")"
        else:
            g = "0"
            if "SP" in f:
                SP = int(float(f.lstrip('SP ')))
                print("SPEED=" + str(SP))
            if "OUT" in f:
                self.ModOut(f)
        return g

    def chkStr(self, s):
        result = "TMSCT," + str(len(s) + 2) + ",3," + s + ","
        return result

    def checksum(self, b):
        result = b[0]
        for i in range(1, len(b)):
            result = result ^ b[i]
        c = result
        if c < 16:
            d = "0" + str(hex(c))[-1:].upper()
        else:
            d = str(hex(c))[-2:].upper()
        return d

    def packetSender(self, s):
        h = self.chkStr(s)
        b = bytearray(h, 'utf-8')
        d = self.checksum(b)
        result = "$" + h + "*" + d + "\r\n"
        return result


if __name__ == '__main__':
    cob = cobotconnect()
    print(cob.readPos())