#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, struct, array
from fcntl import ioctl

from key_names import axis_names, button_names

class JoystickReader():
    def __init__(self):
        self.__num_buttons = None
        self.__num_axes = None
        self.__jsdev = None

    def joy_check(self, dir):
        for fn in os.listdir(dir):
            if fn.startswith('js'):
                print(' /dev/input/%s' %(fn))

    def joy_open(self, dir):
        print('Opening %s...' % dir)
        self.__jsdev = open(dir, 'rb')

    def joy_read(self):
        # Get the device name.
        #buf = bytearray(63)
        # 배열 선언
        # 바이트(unsigned char)형으로 64개 생성
        buf = array.array('B', [0] * 64)

        # 드라이버로부터 조이스틱 이름 가져오기
        ioctl(self.__jsdev, 0x80006a13 + (0x10000 * len(buf)), buf) # JSIOCGNAME(len)
        js_name = buf.tobytes().rstrip(b'\x00').decode('utf-8')
        print('Device name: %s' % js_name)

        # Get number of axes and buttons.
        # 드라이버로부터 축 개수 가져오기
        buf = array.array('B', [0])
        ioctl(self.__jsdev, 0x80016a11, buf) # JSIOCGAXES
        # x,y 축이면 2
        self.__num_axes = buf[0]

        # 드라이버로부터 버튼 개수 가져오기
        buf = array.array('B', [0])
        ioctl(self.__jsdev, 0x80016a12, buf) # JSIOCGBUTTONS
        # 버튼이 두 개면 2
        self.__num_buttons = buf[0]        

    def joy_mapping(self):
        # Get the axis map.
        # 키 맵핑
        buf = array.array('B', [0] * 0x40)
        ioctl(jsdev, 0x80406a32, buf) # JSIOCGAXMAP
        # 읽은 값에서 총 축 수만큼 loop 돌림
        for axis in buf[:self.__num_axes]:
            # axis_names의 첫번째 번호와 같은 이름을 가져온다.
            # 예를들어 axis가 0이면 axis_names에서 0x00 > 'x'를 가져오고
            # axis가 1이면 axis_names에 0x01 > 'y'를 가져오기 된다.
            axis_name = axis_names.get(axis, 'unknown(0x%02x)' % axis)
            axis_map.append(axis_name)
            # 해당 축 0.0 으로 초기화 
            axis_states[axis_name] = 0.0

        # Get the button map.
        # 축과 마찬가지로 버튼 번호로 이름을 가져온다.
        buf = array.array('H', [0] * 200)
        ioctl(jsdev, 0x80406a34, buf) # JSIOCGBTNMAP

        for btn in buf[:self.__num_buttons]:
            btn_name = button_names.get(btn, 'unknown(0x%03x)' % btn)
            button_map.append(btn_name)
            button_states[btn_name] = 0

        print('%d axes found: %s' % (self.__num_axes, ', '.join(axis_map)))
        print('%d buttons found: %s' % (self.__num_buttons, ', '.join(button_map)))





# # Main event loop
# # 키 이벤트 처리
# while True:
#     # 키 읽기 블록 상태(Block) 
#     # 키 입력이 들어오기 전까지 무조건 대기
#     evbuf = jsdev.read(8)
#     # 이벤트가 발생했다면
#     if evbuf:
#         # 시간, 값, 타입, 번호 등으로 가져옴
#         time, value, type, number = struct.unpack('IhBB', evbuf)

#         # type이 0x80이면 장치 초기 상태이다.
#         if type & 0x80:
#              print("(initial)", end="")

#         # type이 0x01 버튼이 눌렸거나 떨어졌을때이다.
#         if type & 0x01:
#             # number 값으로 해당 버튼 이름 가져오기
#             button = button_map[number]
#             if button:      
#                 # 해당 버튼 상태(button_states)에 value 값으로 변경          
#                 button_states[button] = value
#                 if value:
#                     print("%s pressed" % (button))
#                 else:
#                     print("%s released" % (button))

#         # type이 0x02이면 축이 이동한 상태이다.
#         if type & 0x02:
#             # number로 해당 축의 이름 가져오기
#             axis = axis_map[number]
#             if axis:
#                 # 값을 32767로 나눠서 0 또는 1, -1 로 표시
#                 # 축 값이 -32767 ~ 0 ~ 32767 사이 값으로 표시되는 데
#                 # 0보다 큰지 작은지 0인지를 구분하기 위함이다.
#                 fvalue = value / 32767.0
#                 # 상태값(0, 1, -1)을 저장
#                 axis_states[axis] = fvalue
#                 print("%s: %.3f" % (axis, fvalue))
