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

    def __init__(self):
        self.__serial = None
        self.__writer = None
        self.__joyreader = None
        self.__is_serial_connect = False
        self.__is_joy_connect = False

    def waitPort(self):

        # print("시리얼 연결이 되었습니다.")
        while(True) : 
            self.__is_serial_connect = self.open()
  
            # 시리얼 연결이 되면
            if self.__is_serial_connect == True :
                print("시리얼 연결이 되었습니다.")
                self.triggerjoy()
                break
            else :
                print("시리얼 연결이 되었는지 확인해 주세요.")
        
            time.sleep(1.0)

    def open(self):
        try:
            self.__serial = serial.Serial(
                port='/dev/serial0',
                baudrate=9600,
            )
            # print('시리얼 연결이 확인되었습니다.')
        except:
            print(' 포트를 여는 데 실패했습니다.')
           
            return False
        return True

    def triggerjoy(self):
        jr = JoystickReader(serial=self.__serial)
        jr.joy_open()
        jr.joy_name_read()
        jr.axis_read()
        jr.button_read()
        jr.joy_main_event()


    # def test_input(self):
    #     while True:
    #         test_str = input("True or False 입력 : ")
    #         # test_str = bool(test_str)
    #         if test_str.lower() == "true":
    #             print("True")
    #             self.is_input = True
    #             return self.is_input
    #             break
    #         else :
    #             pass
    #             print("다시 입력 하세요.")

if __name__ == "__main__":
    us = UMDSerial()
    print(" -- umd_serial test -- ")
    us.waitPort()
    
    # while True:
        # us.test_input()
        # us.waitPort()
    # t1 = threading.Thread(target = us.waitPort, args="")
    # t2 = threading.Thread(target = us.test_input, args="")

    # t1.start()
    # t2.start()

    # t1.join()
    # t2.join()

        
