#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#Created on Wed Jul 30 18:06:23 2021

import time
try:    
    from EasyModbusPy.cobotconnect19216801 import cobotconnect #voorwaarde verbinding met cobot
    cob=cobotconnect()
except:
    print("geen cobot connected or file cobotconnect missing")
P=[525.274658203125, -259.6734619140625, 190.7347869873047, 176.66314697265625, -1.9161999225616455, 40.99833297729492]
N=[526.7259521484375, -215.16477966308594, 195.68179321289062, -179.4339141845703, -2.6276538372039795, 44.84650421142578]
p_dy=-61 
n_dz=40
sp=50 #speed
E=cob.O_out(801,0)
time.sleep(0.3)
E=cob.O_out(800,1)    
time.sleep(0.5)  #grijer open
for x in range(4):
    pstxt=str(P[0]) + " ,"  + str(P[1]+x*p_dy) + " ,"  + str(P[2]+50) + " ,"  + str(P[3]) + " ,"  + str(P[4]) + " ,"  + str(P[5]) # 10mm boven pak
    cob.sendCobotPos(pstxt,sp) 
    time.sleep(2)
    pstxt=str(P[0]) + " ,"  + str(P[1]+x*p_dy) + " ,"  + str(P[2]) + " ,"  + str(P[3]) + " ,"  + str(P[4]) + " ,"  + str(P[5]) #pak
    cob.sendCobotPos(pstxt,sp)
    time.sleep(0.3)
    E=cob.O_out(800,0)
    time.sleep(0.3)
    E=cob.O_out(801,1)    
    time.sleep(0.5)
    pstxt=str(P[0]) + " ,"  + str(P[1]+x*p_dy) + " ,"  + str(P[2]+50) + " ,"  + str(P[3]) + " ,"  + str(P[4]) + " ,"  + str(P[5]) # 10mm boven pak
    cob.sendCobotPos(pstxt,sp) 
    time.sleep(2)
    pstxt=str(N[0]) + " ,"  + str(N[1]) + " ,"  + str(N[2]+20+x*n_dz) + " ,"  + str(N[3]) + " ,"  + str(N[4]) + " ,"  + str(N[5]) # 10mm boven neerzet
    cob.sendCobotPos(pstxt,sp) 
    time.sleep(2)
    pstxt=str(N[0]) + " ,"  + str(N[1]) + " ,"  + str(N[2]+x*n_dz) + " ,"  + str(N[3]) + " ,"  + str(N[4]) + " ,"  + str(N[5]) # neerzet
    cob.sendCobotPos(pstxt,sp) 
    time.sleep(2)
    E=cob.O_out(801,0)
    time.sleep(0.3)
    E=cob.O_out(800,1)    
    time.sleep(0.5)
    pstxt=str(N[0]) + " ,"  + str(N[1]) + " ,"  + str(N[2]+20+x*n_dz) + " ,"  + str(N[3]) + " ,"  + str(N[4]) + " ,"  + str(N[5]) # 10mm boven neerzet
    cob.sendCobotPos(pstxt,sp) 
    time.sleep(2)
cob.stop()
    
    
        
