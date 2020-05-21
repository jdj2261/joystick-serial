#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created Date: May 15. 2020
Copyright: UNMAND SOLUTION
Author: Dae Jong Jin 
email : jdj2261@unmansol.com
git : jdj2261@github.com
Description: Logitech joystick Serial Test code using raspberry pi 3
'''

import os, struct, array, serial, time
from fcntl import ioctl 

# try :
#     ser = serial.Serial(
#         port = '/dev/opencm',
#         baudrate = 9600,
#     )

# except serial.serialutil.SerialException as e:
#     print(e)

# # try :
# #     fn = '/dev/video1'
# #     print('Opening %s...' % fn)
# #     jsdev = open(fn, 'rb')
# # except FileNotFoundError as e:
# #     print(e)

# number = 4
# value = 1

# class KeyError(Exception):
#     def __str__(self):
#         return "q 입력을 하였습니다."

# class Writer():
#     def __init__(self, serial, send_data):
#         self.__serial = serial
#         self.__send_data = send_data

#     def run(self):
#         # print(self.__serial)
#         result = hex(self.__send_data)
#         self.__serial.write(result.encode('utf-8'))
#         print(result.encode('utf-8'))
#         # send_button_data = str(number)
#         # send_button_value_data = str(value)
#         # send_data = send_button_data + send_button_value_data
#         # ser.write(send_data.encode('utf-8'))
#         # print("sending..")


# def reopen():
#     global ser
#     try:
#         ser = serial.Serial(
#             port='/dev/opencm',
#             baudrate=9600
#         )
#         print("스위치가 재 연결되었습니다.")
#     except:
#         print(u' 포트를 다시 연결해 주세요')
#     time.sleep(1)

# writer_test = Writer(serial=ser, send_data=0x15)
# while True:


#     try : 
#         writer_test.run()
#         # send_button_data = str(number)
#         # send_button_value_data = str(value)
#         # send_data = send_button_data + send_button_value_data
#         # ser.write(send_data.encode('utf-8'))
#         # print("sending..")

#         n = input('입력 : ')
#         if n == "q":
#             raise KeyError()
#     except KeyError as e:
#         print(e)
#     except serial.serialutil.SerialException as e:
#         print("error")
#         reopen()


#     time.sleep(0.1)

axis_states = {}
button_states = {}

axis_names = {
    0x00 : 'x',
    0x01 : 'y',
    0x02 : 'z',
    0x123 : 'd'
}

button_names = {
    0x10 : 'a',
    0x11 : 'b',
}

tmp_axis_map = []
axis_map = []
button_map = []

buf = array.array('B', [0] * 0x40)  # unsigned int
# buf = array.array('B', [0] * 0x40)  # Hex

buf[0] = 0x00
buf[1] = 0x01
buf[2] = 0x02

print(buf)
num_buf = 3

for axis in buf[:num_buf] :

    axis_name = axis_names.get(axis,'unknown')
    print("axis : {0}, axis_name: {1}".format(hex(axis), axis_name))
    axis_map.append(axis_name)
    tmp_axis_map.append(hex(axis))
    axis_states[hex(axis)] = 0.0

print("axis_map : {0}".format(', '.join(axis_map)))
print("tmp_axis_map : {0}".format(', '.join(tmp_axis_map)))
print("axis_states : {0}".format(axis_states))


try :
    while True :
        
        try:
            print(" --- Test ---")
            test_input = input(" 입력하세요 : ")
            test_input = hex(int(test_input, 16))
            print(test_input)

            if test_input in tmp_axis_map :
                pass
                # print(tmp_axis_map[1])
                
            else :
                print(" 존재하지 않습니다..")
            
        except ValueError :
            print("잘못된 입력입니다.")

        
except KeyboardInterrupt as e:
    print(" ctrl + c pressed !!")
    print("exit .. ")