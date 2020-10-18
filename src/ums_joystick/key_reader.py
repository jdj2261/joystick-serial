#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created Date: May 15. 2020
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
    STEER_PARAM = 100

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
        self.__cnt = 0

        self.current_value = [0x00, 0x00]
        self.current_value2 = [0x00, 0x00]
        self.steer_value = [0x00, 0x00]
        self.exp_value   = [0x00,0x00]
        self.brake_value = [0x00, 0x00]
        self.speed_val = 0
        self.brake_val = 0
        self.steer_val = 0
        self.exp_val = 0
        self.pre_val=0
        self.current_val =  self.speed_val + self.APS_VAL
        self.current_val2 = self.speed_val + self.APS_VAL
        self.current_test = self.speed_val + self.APS_VAL

        self.test = 0

        self.condition = Condition()

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
        ioctl(self.__jsdev, 0x80006a13 + (0x10000 * len(buf)), buf) # JSIOCGNAME(len)
        js_name = buf.tobytes().rstrip(b'\x00').decode('utf-8') # 0x00 비어있는 값 제거 
        print('Device name: %s' % js_name)

        if "Microsoft" in js_name:
            return True
        else:
            return False
            
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

    def insert(self):
        value = self.speed_val 
        return value 

    # def insert2(self):
    #     value = self.current_test   
    #     return value 

    # def insert3(self):
    #     value = self.current_val
    #     return value 

    def insert2(self):
        value = self.exp_val
        return value 

    def insert3(self):
        value = self.steer_val
        return value 

    def test_thread(self):
        while True:
            # self.condition.acquire()
            if self.pre_val < self.speed_val:
                while self.current_val2 <= self.speed_val:
                    print("PLUS!!!")
                    if self.__GEAR == 'GFORWARD':
                        self.current_val2 = self.current_val2 + self.DELTA_PLUS
                    elif self.__GEAR == 'GBACKWARD':
                        self.current_val2 = self.current_val2 + ( self.DELTA_PLUS * 2)
                    # else:
                        # self.current_val2 = self.DELTA_PLUS
                    
                    if self.current_val2 >= 60000 :
                        self.current_val2 = 60000
                    # print(self.current_val, end=" ")
                    self.current_value2 = self.current_val2.to_bytes(2, byteorder="little", signed=False)
                    sleep(0.02)
                # self.current_val = self.speed_val
            elif self.pre_val >= self.speed_val:
                
                while self.current_val2 >= self.speed_val:
                    if self.__GEAR == 'GFORWARD':
                        self.current_val2 = self.current_val2 - self.DELTA_MINUS
                    elif self.__GEAR == 'GBACKWARD':
                        self.current_val2 = self.current_val2 - ( self.DELTA_MINUS * 2)
                    # else :
                    #     self.current_val2 = 0
                    # self.current_val2 = self.current_val2 - self.DELTA_MINUS

                    if self.current_val2 < 0:
                        self.current_val2 = self.speed_val + self.APS_VAL
                    # print(self.current_val, end=" ")
                    self.current_value2 = self.current_val2.to_bytes(2, byteorder="little", signed=False)
                    sleep(0.02)
            # self.condition.notify()
            # self.condition.release()
    def plot_thread(self):

        fig = plt.figure(figsize=(10,8))     #figure(도표) 생성
        # ax1 = plt.gca()
        
        ax1 = plt.subplot(311, xlim=(0, 50), ylim=(0, 1024))
        ax2 = plt.subplot(312, xlim=(0, 50), ylim=(0, 1024))
        ax3 = plt.subplot(313, xlim=(0, 50), ylim=(0, 1024))

        # ax2 = ax1.twinx()
        ax1.grid(True)
        ax2.grid(True)
        ax3.grid(True)

        # y축에 표현할 값을 반환해야하고 scope 객체 선언 전 선언해야함.

        # 객체 생성
        scope = Scope(ax1,self.insert, ystart = 0, ymax = 65535, title = "origin", color='b')
        scope2 = Scope(ax2,self.insert2, ystart = -65535, ymax = 65535, title = "result", color='r')
        scope3 = Scope(ax3,self.insert3, ystart = -65535, ymax = 65535, title = "change", color='y')    
        # update 매소드 호출
        ani = animation.FuncAnimation(fig, scope.update,interval=10,blit=True)
        ani2 = animation.FuncAnimation(fig, scope2.update,interval=10,blit=True)
        ani3 = animation.FuncAnimation(fig, scope3.update,interval=10,blit=True)
        plt.show()

    def sendpacket_thread(self):
        try:
            t = Thread(target=self.test_thread)
            t.daemon = True
            t.start()

 
        except RuntimeError :
            pass
        
        while True:        # alive count (0 ~ 255)
            # send packet
            if self.__isConnect_joy:
                self.__pt.count_alive()

                # if self.pre_val != self.speed_val :
                #     if abs(self.pre_val-self.speed_val) > 10 :
                        # self.current_val = self.pre_val

                self.current_value = self.current_val.to_bytes(2, byteorder="little", signed=False)
                self.current_value2 = self.current_val2.to_bytes(2, byteorder="little", signed=False)
                # else:
                #     pass

                # self.current_val = self.pre_val

                self.brake_value = self.brake_val.to_bytes(2, byteorder="little", signed=False)
                self.steer_value = self.steer_val.to_bytes(2, byteorder="little", signed=True)
                self.exp_value = self.exp_val.to_bytes(2, byteorder="little", signed=True)

                # brake 잡지 않은 상태 --> APS 해제
                if self.brake_val == 0:
                    if self.current_val2 < self.APS_VAL:
                        self.current_val2 = self.APS_VAL
                    
                    self.current_test = self.current_val2
                # 잡으면 APS 해제
                else :
                    self.current_val2 = 0
                    self.current_test = 0

                print(" TEST : {}".format(self.current_test))
                    


                if self.__ESTOP == 'ON':
                    self.current_test = 0

                self.current_test_value = self.current_test.to_bytes(2, byteorder="little", signed=False)
                
                self.__pt.speed_data[0] = self.current_test_value[0]
                self.__pt.speed_data[1] = self.current_test_value[1]
                self.__pt.brake_data[0] = self.brake_value[0]
                self.__pt.brake_data[1] = self.brake_value[1]
                self.__pt.steer_data[0] = self.steer_value[0]
                self.__pt.steer_data[1] = self.steer_value[1]
                self.__pt.steer_data[2] = self.exp_value[0]
                self.__pt.steer_data[3] = self.exp_value[1]

                packet = self.__pt.makepacket(ESTOPMODE=self.__ESTOP, GEARMODE=self.__GEAR, WHEELMODE=self.__WHEEL)

                print("accel val : {0}".format(self.current_test), end=" ")
                print("steer val : {0}".format(self.steer_val), end=" ")
                print("exp val : {0}".format(self.exp_val), end=" ")
                print("packet : {0}".format(packet))
                self.__writer.run(packet)
            else:
                self.reset_value()
                print("not joystick connect")
                sleep(0.1)

            self.pre_val = self.speed_val
            sleep(0.02) # 50Hz

    def reset_value(self):
        self.speed_val = 0
        self.current_val  = 0
        self.current_val2 = 0
        self.current_test = 0
        self.brake_val = 0
        self.steer_val = 0
        self.exp_val = 0

        self.current_value = [0x00, 0x00]
        self.current_value2 = [0x00, 0x00]
        self.brake_value = [0x00, 0x00]
        self.steer_value  = [0x00, 0x00]
        self.exp_value  = [0x00, 0x00]

    def joy_main_event(self):
        # Main event loop
        # 키 이벤트 처리
        button = None
        axis = 0
        # axis_val = 0
        # exp_val = 0
        try:
            t = Thread(target=self.sendpacket_thread)
            t2 = Thread(target=self.plot_thread)

            t.daemon = True
            t.start()

            t2.daemon = True
            t2.start()
            
            while True:
                # 키 읽기 블록 상태(Block) 
                # 키 입력이 들어오기 전까지 무조건 대기
                try:       
                    evbuf = self.__jsdev.read(8)
                    # 이벤트가 발생했다면
                    if evbuf:
                        # 시간, 값, 타입, 번호 등으로 가져옴
                        _, value, type, number = struct.unpack('IhBB', evbuf)

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
                                if button == 'mode' :
                                    self.__ESTOP = 'ON'      
                                # elif button == 'select':
                                #     self.APS_VAL -= 250
                                #     if self. reset_value <= 2500:
                                #         self.APS_VAL = 2500
                                #     pass
                                # elif button == 'start':
                                #     pass
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
                            # speed_value = [0x00, 0x00]
                            # steer_value = [0x00, 0x00]
                            # exp_value   = [0x00,0x00]
                            
                            # excel
                            if axis == 'z':
                                """
                                값을 32767로 나눠서 0 또는STEER_PARAM
                                0 ~ 65534
                                """
                                self.speed_val = int(value) + 32767
                                # print("%s: %.3f \t" % (axis, axis_val), end="")
                                # self.speed_value = self.speed_val.to_bytes(2, byteorder="little", signed=False)
                                # self.__pt.speed_data[0] = self.speed_value[0]
                                # self.__pt.speed_data[1] = self.speed_value[1]

                            # brake
                            if axis == 'rz':
                                """
                                값을 32767로 나눠서 0 또는 1, -1 로 표시
                                축 값이 -32767 ~ 0 ~ 32767 사이 값으로 표시되는 데
                                0보다 큰지 작은지 0인지를 구분하기 위함이다.
                                상태값(0, 1, -1)을 저장
                                0 ~ 65534
                                """
                                self.brake_val = int(value) + 32767
                                # print("%s: %.3f \t" % (axis, axis_val), end="")
                                # self.brake_value = self.brake_val.to_bytes(2, byteorder="little", signed=False)
                                # self.__pt.brake_data[0] = self.brake_value[0]
                                # self.__pt.brake_data[1] = self.brake_value[1]
                            
                            # steer
                            elif axis == 'rx':
                                self.steer_val = int(value)

                                if self.steer_val == 0:
                                    self.exp_val = 0
                                else :     
                                    self.exp_val = int((pow((self.steer_val/32767),2) * 32767 * (self.steer_val / abs(self.steer_val))))
                                    self.exp_val = self.exp_val / 32767
                                    self.exp_val = pow(self.exp_val, 3) * 32767

                                    if self.exp_val < self.STEER_PARAM:
                                        self.exp_val = int(self.exp_val)
                                    else:   
                                        self.exp_val  = int(self.exp_val  // self.STEER_PARAM) * self.STEER_PARAM

                                if self.exp_val  > 32000 :
                                    self.exp_val  = 32000
                                elif self.exp_val  < -32000:
                                    self.exp_val  = -32000
                
                                # print("steer_val : {0}, exp_val : {1}".format(self.steer_val,int(self.exp_val)))
                                # print("%s: %.3f \t" % (axis, axis_val), end="")
                                # self.steer_value = self.steer_val.to_bytes(2, byteorder="little", signed=True)
                                # self.exp_value = self.exp_val.to_bytes(2, byteorder="little", signed=True)
                                # self.__pt.steer_data[0] = self.steer_value[0]
                                # self.__pt.steer_data[1] = self.steer_value[1]
                                # self.__pt.steer_data[2] = self.exp_value[0]
                                # self.__pt.steer_data[3] = self.exp_value[1]

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
                    sleep(0.2)
                except IndexError as e:
                    print (e)
                    self.__ESTOP = 'ON'
                    self.reconect()
                    sleep(0.2)
                except KeyboardInterrupt:
                    t.join()
                    print(" ctrl + c pressed !!")
                    print("exit .. ")
                    exit(0)
                # except Exception:
                #     self.reconect()
                #     sleep(0.5)

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
        sleep(0.2)
   
    def compare_button_data(self, data):
        buttons = {
            'tl'        :'OFF', 
            'tr'        :'ON', 
            'y'         :'WFORWARD', 
            'a'         :'WBACKWARD',
            'x'         :'WFOURTH',
        }         
        return buttons.get(data,"Invalid button")
                       
