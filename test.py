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

import os, struct, array

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
    # print("{0}".format(axis_name))

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