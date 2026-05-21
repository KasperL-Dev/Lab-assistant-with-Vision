#import easymodbus
from easymodbus.modbusClient import ModbusClient
import struct


def floater(x,y):
    t = (x,y) #31544,16632 => 7.765041351318359, 56191,49724 => -47.214351654052734
    packed_string = struct.pack("HH", *t)
    unpacked_float = struct.unpack("f", packed_string)[0]
    #print (unpacked_float)
    return unpacked_float
    #NB convert_registers_to_float(registers) en omgekeerde in easymodbus module

modbusclient = ModbusClient('169.254.220.130', 502)   #('169.254.220.130', 502)
modbusclient.connect()
keuze=""
ilist=[0]
while not "END" in keuze:
    print("1.Read Coils (0=DO0)")
    print("2.Read Inputs")
    print("3.Read Holding Registers (o.a. 9000)")
    print("4.Read Input registers (7001,0=>x-pos)")
    print("5.Write Coil (0=DO0)")
    print("6.Write Single Register (o.a. 9000)")
    print("15.Write Multiple Coils")
    print("16.Write Multiple Registers")
    #print("Lees  2 Registers vanaf 9000")
    holdingRegisters = modbusclient.read_holdingregisters(9000,2)#vreemd maar nodig
    #print (holdingRegisters)

    keuze=input("Geef keuze of END: ")
    if (keuze=="END"):
        modbusclient.close()
    elif (keuze=="1"):
        coil=int(input("Geef 1e coil: "))
        aant=int(input("Geef aantal: "))
        print(modbusclient.read_coils(coil,aant))
    elif (keuze=="2"):
        inp=int(input("Geef 1e 1e input: "))
        aant=int(input("Geef aantal: "))
        discreteInputs = modbusclient.read_discreteinputs(inp, aant)
        #print("Discrete inputs-onduidelijk wat- F02 startaddres,aantal")
        print(discreteInputs)
    elif (keuze=="3"):
        IR=int(input("Geef 1e adres: "))  
        aant=int(input("Geef aantal: "))
        holdingRegisters = modbusclient.read_holdingregisters(IR,aant)
        print (holdingRegisters)
    elif (keuze=="4"):
        IR=int(input("Geef 1e adres: "))
        aant=int(input("Geef aantal (0=tweetal naar float): "))
        if (aant==0): 
        #Read 8 Inputs Registers from Modbus-TCP Server – Server available at Port 502 (IP-Address 190.172.268.100) – Starting Address “1”, Number of Registers to Read: “8” (Notice that the Starting address might be shifted by “1”. In this example we are reading 8 Registers, the first is Register “1” (Addressed with “0”)
            inputRegisters = modbusclient.read_inputregisters(IR, 2)
            print(floater(inputRegisters[1],inputRegisters[0]))
        else:
            inputRegisters = modbusclient.read_inputregisters(IR, aant)
            print(inputRegisters)
    elif (keuze=="5"):
        coil=int(input("Geef coil: "))  
        waarde=int(input("Geef waarde (1/0): "))
        #Write a single coil to the Server – Coil number “1”
        print("write coil: " + str(coil) + ", waarde: " + str(waarde))
        modbusclient.write_single_coil(coil,waarde) #of moet True/False?
    elif (keuze=="6"):
        IR=int(input("Geef adres: "))  
        val=int(input("Geef waarde 0-65536: "))
        #write single register
        print("Register: " + str(IR) + ", schijven: " + str(val))
        modbusclient.write_single_register(IR, val)
    elif (keuze=="15"):
        IR=int(input("Geef 1e coil: "))  
        val=input("Geef waarden 0 1 0,....: ")
        #print("werkt niet met multiple een herhaalopdracht met 5 geprogrammeerd") 
        list  = val.split()
        i=0
        for num in list:
            if (i==0):
                ilist[i]=int(num) #nog aantal in ilist beperken??
            else:
                ilist.append(int(num))
            modbusclient.write_single_coil(IR+i,ilist[i])
            i=i+1
        #modbusclient.write_multiple_coils(IR,ilist)
    elif (keuze=="16"):
        IR=int(input("Geef 1e adres: "))  
        valR=input("Geef waarden 0-65536 0-65536 0-65536 ....: ")
        #print("werkt niet met multiple een herhaalopdracht met 6 geprogrammeerd") 
        list  = valR.split()
        i=0
        for num in list:
            if (i==0):
                ilist[i]=int(num) #nog aantal in ilist beperken??
            else:
                ilist.append(int(num))
            modbusclient.write_single_register(IR+i,ilist[i])
            i=i+1
            #print(i)
        #write_multiple_registers(IR, ilist)
            
#modbusclient.close()


