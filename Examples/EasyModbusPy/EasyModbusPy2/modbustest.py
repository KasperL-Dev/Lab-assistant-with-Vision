from easymodbus.modbusClient import ModbusClient
modbusclient = ModbusClient('169.254.220.130', 502)
modbusclient.connect()
#Write a single coil to the Server – Coil number “1”
print("write coil 0,0")
modbusclient.write_single_coil(0,False)
#read coils
print("read coils")
print(modbusclient.read_coils(0,8))
#Write a single coil to the Server – Coil number “1”
print("write coil 0,1")
modbusclient.write_single_coil(0,True)
#read coils
print("read coils")
print(modbusclient.read_coils(0,8))
#write single register
print("Register 9000 schijven (11)")
modbusclient.write_single_register(9000, 11)
print("Lees  2 Registers vanaf 9000")
holdingRegisters = modbusclient.read_holdingregisters(9000,2)
print (holdingRegisters)
#print("Register 9000 schijven (0)")
#modbusclient.write_single_register(9000, 0)

print("Lees  2 Registers vanaf 9000")
holdingRegisters = modbusclient.read_holdingregisters(9000,2)
print (holdingRegisters)
print(">>>>>>>>>>>>>>>>>>>>>")
#read coils
###print("read coils")
###print(modbusclient.read_coils(0,8))
###print("Meerdere coils vanaf 0 een waarde geven")
###val=[1,0]
###??????x=modbusclient.write_multiple_coils(0,val)
###print("Meerdere coils vanaf 0")
###val=[0,1]
###x=modbusclient.write_multiple_coils(0,val)
#read coils
###print("read coils")
###print(modbusclient.read_coils(0,8))
print("lees x positie")
holdingRegisters = modbusclient.read_holdingregisters(7001,2)
print (holdingRegisters)
#discreteInputs = modbusclient.read_discreteinputs(0, 1)
#print("Discrete inputs-onduidelijk wat- F02 startaddres,aantal")
#print(discreteInputs)
#Read 8 Inputs Registers from Modbus-TCP Server – Server available at Port 502 (IP-Address 190.172.268.100) – Starting Address “1”, Number of Registers to Read: “8” (Notice that the Starting address might be shifted by “1”. In this example we are reading 8 Registers, the first is Register “1” (Addressed with “0”)
inputRegisters = modbusclient.read_inputregisters(7001, 2)
#print("Read Multiple Registers")
print(inputRegisters)
print(float(65536*inputRegisters[0]+inputRegisters[1]))
modbusclient.close()
