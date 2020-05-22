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

    def makepacket(self, ESTOPMODE='OFF', GEARMODE='GNEUTRAL', WHEELMODE='WFOURTH'):
        self.packet[0]   = self.S
        self.packet[1]   = self.T 
        self.packet[2]   = self.X       
        self.packet[3]   = self.ESTOP.get(ESTOPMODE)
        self.packet[4]   = self.GEAR.get(GEARMODE)
        self.packet[5]   = self.WHEEL.get(WHEELMODE)
        self.packet[6]   = self.speed_data[0]
        self.packet[7]   = self.speed_data[1]
        self.packet[8]   = self.steer_data[0]
        self.packet[9]   = self.steer_data[1]
        self.packet[10]  = self.ALIVE
        self.packet[11]  = self.calc_checksum(self.packet[3:10])
        self.packet[12]  = self.ETX0
        self.packet[13]  = self.ETX1

        return self.packet


    def calc_checksum(self, data ):
        result = data
        # print(data) 
        sum = 0
        for i in data:
            sum = sum + i
        sum = -(sum % 256)
        checksum = sum & 0xFF
        return checksum

    def count_alive(self):
        self.ALIVE += 1
        if self.ALIVE >= 256 :
            self.ALIVE = 0
        
# if __name__ == "__main__":
#     pt = PacketProtocol()

#     while True:

#         speed_data = -1253
#         steer_data = -1
#         speed_data = speed_data.to_bytes(2, byteorder="little", signed=True)
#         steer_data = steer_data.to_bytes(2, byteorder="little", signed=True)

#         pt.steer_data[0] = steer_data[0]
#         pt.steer_data[1] = steer_data[1]
#         pt.speed_data[0] = speed_data[0]
#         pt.speed_data[1] = speed_data[1]

#         pt.count_alive()
#         # print('{0:02x}'.format(pt.ALIVE))
#         result = pt.makepacket(WHEELMODE='WBACKWARD')
#         print(result)
#         test = sum(result[3:10])
#         checksum = pt.calc_checksum(result[3:10])
#         check_checksum = test + checksum
#         check_checksum = check_checksum & 0xFF
#         # test ="0x{:02x}".format(check_checksum)

#         print("0x{:02x}".format(check_checksum))       
#         sleep(0.05)



# print calc_checksum('00300005000')

    # print(pt.packet)
    # print(pt.makepacket())

