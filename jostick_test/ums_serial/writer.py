#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created Date: May 15. 2020
Copyright: UNMAND SOLUTION
Author: Dae Jong Jin 
Description: Pyserial Write
'''

import serial
import time
import threading


class UMDSerialWriter():
    def __init__(self, serial, send_data):
        super(UMDSerialWriter, self).__init__()
        self.__serial = serial
        self.__send_data = send_data

    def run(self):
        print("write threading....")
        # self.__serial.write("1")
        print(self.__serial)
        print(self.__send_data)

        # self.__serial.op
        # self.serial = 0x00
        # print(self.serial)



# if __name__ == "__main__":

#     sw = UMDSerialWriter(0,0)
#     t = threading.Thread(target = sw.run, args="")
#     t.start()
#     time.sleep(1)

#     print("Main Thread")

# from threading import Thread

# def work(id, start, end, result):
#     total = 0
#     for i in range(start, end):
#         total += i
#     result.append(total)
#     return

# if __name__ == "__main__":
#     START, END = 0, 100000000
#     result = list()
#     th1 = Thread(target=work, args=(1, START, END, result))
    
#     th1.start()
#     th1.join()

# print("Result: {sum(result)}")
