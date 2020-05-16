import sys
import time
import serial
import threading

from jostick_test.ums_serial.writer import UMDSerialWriter
from jostick_test.ums_joystick.key_reader import JoystickReader 

class UMDSerial():
    
    is_input = False
    
    def __init__(self):
        self.__serial = None
        self.__writer = None
        self.__joyreader = None
        self.__is_serial_connect = False
        self.__is_joy_connect = False

    
        # self.waitPort()
        # self.write("1")

    def waitPort(self):

        # while(True) : 
            # self.__is_connect = self.open()

        self.__is_serial_connect = self.is_input
        
        if self.__is_serial_connect == True :
            
            # joy 연결 여부
            self.__is_joy_connect = self.waitjoy()

            if self.__is_joy_connect == True :
                self.triggerjoy()
            else :
                print("조이스틱 연결을 확인 해 주세요...")

            self.write("1")
            # break
        else :
            print("error")
        
        time.sleep(1.0)

    print("스위치가 연결되었습니다.")

    def open(self):
        try:
            self.__serial = serial.Serial(
                port='/dev/serial0',
                baudrate=9600
            )
        except:
            print(' 포트를 여는 데 실패했습니다.')
           
            return False
        return True

    def write(self, data):
        self.__writer = UMDSerialWriter(serial=1, send_data = data)
        t = threading.Thread(target = self.__writer.run, args="")
        t.start()

    def waitjoy(self):
        pass
        # try:
        # joystick 연결되어 있는지 확인
        
        # 연결되었으면
        # joystick trigger 시작
    
    def triggerjoy(self):
        pass
        

    def test_input(self):
        test_str = input("True or False 입력 : ")
        # test_str = bool(test_str)
        if test_str.lower() == "true":
            print("True")
            self.is_input = True
            return self.is_input
        elif test_str.lower() == "false":
            print("False")
            self.is_input = False
            return self.is_input
        else :
            print("다시 입력 하세요.")


        # thread test 
        # self.__writer = UMDSerialWriter(serial=1, send_data = data)
        # t = threading.Thread(target = self.__writer.run, args="")
        # t.start()

if __name__ == "__main__":
    us = UMDSerial()
    print(" -- umd_serial test -- ")


    # us.waitPort()
    while True:
        # us.test_input()
        # us.waitPort()
        t1 = threading.Thread(target = us.waitPort, args="")
        t1.start()
        t2 = threading.Thread(target = us.test_input, args="")
        t2.start()

        

        # t1.start()


        # if us.is_input == True:
        #     t2.join()

        time.sleep(1)