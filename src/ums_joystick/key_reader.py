#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created Date: May 15. 2020
Copyright: UNMAND SOLUTION
Author: Dae Jong Jin 
Description: Logitech Joystick key reader
'''
"""
*************** ISUE - UPDATE ***************
10 / 14 세종시 조종기 테스트
이슈 1. 조종기 선 연결 불안정 (연결 선 후크 마모현상으로 자주 연결이 끊어지는 현상이 발생함.)
이슈 2. 민감도 조절 (올라가는 속도, 내려가는 속도)
이슈 3. 버튼 누른 상태에서 선 연결이 끊어지면 추후에 선 연결 시 전 값이 남아있어 출발할때 움직이는 현상 발생 --> 매인 컨트롤러 : VCU 보드 쪽 문제

10 / 16 카트리 조종기 테스트
업데이트 1. 민감도 조절 (기존 쓰레드 이용 -> Lock 사용)

10 / 21 조종기 횡방향 테스트
업데이트 1. 횡방향 민감도 조절 (2차함수 이용)

11 / 05 세종시 4호차, 6호차 최종 업데이트

11 / 24 아이솔 3, 4호차 업데이트 (조종기 민감도 이슈)

12 / 04 크루즈 모드 추가 및 조종기 버그 수정

12 / 15 X-Box 조종기 모드 추가 및 파라미터 변경

01 / 11 BETAFPV 조종기 모드 추가
*********************************************
"""

import os
import struct
import array
from time import sleep
from fcntl import ioctl
import sys
from threading import Thread, Condition
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

    """
    CLASS VARIABLES
    """
    ACCEL_MAX   = 40000 #50000
    ACCEL_Threshold = 25000
    ACCEL_RATIO = 1.0

    DELTA_PLUS  = 100 #100 
    DELTA_MINUS = 200 #100 

    APS_VAL     = 2500 
    CRUISE_VAL  = 5000
    
    STEER_RATIO = 0.8
    STEER_LIMIT = 32700 # 32000  

    def __init__(self, serial, port, mode):

        self.__serial = serial
        self.__port = port
        self.__test_mode = mode
        self.__num_buttons = None
        self.__num_axes = None
        self.__jsdev = None
        self.__fn = '/dev/input/js0'
        self.__writer = UMDSerialWriter(serial=self.__serial, port=self.__port, mode=self.__test_mode)
        self.__pt = PacketProtocol()
        self.__ESTOP = 'OFF'
        self.__GEAR = 'GNEUTRAL'
        self.__WHEEL = 'WFORWARD'

        self.isXbox = False
        self.__isConnect_joy = True
        self.__isThread = False
        self.__isCruise = False
        self.__initCruise = True

        self.speed_value = [0x00, 0x00]
        self.brake_value = [0x00, 0x00]
        self.steer_value = [0x00, 0x00]
        self.exp_value = [0x00, 0x00]

        self.accel_val = 0 # 실제 accel raw data
        self.brake_val = 0
        self.steer_val = 0
        self.pre_exp_data = 0
        self.exp_val = 0
        self.pre_accel_val = 0

        self.cruise_val = 0

        self.__aps_val = self.APS_VAL
        self.current_val = self.accel_val + self.__aps_val
        self.speed_val = self.accel_val + self.__aps_val

        self.condition = Condition()

    # joystick connection checking
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
            sleep(0.2)

    def joy_name_read(self):
        # 드라이버로부터 조이스틱 이름 가져오기
        buf = array.array('B', [0] * 64)
        ioctl(self.__jsdev, 0x80006a13 +
              (0x10000 * len(buf)), buf)  # JSIOCGNAME(len)
        self.__js_name = buf.tobytes().rstrip(b'\x00').decode('utf-8')  # 0x00 비어있는 값 제거
        print('Device name: %s' % self.__js_name)

        if "Microsoft" in self.__js_name or "Generic" in self.__js_name:
            self.isXbox = True
            return True
        elif "BetaFPV" in self.__js_name:
            self.isXbox = False
            return True
        else:
            return False

    def axis_read(self):
        # 드라이버로부터 축 개수 가져오기
        buf = array.array('B', [0])
        ioctl(self.__jsdev, 0x80016a11, buf)  # JSIOCGAXES
        # x,y 축이면 2
        num_axes = buf[0]

        # Get the axis map.
        # 키 맵핑
        buf = array.array('B', [0] * 0x40)
        ioctl(self.__jsdev, 0x80406a32, buf)  # JSIOCGAXMAP
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
        ioctl(self.__jsdev, 0x80016a12, buf)  # JSIOCGBUTTONS
        # 버튼이 두 개면 2
        num_buttons = buf[0]

        # Get the button map.
        # 축과 마찬가지로 버튼 번호로 이름을 가져온다.
        buf = array.array('H', [0] * 200)
        ioctl(self.__jsdev, 0x80406a34, buf)  # JSIOCGBTNMAP

        for btn in buf[:num_buttons]:
            btn_name = button_names.get(btn, 'unknown(0x%03x)' % btn)
            self.button_map.append(btn_name)
            self.button_states[btn_name] = 0

    def control_thread(self):
        # 상태를 잠금으로 변경 후 즉시 반환
        while True :
            self.condition.acquire()
            # accel button을 누를 경우
            if self.pre_accel_val < self.accel_val:
                self.__initCruise = True
                # accel axis value가 될 때 까지 0.02초 마다
                while self.current_val <= self.accel_val:
                    # GEAR가 전진일 경우 DELTA PLUS 만큼 증가
                    if self.__GEAR == 'GFORWARD':
                        if self.current_val <= self.ACCEL_Threshold:
                            self.current_val = self.current_val + self.DELTA_PLUS
                        else:
                            self.current_val = (int)(self.current_val + self.DELTA_PLUS / 4)
                    # GEAR가 후진일 경우 DELTA PLUS * 2 만큼 증가
                    elif self.__GEAR == 'GBACKWARD':
                        self.current_val = self.current_val + (self.DELTA_PLUS * 2)
                    # 액셀 최댓값 설정 (60000)
                    else:
                        self.current_val = 0
                    if self.current_val > self.ACCEL_MAX:
                        self.current_val = self.ACCEL_MAX
                    sleep(0.02)
            
            # accel button을 뗄 경우
            elif self.pre_accel_val > self.accel_val:
                self.__initCruise = True
                while self.current_val >= self.accel_val:
                    if self.__GEAR == 'GFORWARD':
                        self.current_val = self.current_val - self.DELTA_MINUS
                    elif self.__GEAR == 'GBACKWARD':
                        self.current_val = self.current_val - (self.DELTA_MINUS * 3)                   
                    else:
                        self.current_val = 0
                    if self.current_val < 0:
                        self.current_val = self.accel_val + self.__aps_val
                    sleep(0.02)
            else:
                if self.accel_val > self.speed_val:
                    self.accel_val += 1
                else:
                    self.accel_val -= 1

            self.condition.notify()
            # 쓰레드 잠김 해제
            self.condition.release()

    def sendpacket_thread(self):
        try:
            control_t = Thread(target=self.control_thread)
            control_t.daemon = True
            control_t.start()
            while True:        
                if self.__isConnect_joy:
                    self.__pt.count_alive()

                    self.limitAPS()
                    self.limitAccel()

                    # brake 값 0일 경우
                    if self.brake_val == 0:
                        if self.__isCruise:
                            self.speed_val = self.cruise_val
                            self.current_val = self.cruise_val
                        else:
                            self.__aps_val = self.APS_VAL
                            self.speed_val = self.current_val
                    # 0이 아닐 경우
                    else:
                        self.cruise_val = self.APS_VAL
                        self.current_val = 0
                        self.speed_val = 0

                    # ESTOP 걸릴 경우, 기어가 중립일 경우
                    if self.__ESTOP == 'ON' or self.__GEAR =="GNEUTRAL":
                        self.__isCruise = False
                        self.cruise_val = 0
                        self.speed_val = 0
                        self.current_val = 0

                    if self.steer_val == 0:
                        self.exp_val = 0
                    else:
                        self.limitSteer()
                    
                    self.value2bytes()
                    packet = self.__pt.makepacket(ESTOPMODE=self.__ESTOP, GEARMODE=self.__GEAR, WHEELMODE=self.__WHEEL)

                    # print("tread mode : {} ". format(self.__isThread), end="")
                    # print("cruise mode : {} ". format(self.__isCruise), end="")
                    # print("init mode : {} ". format(self.__initCruise), end="")
                    # print("current_val : {} ". format(self.current_val), end="")
                    # print("cruise_val : {} ". format(self.cruise_val), end="")
                  
                    # print("speed_val : {0} ".format(self.speed_val), end=" ")
                    # print("steer_val : {0} ".format(self.steer_val), end=" ")
                    # print("fitting_steer_val : {0} ".format(self.exp_val), end=" ")
                    if self.__test_mode:
                        print("packet : {0}".format(packet))
                        
                    self.__writer.run(packet)

                else:
                    self.reset_value()
                    print("not joystick connect")
                    sleep(0.5)

                self.pre_accel_val = self.accel_val
                sleep(0.02)  # 50Hz

        except KeyboardInterrupt:
            control_t.join()
        except Exception as e:
            print(e)
            
    def reset_value(self):
        self.accel_val = 0
        self.current_val  = 0
        self.speed_val = 0
        self.brake_val = 0
        self.steer_val = 0
        self.cruise_val = self.APS_VAL
        self.exp_val = 0

        self.speed_value = [0x00, 0x00]
        self.brake_value = [0x00, 0x00]
        self.steer_value  = [0x00, 0x00]
        self.exp_value  = [0x00, 0x00]

        self.axis_states = {}
        self.button_states = {}
        self.axis_map = []
        self.button_map = []
        self.origin_axis_states = {}
        self.origin_button_states = {}
        self.origin_axis_map = []
        self.origin_button_map = []

    def joy_main_event(self):
        # Main event loop
        # 키 이벤트 처리
        button = None
        axis = 0
        # axis_val = 0
        # exp_val = 0

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
                        _, value, type, number = struct.unpack(
                            'IhBB', evbuf)
                        
                    self.APS_VAL = JoystickReader.APS_VAL if self.isXbox else 0

                    if self.isXbox:
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
                                if button == 'mode':
                                    self.__ESTOP = 'ON'

                                if button == 'start':
                                    self.__isCruise = True

                                    if self.__initCruise:
                                        self.cruise_val = self.speed_val
                                        self.__initCruise = False
                                    else:
                                        self.cruise_val = self.cruise_val + self.CRUISE_VAL

                                    if self.cruise_val > self.ACCEL_MAX:
                                        self.cruise_val = self.ACCEL_MAX

                                elif button == 'select':
                                    self.__isCruise = True

                                    if self.__initCruise:
                                        self.cruise_val = self.speed_val
                                        self.__initCruise = False
                                    else:
                                        self.cruise_val = self.cruise_val - int(self.CRUISE_VAL / 2)
                                    # else:

                                    if self.cruise_val < self.__aps_val:
                                        self.cruise_val = self.__aps_val

                                if result_button == 'OFF':
                                    self.__ESTOP = 'OFF'
                                elif result_button == 'ON':
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
                            # excel
                            if axis == 'z':
                                self.accel_val = int((value + 32767) * self.ACCEL_RATIO)  
                                # print("%s: %.3f \t" % (axis, axis_val), end="")

                            # brake
                            if axis == 'rz':
                                self.brake_val = int(value) + 32767
                                # print("%s: %.3f \t" % (axis, axis_val), end="")
                                # self.brake_value = self.brake_val.to_bytes(2, byteorder="little", signed=False)
                                # self.__pt.brake_data[0] = self.brake_value[0]
                                # self.__pt.brake_data[1] = self.brake_value[1]

                            # steer
                            elif axis == 'rx':
                                self.steer_val = int(value)  
                                if abs(self.steer_val) < 1000:
                                    self.steer_val = 0

                            elif axis == 'hat0y':
                                axis_val = int(value) / 32767
                                if axis_val == -1.0:
                                    self.__GEAR = 'GFORWARD'
                                elif axis_val == 1.0:
                                    self.__GEAR = 'GBACKWARD'

                            elif axis == 'hat0x':
                                axis_val = int(value) / 32767
                                if axis_val:
                                    self.__GEAR = 'GNEUTRAL'
                    else:
                        if type & 0x02:
                            axis = self.axis_map[number]
                            # excel or brake
                            if axis == 'z':
                                if value > 0:
                                    self.accel_val = int(value * self.ACCEL_RATIO) 
                                elif value < 0:
                                    self.brake_val = int(value) + 65534
                                else:
                                    self.accel_val = 0
                                    self.brake_val = 0
                            # steer
                            elif axis == 'x':
                                self.steer_val = int(value)  
                                # if abs(self.steer_val) < 1000:
                                #     self.steer_val = 0
                            # Gear
                            elif axis == 'rz':
                                axis_val = int(value) / 32767
                                if axis_val == -1.0:
                                    self.__GEAR = 'GFORWARD'
                                elif axis_val == 1.0:
                                    self.__GEAR = 'GBACKWARD'
                                elif axis_val == 0.0:
                                    self.__GEAR = 'GNEUTRAL'
                            # Estop
                            elif axis == 'ry':
                                axis_val = int(value) / 32767
                                if axis_val == -1.0:
                                    self.__ESTOP = 'ON'
                                else:
                                    self.__ESTOP = 'OFF'
                            # Wheel Mode
                            elif axis == 'trottle':
                                axis_val = int(value) / 32767
                                if axis_val == -1.0:
                                    self.__WHEEL = 'WFORWARD'
                                elif axis_val == 0:
                                    self.__WHEEL = 'WFOURTH'
                                elif axis_val == 1.0:
                                    self.__WHEEL = 'WBACKWARD'
                # 조이스틱 연결이 끊어지면 재 연결 시도
                except OSError:
                    self.reconect()
                    sleep(0.2)
                except IndexError as e:
                    print (e)
                    # self.__ESTOP = 'ON'
                    self.reconect()
                    sleep(0.2)
                except KeyboardInterrupt:
                    t.join()
                    print(" ctrl + c pressed !!")
                    exit(0)

        except (KeyboardInterrupt, SystemExit):
            print ('\n! Received keyboard interrupt, quitting threads.\n')
            exit(0)

    def limitAPS(self):
        if self.__aps_val < self.APS_VAL:
            self.__aps_val = self.APS_VAL
        elif self.__aps_val > self.ACCEL_MAX:
            self.__aps_val = self.ACCEL_MAX
    
    def limitAccel(self):
        if self.accel_val == 0:
            self.__isThread = False
        else:
            self.__isCruise = False
            self.__isThread = True

        if self.accel_val < 0 :
            self.accel_val = 0
        elif self.accel_val !=0:
            self.cruise_val = self.APS_VAL

        if self.current_val < self.__aps_val:
            self.current_val = self.__aps_val

    def limitSteer(self):
        self.exp_val = (self.steer_val// 10) * 10
        if self.exp_val > self.STEER_LIMIT:
            self.exp_val = self.STEER_LIMIT
        elif self.exp_val < -self.STEER_LIMIT:
            self.exp_val = -self.STEER_LIMIT

    def value2bytes(self):
        self.speed_value = self.speed_val.to_bytes(
            2, byteorder="little", signed=False)
        self.brake_value = self.brake_val.to_bytes(
            2, byteorder="little", signed=False)
        self.steer_value = self.steer_val.to_bytes(
            2, byteorder="little", signed=True)
        self.exp_value = self.exp_val.to_bytes(
            2, byteorder="little", signed=True)

        self.__pt.speed_data[1] = self.speed_value[1]
        self.__pt.brake_data[0] = self.brake_value[0]
        self.__pt.brake_data[1] = self.brake_value[1]
        self.__pt.steer_data[0] = self.steer_value[0]
        self.__pt.steer_data[1] = self.steer_value[1]
        self.__pt.steer_data[2] = self.exp_value[0]
        self.__pt.steer_data[3] = self.exp_value[1]

    def reconect(self):
        # print("test")
        try:
            # self.isConnect_joy = False
            print("조이스틱을 재 연결합니다.")
            print('Opening %s...' % self.__fn)
            self.isXbox = False
            self.__jsdev = open(self.__fn, 'rb')

            self.joy_open()
            isCorrect = self.joy_name_read()
            if isCorrect:

            # if self.__jsdev:
                # self.joy_name_read()
                self.axis_read()
                self.button_read()
                self.__isConnect_joy = True
        except:
            self.__isConnect_joy = False
            print("조이스틱을 다시 연결하세요..")
        sleep(0.2)

    def compare_button_data(self, data):
        buttons = {
            'tl': 'OFF',
            'tr': 'ON',
            'y': 'WFORWARD',
            'a': 'WBACKWARD',
            'x': 'WFOURTH',
        }
        return buttons.get(data, "Invalid button")
