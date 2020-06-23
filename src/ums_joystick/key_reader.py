#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created Date: May 15. 2020
Copyright: UNMAND SOLUTION
Author: Dae Jong Jin 
Description: Logitech Joystick key reader
'''

import os, struct, array
from time import sleep
from fcntl import ioctl
import sys
from threading import Thread
from .names import axis_names, button_names
from .protocol import PacketProtocol
from src.ums_serial.writer import UMDSerialWriter

class JoystickReader(object):

    axis_states = {}
    button_states = {}  
    axis_map = []
    button_map = []
    origin_axis_states = {}
    origin_button_states = {}  
    origin_axis_map = []
    origin_button_map = []

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

    def joy_check(self):

        try:
            print('Opening %s...' % self.__fn)
            self.__jsdev = open(self.__fn, 'rb')

            if self.__jsdev:
                print("조이스틱 체크 성공")
                return True
        except:
            print("조이스틱 체크 실패")
            return False

    def joy_open(self):
        print("조이스틱의 접속을 확인하는 중입니다.")
        while True:
            is_open = self.joy_check()
            if is_open == True:
                print("조이스틱을 불러옵니다.")
                break
            sleep(1.0)

    def joy_name_read(self):
        # 드라이버로부터 조이스틱 이름 가져오기
        buf = array.array('B', [0] * 64)
        ioctl(self.__jsdev, 0x80006a13 + (0x10000 * len(buf)), buf) # JSIOCGNAME(len)
        js_name = buf.tobytes().rstrip(b'\x00').decode('utf-8') # 0x00 비어있는 값 제거 
        print('Device name: %s' % js_name)

    def axis_read(self):
        # 드라이버로부터 축 개수 가져오기
        buf = array.array('B', [0])
        ioctl(self.__jsdev, 0x80016a11, buf) # JSIOCGAXES
        # x,y 축이면 2
        num_axes = buf[0]

        # Get the axis map.
        # 키 맵핑
        buf = array.array('B', [0] * 0x40)
        ioctl(self.__jsdev, 0x80406a32, buf) # JSIOCGAXMAP
        # 읽은 값에서 총 축 수만큼 loop 돌림
        for axis in buf[:num_axes]:
            # axis_names의 첫번째 번호와 같은 이름을 가져온다.
            # 예를들어 axis가 0이면 axis_names에서 0x00 > 'x'를 가져오고
            # axis가 1이면 axis_names에 0x01 > 'y'를 가져오기 된다.
            axis_name = axis_names.get(axis, 'unknown(0x%02x)' % axis)
            self.axis_map.append(axis_name)
            self.axis_states[axis_name] = 0.0

    def button_read(self):
        # 드라이버로부터 버튼 개수 가져오기
        buf = array.array('B', [0])
        ioctl(self.__jsdev, 0x80016a12, buf) # JSIOCGBUTTONS
        # 버튼이 두 개면 2
        num_buttons = buf[0]

        # Get the button map.
        # 축과 마찬가지로 버튼 번호로 이름을 가져온다.
        buf = array.array('H', [0] * 200)
        ioctl(self.__jsdev, 0x80406a34, buf) # JSIOCGBTNMAP

        for btn in buf[:num_buttons]:
            btn_name = button_names.get(btn, 'unknown(0x%03x)' % btn)
            self.button_map.append(btn_name)
            self.button_states[btn_name] = 0

    def sendpacket_thread(self):
        
        while True:        # alive count (0 ~ 255)
            # send packet
            if self.__isConnect_joy:
                self.__pt.count_alive()
                packet = self.__pt.makepacket(ESTOPMODE=self.__ESTOP, GEARMODE=self.__GEAR, WHEELMODE=self.__WHEEL)
                print("packet : {0}".format(packet))
                self.__writer.run(packet)
            else:
                print("not joystick connect")
                sleep(1.0)
            sleep(0.02) # 50Hz


    def joy_main_event(self):
        # Main event loop
        # 키 이벤트 처리
        button = None
        axis = 0
        axis_val = 0
        exp_val = 0
        try:
            t = Thread(target=self.sendpacket_thread)
            t.daemon = True
            t.start()
            
            while True:
                # 키 읽기 블록 상태(Block) 
                # 키 입력이 들어오기 전까지 무조건 대기
                try:       
                    evbuf = self.__jsdev.read(8)
                    # 이벤트가 발생했다면
                    if evbuf:
                        # 시간, 값, 타입, 번호 등으로 가져옴
                        time, value, type, number = struct.unpack('IhBB', evbuf)

                        # type이 0x01 버튼이 눌렸거나 떨어졌을때이다.
                        if type & 0x01:
                            # number 값으로 해당 버튼 이름 가져오기
                            button = self.button_map[number]
                            self.button_states[button] = value
                            result_button = self.compare_button_data(button)
                            
                            # 버튼을 누르면
                            if value:
                                # 누른 버튼의 정보를 가져옴
                                # print(result_button)
                            
                                if result_button == 'OFF' :
                                    self.__ESTOP = 'OFF'
                                elif result_button == 'ON' :
                                    self.__ESTOP = 'ON'
                                elif result_button == 'WFORWARD':
                                    self.__WHEEL = 'WFORWARD'
                                elif result_button == 'WFOURTH':
                                    self.__WHEEL = 'WFOURTH'                        
                                elif result_button == 'WBACKWARD':
                                    self.__WHEEL = 'WBACKWARD'
                        
                        # type이 0x02이면 축이 이동한 상태이다.
                        if type & 0x02:
                            # number로 해당 축의 이름 가져오기
                            axis = self.axis_map[number]
                            speed_value = [0x00, 0x00]
                            steer_value = [0x00, 0x00]
                            exp_value   = [0x00,0x00]
                            
                            '''
                            v 1.0.0 --> excel, brake 동시에 눌려지면 안됨.
                            excel 값 exp 이용 (점점 증가할 수 있도록)
                            '''
                            # excel
                            if axis == 'z':
                                # 값을 32767로 나눠서 0 또는 1, -1 로 표시
                                # 축 값이 -32767 ~ 0 ~ 32767 사이 값으로 표시되는 데
                                # 0보다 큰지 작은지 0인지를 구분하기 위함이다.
                                # 상태값(0, 1, -1)을 저장
                                # 0 ~ 65534
                                axis_val = int(value) + 32767
                                # print("%s: %.3f \t" % (axis, axis_val), end="")
                                speed_value = axis_val.to_bytes(2, byteorder="little", signed=False)
                                self.__pt.speed_data[0] = speed_value[0]
                                self.__pt.speed_data[1] = speed_value[1]

                            # brake
                            elif axis == 'rz':
                                # 값을 32767로 나눠서 0 또는 1, -1 로 표시
                                # 축 값이 -32767 ~ 0 ~ 32767 사이 값으로 표시되는 데
                                # 0보다 큰지 작은지 0인지를 구분하기 위함이다.
                                # 상태값(0, 1, -1)을 저장
                                # 0 ~ 65534
                                axis_val = int(value) + 32767
                                # print("%s: %.3f \t" % (axis, axis_val), end="")
                                brake_value = axis_val.to_bytes(2, byteorder="little", signed=False)
                                self.__pt.brake_data[0] = brake_value[0]
                                self.__pt.brake_data[1] = brake_value[1]

                            # # excel
                            # if axis == 'z':
                            #     # 값을 32767로 나눠서 0 또는 1, -1 로 표시
                            #     # 축 값이 -32767 ~ 0 ~ 32767 사이 값으로 표시되는 데
                            #     # 0보다 큰지 작은지 0인지를 구분하기 위함이다.
                            #     # 상태값(0, 1, -1)을 저장
                            #     # 0 ~ 65534
                            #     axis_val = int(value) + 32767
                            #     # print("%s: %.3f \t" % (axis, axis_val), end="")
                            #     speed_value = axis_val.to_bytes(2, byteorder="little", signed=False)
                            #     self.__pt.speed_data[0] = speed_value[0]
                            #     self.__pt.speed_data[1] = speed_value[1]

                            # # brake
                            # elif axis == 'rz':
                            #     # 값을 32767로 나눠서 0 또는 1, -1 로 표시
                            #     # 축 값이 -32767 ~ 0 ~ 32767 사이 값으로 표시되는 데
                            #     # 0보다 큰지 작은지 0인지를 구분하기 위함이다.
                            #     # 상태값(0, 1, -1)을 저장
                            #     # 0 ~ 65534
                            #     axis_val = int(value) + 32767
                            #     # print("%s: %.3f \t" % (axis, axis_val), end="")
                            #     brake_value = axis_val.to_bytes(2, byteorder="little", signed=False)
                            #     self.__pt.brake_data[0] = brake_value[0]
                            #     self.__pt.brake_data[1] = brake_value[1]
                            #     self.__pt.speed_data[0] = 0
                            #     self.__pt.speed_data[1] = 0

                            # steer
                            elif axis == 'rx':
                                axis_val = int(value)
                                if axis_val == 0:
                                    exp_val = 0
                                else:     
                                    exp_val = int((pow((axis_val/32767),2) * 32767 * (axis_val / abs(axis_val))))
                                # print("axis_val : {0}, exp_val : {1}".format(axis_val,int(exp_val)))
                                # print("%s: %.3f \t" % (axis, axis_val), end="")
                                steer_value = axis_val.to_bytes(2, byteorder="little", signed=True)
                                exp_value = exp_val.to_bytes(2, byteorder="little", signed=True)
                                self.__pt.steer_data[0] = steer_value[0]
                                self.__pt.steer_data[1] = steer_value[1]
                                self.__pt.steer_data[2] = exp_value[0]
                                self.__pt.steer_data[3] = exp_value[1]

                            elif axis == 'hat0y':
                                axis_val = int(value) / 32767
                                if axis_val == -1.0:
                                    self.__GEAR = 'GFORWARD'
                                elif axis_val == 1.0:
                                    self.__GEAR = 'GBACKWARD'

                            elif axis == 'hat0x':
                                axis_val = int(value) / 32767
                                if axis_val :
                                    self.__GEAR = 'GNEUTRAL'
                                           
                # 조이스틱 연결이 끊어지면 재 연결 시도
                except OSError:
                    self.reconect()
                except IndexError:
                    self.reconect()
                except KeyboardInterrupt:
                    t.join()
                    print(" ctrl + c pressed !!")
                    print("exit .. ")
                    exit(0)

        except (KeyboardInterrupt, SystemExit):
            print ('\n! Received keyboard interrupt, quitting threads.\n')
            exit(0)

            
    def reconect(self):
        # print("test")
        try:
            # self.isConnect_joy = False
            print("조이스틱을 재 연결합니다.")
            print('Opening %s...' % self.__fn)
            self.__jsdev = open(self.__fn, 'rb')

            if self.__jsdev:
                print("조이스틱 체크 성공")
                self.__isConnect_joy = True

        except:
            self.__isConnect_joy = False
            print("조이스틱을 다시 연결하세요..")
        sleep(1)
   
    def compare_button_data(self, data):
        buttons = {
            'tl'        :'OFF', 
            'tr'        :'ON', 
            'y'         :'WFORWARD', 
            'a'         :'WBACKWARD',
            'x'         :'WFOURTH',
        }         
        return buttons.get(data,"Invalid button")
                       