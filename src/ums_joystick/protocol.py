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
LENGTH : 14bytes
0 1 2   3     4    5      6     7      8      9      10      11     12   13
S T X ESTOP GEAR WHEEL SPEED0 SPEED1 STEER0 STEER1 ALIVE CHECKSUM ETX0 ETX1

S → 0x53 
T → 0x54
X → 0x58
ESTOP → 0x00 : OFF,           0x01 : ON
GEAR  → 0x00 : forward drive, 0x01 : neutral,     0x02 : backward drive
WHEEL → 0x00 : forward wheel, 0x01: fourth wheel, 0x02 : backward wheel
SPEED → -32768 ~ 32768 //actual speed
STEER → -32768 ~ 32768 // actual steering degree
ALIVE → 0 ~ 255        // increasing each one step 
Checksum → E-STOP + GEAR + WHEEL + SPEED0 + SPEED1 + STEER0 + STEER1
ETX0 → 0x0D
ETX1 → 0x0A 
'''
from time import sleep

class PacketProtocol(object):
    packet  = [0 for i in range(14)]
    ESTOP   = {'OFF' : 0x00 , 'ON' : 0x01}
    GEAR    = {'GFORWARD' : 0x00, 'GNEUTRAL' : 0x01, 'GBACKWARD' : 0x02}
    WHEEL   = {'WFORWARD' : 0x00, 'WFOURTH'  : 0x01, 'WBACKWARD' : 0x02}

    def __init__(self):
        self.S           = 0x53
        self.T           = 0x54
        self.X           = 0x58
        # self.ESTOP       = self.ESTOP['OFF']
        # self.GEAR        = self.GEAR['GNEUTRAL']
        # self.WHEEL       = self.WHEEL['WFOURTH']
        self.speed_data  = [0x00,0x00]
        self.steer_data  = [0x00,0x00]
        self.ALIVE       = 0x00
        self.CHECKSUM    = 0x00
        self.ETX0        = 0x0D
        self.ETX1        = 0x0A

    def makepacket(self):
        self.packet[0]   = self.S
        self.packet[1]   = self.T 
        self.packet[2]   = self.X       
        self.packet[3]   = self.ESTOP.get('OFF')
        self.packet[4]   = self.GEAR.get('GBACKWARD')
        self.packet[5]   = self.WHEEL.get('WFOURTH')
        self.packet[6]   = self.speed_data[0]
        self.packet[7]   = self.speed_data[1]
        self.packet[8]   = self.steer_data[0]
        self.packet[9]   = self.steer_data[1]
        self.packet[10]  = self.ALIVE
        self.packet[11]  = self.CHECKSUM
        self.packet[12]  = self.ETX0
        self.packet[13]  = self.ETX1

        return self.packet

if __name__ == "__main__":
    pt = PacketProtocol()

    print(pt.GEAR['GBACKWARD'])
    pt.GEAR['GNEUTRAL'] = 0x05
    print(pt.GEAR['GBACKWARD'])

    print(pt.packet[4])
    print(pt.makepacket())


    # pt.packet[4] = pt.GEAR['GBACKWARD']
    # pt.WHEEL = pt.WHEEL

    # while True:
    #     print('{0:02x}'.format(pt.ALIVE))
    #     print(pt.makepacket())
    #     pt.ALIVE += 1

    #     if pt.ALIVE >= 256 :
    #         pt.ALIVE = 0

    #     sleep(0.05)

    # print(pt.packet)
    # print(pt.makepacket())

