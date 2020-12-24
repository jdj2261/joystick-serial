#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created Date: May 15. 2020
Copyright: UNMAND SOLUTION
Author: Dae Jong Jin 
Description: Joystick Protocol
'''

'''
packet definition
LENGTH : 18bytes
0 1 2   3     4    5      6     7      8      9      10     11     12     13     14     15     16   17
S T X ESTOP GEAR WHEEL SPEED0 SPEED1 BRAKE0 BRAKE1 STEER0 STEER1 STEER2 STEER3 ALIVE CHECKSUM ETX0 ETX1

S → 0x53 
T → 0x54
X → 0x58
ESTOP → 0x00 : OFF,           0x01 : ON
GEAR  → 0x00 : forward drive, 0x01 : neutral,     0x02 : backward drive
WHEEL → 0x00 : forward wheel, 0x01: fourth wheel, 0x02 : backward wheel
SPEED → -32767 ~ 32767 //actual speed
BRAKE → -32767 ~ 32767 //brake 
STEER[0,1] → -32767 ~ 32767 // actual steering degree
STEER[1,2] → -32767 ~ 32767 // Transformed Value 
Y = int((pow((X/32767),2) * 32767 * (X / abs(X)))), Y : Transformed Value, X : Raw Data

ALIVE → 0 ~ 255        // increasing each one step 
Checksum → E-STOP +    operate = JoystickReader()
                t = Thread(target=operate.sendpacket_thread)
                t.daemon = True
                t.start() GEAR + WHEEL + SPEED0 + SPEED1 + BRAKE0 + BRAKE1 + STEER0 + STEER1
ETX0 → 0x0D
ETX1 → 0x0A 
'''
from time import sleep
from threading import Thread

class PacketProtocol(object):
    
    packet  = [0 for i in range(18)]
    ESTOP   = {'OFF' : 0x00 , 'ON' : 0x01}
    GEAR    = {'GFORWARD' : 0x00, 'GNEUTRAL' : 0x01, 'GBACKWARD' : 0x02}
    WHEEL   = {'WFORWARD' : 0x00, 'WFOURTH'  : 0x01, 'WBACKWARD' : 0x02}

    def __init__(self):
        self.S           = 0x53
        self.T           = 0x54
        self.X           = 0x58
        self.speed_data  = [0x00,0x00]
        self.brake_data  = [0x00,0x00]
        self.steer_data  = [0x00,0x00, 0x00, 0x00]
        self.ALIVE       = 0x00
        self.CHECKSUM    = 0x00
        self.ETX0        = 0x0D
        self.ETX1        = 0x0A

    def makepacket(self, ESTOPMODE='OFF', GEARMODE='GNEUTRAL', WHEELMODE='WFORWARD'):
        self.packet[0]   = self.S
        self.packet[1]   = self.T 
        self.packet[2]   = self.X       
        self.packet[3]   = self.ESTOP.get(ESTOPMODE)
        self.packet[4]   = self.GEAR.get(GEARMODE)
        self.packet[5]   = self.WHEEL.get(WHEELMODE)
        self.packet[6]   = self.speed_data[0]
        self.packet[7]   = self.speed_data[1]
        self.packet[8]   = self.brake_data[0]
        self.packet[9]   = self.brake_data[1]
        self.packet[10]  = self.steer_data[0]
        self.packet[11]  = self.steer_data[1]
        self.packet[12]  = self.steer_data[2]
        self.packet[13]  = self.steer_data[3]
        self.packet[14]  = self.ALIVE
        self.packet[15]  = self.calc_checksum(self.packet[3:14])
        self.packet[16]  = self.ETX0
        self.packet[17]  = self.ETX1

        return self.packet

    def calc_checksum(self, data ):
        sum = 0
        for i in data:
            sum = sum + i
        # sum = -(sum % 256)
        checksum = sum & 0xFF
        return checksum

    def count_alive(self):
        self.ALIVE += 1
        if self.ALIVE >= 256 :
            self.ALIVE = 0
