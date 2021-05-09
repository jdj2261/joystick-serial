#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
@ Created Date: May 15. 2020
@ Updated Date: May  4. 2021
@ Author: Dae Jong Jin 
@ Description: Packet Protocol Definition
'''

class Packet:
    ESTOP   = {'ESTOP_OFF' : 0x00 , 'ESTOP_ON' : 0x01}
    GEAR    = {'GEAR_D' : 0x00, 'GEAR_N' : 0x01, 'GEAR_R' : 0x02}
    WHEEL   = {'WHEEL_FRONT' : 0x00, 'WHEEL_ALL'  : 0x01, 'WHEEL_REAR' : 0x02}

    def __init__(self):
        self.packet      = [0 for _ in range(18)]
        self.s           = 0x53
        self.t           = 0x54
        self.x           = 0x58
        self.accel_data  = [0x00, 0x00]
        self.brake_data  = [0x00, 0x00]
        self.steer_data  = [0x00, 0x00, 0x00, 0x00]
        self.alive       = 0x00
        self.checksum    = 0x00
        self.etx0        = 0x0D
        self.etx1        = 0x0A

    def makepacket(self, estop='ESTOP_OFF', gear='GEAR_N', wheel='WHEEL_FRONT') -> list:
        self.packet[0]   = self.s
        self.packet[1]   = self.t 
        self.packet[2]   = self.x       
        self.packet[3]   = self.ESTOP.get(estop)
        self.packet[4]   = self.GEAR.get(gear)
        self.packet[5]   = self.WHEEL.get(wheel)
        self.packet[6]   = self.accel_data[0]
        self.packet[7]   = self.accel_data[1]
        self.packet[8]   = self.brake_data[0]
        self.packet[9]   = self.brake_data[1]
        self.packet[10]  = self.steer_data[0]
        self.packet[11]  = self.steer_data[1]
        self.packet[12]  = self.steer_data[2]
        self.packet[13]  = self.steer_data[3]
        self.packet[14]  = self.alive
        self.packet[15]  = self.calc_checksum(self.packet[3:14])
        self.packet[16]  = self.etx0
        self.packet[17]  = self.etx1

        return self.packet

    @staticmethod
    def calc_checksum(datas: list) -> int:
        checksum = sum(datas) & 0xFF
        return checksum
