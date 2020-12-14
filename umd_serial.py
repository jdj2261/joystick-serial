import sys
import time
import serial
import threading

from src.ums_serial.writer import UMDSerialWriter
from src.ums_joystick.key_reader import JoystickReader 

'''
Created Date: May 15. 2020
Copyright: UNMAND SOLUTION
Author: Dae Jong Jin 
Description: Serial and Joystick Connection
'''

class UMDSerial():
    port_name = "/dev/serial0"

    def __init__(self):
        self.__serial = None
        self.__writer = None
        self.__joyreader = None
        self.__is_serial_connect = False
        self.__is_joy_connect = False

    def waitPort(self):

        while(True) : 
            # print(self.port_name)
            self.__is_serial_connect = self.open(UMDSerial.port_name)
            self.__is_serial_connect = True
  
            # 시리얼 연결이 되면
            if self.__is_serial_connect == True :
                print("시리얼 연결이 되었습니다.")
                self.triggerjoy()
                break
            else :
                print("시리얼 연결이 되었는지 확인해 주세요.")
            time.sleep(0.2)

    def open(self, port_name):
        try:
            self.__serial = serial.Serial(
                port=port_name,
                baudrate=9600,
            )
            # print('시리얼 연결이 확인되었습니다.')
        except:
            print(' 포트를 여는 데 실패했습니다.')
           
            return False
        return True

    def triggerjoy(self):
        while True:
            jr = JoystickReader(serial=self.__serial, port=self.port_name)
            jr.joy_open()
            isCorrect = jr.joy_name_read()
            if isCorrect:
                jr.axis_read()
                jr.button_read()
                jr.joy_main_event()
                break
            else:
                print(" \n 조이스틱을 다시 연결해 주세요")
                jr.joy_open()
            time.sleep(0.2)

if __name__ == "__main__":
    us = UMDSerial()
    us.waitPort()

        
