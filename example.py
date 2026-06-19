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
        
