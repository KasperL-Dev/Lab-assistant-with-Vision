#import sys
# sys.path.append(./Documents/Techman_controller-git/Techman-controller/EasyModbusPy)
import time
keuze="x"
while (keuze!='q'): 
    #try:
    from EasyModbusPy.cobotconnect19216801 import cobotconnect #voorwaarde verbinding met cobot
    cob=cobotconnect()
    #except:
    #    print("geen cobot connected or file cobotconnect missing")
    print("___________menu voor cobot________")
    print("a. Ga naar positie")    
    print("aa. Wacht tot op positie")
    print("ab. Ga naar joint-position")
    print("ac. Wacht tot op joint-position")
    print("b. Lees positie cobot")
    print("bb. Lees joints cobot")
    print("c. Lees koppels cobot")     
    print("d. Schrijf output D0 t/m D15")    
    print("e. Schrijf output op eind effector DE0 t/m DE4")
    print("f. Lees output D0 t/m D15")    
    print("g. Lees input DI0 t/m DI15")
    print("h. Schrijf register")
    print("i. Lees register")
    print("j. Lees toestand cobot")
    print("k. stopListen")
    print("l. Run program")
    print("m. Pause cobot")
    print("n. Resume cobot")
    print("o. Stop en Buffer legen")
    
    #print("m. Open stationfile-needed for functions n,p,t,u,w,x,y,z")
    #print("n. Ga naar punt")
    #print("p. Grijperorientatie")
    #print("r. Point with Orientation")
    #print("o. Open grijper(DE1 uit, DE0 aan)")
    #print("s. Sluit grijper(DE0 uit, DE1 aan)")
    print("v. Vertikaal 50 mm")
    print("r. Relatieve beweging (let op z positief=>naar beneden)")
    print("q. Quit")
    keuze=input("geef keuze: ")
    if (keuze=="a"):
        pstxt=input("Geef positie. x,y,z,a,b,c: ")
        sp=50 #speed
        cob.sendCobotPos(pstxt,sp) 
    elif (keuze=="aa"):
        pstxt=input("Geef positie. x,y,z,a,b,c: ")
        sp=50 #speed
        cob.waitCobotPos(pstxt,sp)
    elif (keuze=="ab"):
        pstxt=input("Geef hoeken. a,b,c,d,e,f: ")
        sp=50 #speed
        cob.sendCobotJoint(pstxt,sp)
    elif (keuze=="ac"):
        pstxt=input("Geef hoeken. a,b,c,d,e,f: ")
        sp=50 #speed
        cob.waitCobotJoint(pstxt,sp)
    elif (keuze=="b"):
        P=cob.readPos() 
        print("Positie x,y,z,a,b,c= ",P[0],P[1],P[2],P[3],P[4],P[5])    
    elif (keuze=="bb"):
        P=cob.readJoints() 
        print("Positie a,b,c,d,e,f= ",P[0],P[1],P[2],P[3],P[4],P[5])    
    elif (keuze=="c"):
        T=cob.readTorque() 
        print("Koppels: ",T[0],T[1],T[2],T[3],T[4],T[5])    
    elif (keuze=="d"):
        DO=int(input("Geef nummer output (0 t/m 15): "))
        waarde=int(input("Geef waarde (0 of 1): "))
        cob.O_out(DO,waarde)
    elif (keuze=="e"):
        DO=int(input("Geef nummer output end effector (0 t/m 3): "))
        waarde=int(input("Geef waarde (0 of 1): "))
        cob.O_out(DO+800,waarde)
    elif (keuze=="f"):
        DO=int(input("Geef nummer output (0 t/m 15): "))
        print(cob.O_in(DO))
    elif (keuze=="g"):
        DI=int(input("Geef nummer intput (0 t/m 15): "))
        print(cob.I_in(DO))
    elif (keuze=="h"):
        Reg=int(input("Geef nummer register (9000 t/m 9999): "))
        waarde=int(input("Geef waarde: "))
        cob.ModReg(Reg,waarde)
    elif (keuze=="i"):
        Reg=int(input("Geef nummer register (9000 t/m 9999): "))
        print(cob.ModRegRead(Reg))
    elif (keuze=="j"):
        E=cob.readError()
        print(E)
    elif (keuze=="k"):
        cob.stopListen()
    elif (keuze=="l"):
        padnaam=input ("geef volledig pad en naam van een .prg file (zonder extensie): ")
        cob.RunProg(padnaam)
    elif (keuze=='m'):
        cob.Pause()
    elif (keuze=='n'):
        cob.Resume()
    elif (keuze=='o'):       
        cob.DeleteBuffer()

    elif (keuze=='m'):
        station=input("give the name of the station: ")
        with open('C:/Users/jtmva/OneDrive - Hogeschool Rotterdam/AI Cobot/CAD2RoboDK/' + station+ '.stt', 'r') as f:
            station=[]
            for line in iter(f.readline, ''):
                station.append(line.rstrip('\n'))
        f.close

    elif (keuze=="n"):
        #print("n. Ga naar punt")
        pstxt=300,300,300,180,0,90 #als geen punt gevonden
        positie=input("Give the name of the point: ")
        P=cob.readPos()
        for i in range(len(station)):
            stat=station[i].split(',')
            if (stat[0]=="Point"):
                if (stat[1]==positie):
                    pstxt=stat[2] +','+ stat[3] +','+ stat[4] +','+ P[3] +','+ P[4] +','+ P[5] 
        cob.sendCobotPos(pstxt,sp)

    elif (keuze=='p'):
        pstxt=300,300,300,180,0,90 #als geen punt gevonden
        positie=input("Give the name of the Gripperorientation: ")
        P=cob.readPos()
        for i in range(len(station)):
            stat=station[i].split(',')
            if (stat[0]=="GripOrient"):
                if (stat[1]==positie):
                    pstxt=P[0] +','+ P[1] +','+ P[2] +','+ stat[2] +','+ stat[3] +','+ stat[4] 
        cob.sendCobotPos(pstxt,sp)
        #print("p. Grijperorientatie")

    elif (keuze=='r'):
        print("r. Point with Orientation")
        pstxt=300,300,300,180,0,90 #als geen punt gevonden
        positie=input("Give the name of the point with orientation: ")
        P=cob.readPos()
        for i in range(len(station)):
            stat=station[i].split(',')
            if (stat[0]=="PointOrient"):
                if (stat[1]==positie):
                    pstxt=stat[2] +','+ stat[3] +','+ stat[4] +','+ stat[5] +','+ stat[6] +','+ stat[7] 
        cob.sendCobotPos(pstxt,sp)
 
    elif (keuze=="o"):
        E=cob.O_out(801,0)
        time.sleep(0.3)
        E=cob.O_out(800,1) 
        
#     elif (keuze=="s"):
#         E=cob.O_out(800,0)
#         time.sleep(0.3)
#         E=cob.O_out(801,1)
#     elif (keuze=="v"):
#         P=cob.readPos() 
#         print("Positie x,y,z,a,b,c= ",P[0],P[1],P[2],P[3],P[4],P[5])
#         sp=50 #speed
#         pstxt=str(P[0]) + " ,"  + str(P[1]) + " ,"  + str(P[2]+50) + " ,"  + str(P[3]) + " ,"  + str(P[4]) + " ,"  + str(P[5]) 
#         cob.sendCobotPos(pstxt,sp)
#     elif (keuze=="vv"):
#         P=cob.readPos() 
#         print("Positie x,y,z,a,b,c= ",P[0],P[1],P[2],P[3],P[4],P[5])
#         sp=50 #speed
#         pstxt=str(P[0]) + " ,"  + str(P[1]) + " ,"  + str(P[2]-50) + " ,"  + str(P[3]) + " ,"  + str(P[4]) + " ,"  + str(P[5]) 
#         cob.sendCobotPos(pstxt,sp)
#     elif (keuze=="r"):
#         pstxt=input("Geef verplaatsing. x,y,z,a,b,c: ")
#         sp=50 #speed
#         cob.sendCobotMove(pstxt,sp) 
cob.stop()
        
