#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created Date: Oct 20. 2020
Copyright: UNMAND SOLUTION
Author: Dae Jong Jin 
Description: Logitech Joystick key reader
'''
import matplotlib.animation as animation
import matplotlib.pyplot as plt
import sys
import os, struct, array
from time import sleep
from fcntl import ioctl

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from threading import Thread, Condition
from .names import axis_names, button_names
from .protocol import PacketProtocol
from .scope import Scope
from src.ums_serial.writer import UMDSerialWriter


# class Error(Exception):
#     def __init__(self):


"""
10 /14 세종시 조종기 테스트

이슈 1. 조종기 선 연결 불안정 (연결 선 후크 마모현상으로 자주 연결이 끊어지는 현상이 발생함.)
이슈 2. 민감도 조절 (올라가는 속도, 내려가는 속도)
이슈 3. 버튼 누른 상태에서 선 연결이 끊어지면 추후에 선 연결 시 전 값이 남아있어 출발할때 움직이는 현상 발생 --> 매인 컨트롤러 : VCU 보드 쪽 문제
"""

"""
master --> write pass 주석해제 하기!!!!
"""

class JoystickReader(object):

    axis_states = {}
    button_states = {}  
    axis_map = []
    button_map = []
    origin_axis_states = {}
    origin_button_states = {}  
    origin_axis_map = []
    origin_button_map = []
    APS_VAL = 2500#5000
    DELTA_PLUS = 250#100
    DELTA_MINUS = 250#50
    STEER_RATIO = 1
    # STEER_PARAM = 100

    def __init__(self,serial, port):
        self.__serial = serial
        self.__port = port
        self.__num_buttons = None
        self.__num_axes = None
        self.__jsdev = None
        self.__fn = '/dev/input/js0'
        self.__writer = UMDSerialWriter(serial=self.__serial, port=self.__port)
        self.__pt = PacketProtocol()
        self.__ESTOP = 'OFF' 
        self.__GEAR = 'GNEUTRAL'
        self.__WHEEL = 'WFORWARD'
        self.__isConnect_joy = True

        self.accel_value = [0x00, 0x00]
        self.steer_value = [0x00, 0x00]
        self.exp_value   = [0x00,0x00]
        self.brake_value = [0x00, 0x00]
        self.speed_val = 0
        self.brake_val = 0
        self.steer_val = 0
        self.exp_val = 0
        self.pre_exp_val = 0
        self.pre_val=0
        self.accel_val = self.speed_val + self.APS_VAL
        self.result_accel_val = self.speed_val + self.APS_VAL

        self.condition = Condition()

    def joy_check(self):
        print("Joystick Test.. ")
        return True

    def joy_open(self):
        print("Joystick Test.. ")

    def joy_name_read(self):
        print("Joystick Test.. ")
        return True

    def axis_read(self):
        print("Joystick Test.. ")

    def button_read(self):
        print("Joystick Test.. ")

    def speed_insert(self):
        value = self.speed_val 
        return value 

    def exp_insert(self):
        value = self.exp_val
        return value 

    def steer_insert(self):
        value = self.tmp
        return value 

    def accel_test_thread(self):
        while True:
            # self.condition.acquire()
            if self.pre_val < self.speed_val:
                while self.accel_val <= self.speed_val:
                    print("PLUS!!!")
                    if self.__GEAR == 'GFORWARD':
                        self.accel_val = self.accel_val + self.DELTA_PLUS
                    elif self.__GEAR == 'GBACKWARD':
                        self.accel_val = self.accel_val + ( self.DELTA_PLUS * 2)
                    # else:
                        # self.accel_val = self.DELTA_PLUS
                    
                    if self.accel_val >= 60000 :
                        self.accel_val = 60000
                    # print(self.current_val, end=" ")
                    self.accel_value = self.accel_val.to_bytes(2, byteorder="little", signed=False)
                    sleep(0.02)
                # self.current_val = self.speed_val
            elif self.pre_val >= self.speed_val:
                
                while self.accel_val >= self.speed_val:
                    if self.__GEAR == 'GFORWARD':
                        self.accel_val = self.accel_val - self.DELTA_MINUS
                    elif self.__GEAR == 'GBACKWARD':
                        self.accel_val = self.accel_val - ( self.DELTA_MINUS * 2)
                    # else :
                    #     self.accel_val = 0
                    # self.accel_val = self.accel_val - self.DELTA_MINUS

                    if self.accel_val < 0:
                        self.accel_val = self.speed_val + self.APS_VAL
                    # print(self.current_val, end=" ")
                    self.accel_value = self.accel_val.to_bytes(2, byteorder="little", signed=False)
                    sleep(0.02)
            # self.condition.notify()
            # self.condition.release()

    def data_thread(self):
        while True:
            self.exp_val += 100
            # print(self.exp_val)
            if self.exp_val >= 32000:
                self.exp_val = 32000
                while True:
                    # print(tmp)
                    self.exp_val = self.exp_val - 200
                    if self.exp_val <=-32000:
                        self.exp_val = -32000
                        break
                    sleep(0.01)
            sleep(0.01)
    def sendpacket_thread(self):
        try:
            t = Thread(target=self.accel_test_thread)
            t.daemon = True
            t.start()

            t2 = Thread(target=self.data_thread)
            t2.daemon = True
            t2.start()
        except RuntimeError :
            pass

        while True:        # alive count (0 ~ 255)
            # send packet
            if self.__isConnect_joy:
                self.__pt.count_alive()

                self.tmp = self.exp_val / 32000

                if self.pre_exp_val != self.exp_val:
                    print("PRE : {}, CUR : {}".format(self.pre_exp_val, self.exp_val))
                    if self.pre_exp_val < self.exp_val:
                        if self.exp_val >= 0:
                            # CASE 2
                            if self.tmp <= self.STEER_RATIO:
                                self.tmp = (1/self.STEER_RATIO) * self.tmp * self.tmp
                                self.tmp = int(self.tmp * 32000)
                            # else:
                            #     self.tmp = int(self.tmp * 32000)
                        else:
                            if self.tmp <=  self.STEER_RATIO -1 :
                                self.tmp = (1/self.STEER_RATIO)*(self.tmp +1)*(self.tmp + 1) -1
                                self.tmp = int(self.tmp * 32000)
                            # else:
                            #     self.tmp = self.tmp
                            #     self.tmp = int(self.tmp * 32000)

                    elif self.pre_exp_val >= self.exp_val:
                        if self.exp_val >= 0:
                            print("TEST : {}".format(self.tmp))
                            if self.tmp >=  (1 - self.STEER_RATIO) :
                                self.tmp = (-1/self.STEER_RATIO)*(self.tmp -1)*(self.tmp-1) + 1  
                                print("TEST22 : {}".format(self.tmp))
                                self.tmp = int(self.tmp * 32000)
                            # else:
                            #     self.tmp = self.tmp
                            #     self.tmp = int(self.tmp * 32000)
                        else:
                            # CASE 2
                            if self.tmp >= -self.STEER_RATIO:
                                self.tmp = (-1/self.STEER_RATIO) * self.tmp * self.tmp
                                self.tmp = int(self.tmp * 32000)
                            # else:
                            #     self.tmp = int(self.tmp * 32000)
                    self.pre_exp_val = self.exp_val

                self.accel_value = self.accel_val.to_bytes(2, byteorder="little", signed=False)
                self.brake_value = self.brake_val.to_bytes(2, byteorder="little", signed=False)
                self.steer_value = self.steer_val.to_bytes(2, byteorder="little", signed=True)
                self.exp_value = self.exp_val.to_bytes(2, byteorder="little", signed=True)

                # brake 잡지 않은 상태 --> APS 해제
                if self.brake_val == 0:
                    if self.accel_val < self.APS_VAL:
                        self.accel_val = self.APS_VAL
                    
                    self.result_accel_val = self.accel_val
                # 잡으면 APS 해제
                else :
                    self.accel_val = 0
                    self.result_accel_val = 0
  
                if self.__ESTOP == 'ON':
                    self.result_accel_val = 0

                self.speed_value = self.result_accel_val.to_bytes(2, byteorder="little", signed=False)
                
                self.__pt.speed_data[0] = self.speed_value[0]
                self.__pt.speed_data[1] = self.speed_value[1]
                self.__pt.brake_data[0] = self.brake_value[0]
                self.__pt.brake_data[1] = self.brake_value[1]
                self.__pt.steer_data[0] = self.steer_value[0]
                self.__pt.steer_data[1] = self.steer_value[1]
                self.__pt.steer_data[2] = self.exp_value[0]
                self.__pt.steer_data[3] = self.exp_value[1]

                packet = self.__pt.makepacket(ESTOPMODE=self.__ESTOP, GEARMODE=self.__GEAR, WHEELMODE=self.__WHEEL)

                # print("accel val : {0}".format(self.result_accel_val), end=" ")
                # print("steer val : {0}".format(self.steer_val), end=" ")
                # print("exp val : {0}".format(self.exp_val), end=" ")
                # print("packet : {0}".format(packet))
                self.__writer.run(packet)
            else:
                self.reset_value()
                print("not joystick connect")
                sleep(0.1)

            self.pre_val = self.speed_val
            sleep(0.02) # 50Hz

    def reset_value(self):
        self.speed_val = 0
        self.accel_val = 0
        self.result_accel_val = 0
        self.brake_val = 0
        self.steer_val = 0
        self.exp_val = 0

        self.accel_value = [0x00, 0x00]
        self.brake_value = [0x00, 0x00]
        self.steer_value  = [0x00, 0x00]
        self.exp_value  = [0x00, 0x00]
        
    def plot_thread(self):

        try:
            fig = plt.figure(figsize=(10,8))     #figure(도표) 생성

            ax1 = plt.subplot(311, xlim=(0, 50), ylim=(0, 1024))
            ax2 = plt.subplot(312, xlim=(0, 50), ylim=(0, 1024))
            ax3 = plt.subplot(313, xlim=(0, 50), ylim=(0, 1024))

            ax1.grid(True)
            ax2.grid(True)
            ax3.grid(True)

            # 객체 생성
            scope = Scope(ax1,self.speed_insert, ystart = 0, ymax = 65535, title = "origin", color='b')
            scope2 = Scope(ax2,self.exp_insert, ystart = -65535, ymax = 65535, title = "result", color='r')
            scope3 = Scope(ax3,self.steer_insert, ystart = -65535, ymax = 65535, title = "change", color='y')    

            # update 매소드 호출
            ani = animation.FuncAnimation(fig, scope.update,interval=10,blit=True)
            ani2 = animation.FuncAnimation(fig, scope2.update,interval=10,blit=True)
            ani3 = animation.FuncAnimation(fig, scope3.update,interval=10,blit=True)
            plt.show()
        except:
            print("Not show plot")
        finally:
            plt.show()

    def joy_main_event(self):
        cnt = 0
        try:
            t = Thread(target=self.sendpacket_thread)
            t2 = Thread(target=self.plot_thread)

            t.daemon = True
            t.start()

            t2.daemon = True
            t2.start()
            
            while True:
                cnt += 1
                if cnt >= 255:
                    cnt = 0

                sleep(0.01)
        except (KeyboardInterrupt, SystemExit):
            print ('\n! Received keyboard interrupt, quitting threads.\n')
            # exit(0)

