#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#Created on Wed Jul 30 18:06:23 2021

import time
try:    
    from EasyModbusPy.cobotconnect19216801 import cobotconnect #voorwaarde verbinding met cobot
    cob=cobotconnect()
except:
    print("geen cobot connected or file cobotconnect missing")
P=[0.0,0.0,0.0,0.0,0.0,0.0]
N=[0.0,0.0,0.0,0.0,0.0,0.0]
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
    
cob.stop()
    
    
        
