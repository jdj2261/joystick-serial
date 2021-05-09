#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
@ Created Date: May 15. 2020
@ Updated Date: May 03. 2021  
@ Author: Dae Jong Jin 
@ Description: TODO
'''

import time
import sys, os
sys.path.append(os.path.dirname(__file__))
from threading import Thread

from ums_xbox.xbox import Xbox 
from ums_serial.ums_serial import UmsSerial

# dev_port = "/dev/serial0"
class XboxControl:
    def __init__(self, port_name, baudrate, timeout, testmode):
        self.ums_ser = UmsSerial(port_name, baudrate, timeout, testmode)

    def __repr__(self) -> str:
        return "<{cls}>".format(cls=self.__class__.__name__)
    
    def __call__(self):
        return self.execute()

    def execute(self):
        xbox = Xbox(0)
        xbox.start()
        while True:
            try:
                if self.ums_ser.connect():
                    print("connected")
                    self.ums_ser.write(0x01)
            except Exception :
                self.ums_ser.disconnect()
            time.sleep(0.5)
    
        # self.connect_port()
        # self.read_data()

#     def connect_port(self):
#         is_connected_port = False
#         while True:
#             is_connected_port = self.open_port() if not self.mode else True
#             if is_connected_port:
#                 print("시리얼 연결이 되었습니다.")
#                 break
#             print("시리얼 연결이 되었는지 확인해 주세요.")
#             time.sleep(0.2)

#     def open_port(self):
#         try:
#             self.serial = serial.Serial(
#                 port=dev_port,
#                 baudrate=9600,
#             )
#         except:
#             print(' 포트를 여는 데 실패했습니다.')
#             return False
#         return True

#     def read_data(self):
#         xbox = Xbox(serial=self.serial, port=dev_port, mode=self.mode)
#         while True:
#             xbox.connect_joystick()
#             isXbox = xbox.read_joystic_name()
#             if isXbox:
#                 xbox.read_axises()
#                 xbox.read_buttons()
#                 xbox.joy_main_event()
#                 break
#             else:
#                 print(" \n 조이스틱을 다시 연결해 주세요")
#                 xbox.connect_joystick()
#             time.sleep(0.2)

def test():
    port_name = "/dev/ttyACM0"
    baudrate = 9600
    timeout = 0.1
    testmode = True
    xc = XboxControl(port_name, baudrate, timeout, testmode)
    xc.start()
    # main loop

    # mode = False if len(sys.argv) <= 1 else True
    # XboxControl(mode).start()

if __name__ == "__main__":
    test()

        
