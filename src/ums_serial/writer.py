#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created Date: May 15. 2020
Copyright: UNMAND SOLUTION
Author: Dae Jong Jin 
Description: Pyserial Write
'''

import serial
from time import sleep

class UMDSerialWriter():
    def __init__(self, serial, port):
        self.__serial = serial
        self.__port = port

    def run(self, send_data):
        try:
            self.__serial.write(serial.to_bytes(send_data))        
            # self.__serial.write(bytearray(send_data))
            # self.__serial.write(result.encode('utf-8'))'zs
            # print("\tSend ---> {0} ".format(result.encode('utf-8')))
        except:
            print("시리얼 연결이 끊어졌습니다.")
            self.reopen()

    def reopen(self):
        try:
            self.__serial = serial.Serial(
                port=self.__port,
                baudrate=9600,
            )
            print("시리얼이 재 연결되었습니다.")

        except:
            print(u' 포트를 다시 연결해 주세요')
        sleep(1)


