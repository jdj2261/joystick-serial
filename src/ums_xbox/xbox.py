#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
@ Created Date: May 15. 2020
@ Updated Date: May 03. 2021  
@ Author: Dae Jong Jin 
@ Description: TODO
'''
import sys, os
import struct
import array
import threading
import time
from threading import Thread

from fcntl import I_PUSH, ioctl
from collections import namedtuple

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from ums_xbox.names import *
from ums_xbox.protocol import Packet

ControllerEvent = namedtuple("Event", ["time", "type", "number", "value", "is_init"])

# TODO
def available(joystickNumber = 0):
    """Check if a joystick is connected and ready to use."""
    joystickPath = '/dev/input/js' + str(joystickNumber)
    return os.path.exists(joystickPath)

class Xbox(threading.Thread):
    def __init__(self, index=0):
        threading.Thread.__init__(self)
        self.is_connect = False
        self.is_cruise = False
        self.is_thread = True
        self.index = index
        self._dev_file = None
        self.daemon = True

        self.pushed_wheel = 'WHEEL_ALL'
        self.pushed_estop = 'ESTOP_OFF'
        self.pushed_gear = None
        self.pushed_cruise = None
        self.pushed_accel = None
        self.pushed_steer = None
        self.pushed_brake = None

        self.accel_data = 0
        self.pre_accel_data = 0
        self.current_accel_data = self.accel_data + Param.APS_INIT_VAL
        self.result_accel_data = self.current_accel_data
        self.cruise_accel_data = 0
        self.aps_accel_data = Param.APS_INIT_VAL

        self.brake_data = 0
        self.steer_data = 0
        self.gear_data = 'GEAR_N'

    def __repr__(self) -> str:
        return "<{cls}>".format(cls=self.__class__.__name__)

    def run(self):
        accel_thread = Thread(target=self.control_accel_thread)
        accel_thread.daemon = True
        accel_thread.start()

        while True:
            if self.connect():
                self.event_loop()

    def control_accel_thread(self):
        while True:
            if self.pre_accel_data < self.accel_data:
                self._control_increase_accel()
            elif self.pre_accel_data > self.accel_data:
                self._control_decrease_accel()
            else:
                self._correct_current_accel()

    def _control_increase_accel(self):
        self.is_thread = True
        while self.current_accel_data <= self.accel_data:
            if self.gear_data == 'GEAR_D':
                self._increase_based_on_threshold()
            elif self.gear_data =='GEAR_R':
                self.current_accel_data += Param.INCREASE_VAL * 2
            else:
                self.current_accel_data = 0
            self._limit_max_current_accel()
            time.sleep(0.02)

    def _control_decrease_accel(self):
        self.is_thread = True
        while self.current_accel_data >= self.accel_data:
            if self.gear_data == 'GEAR_D':
                self.current_accel_data -= Param.DECREASE_VAL
            elif self.gear_data =='GEAR_R':
                self.current_accel_data -= Param.DECREASE_VAL * 3
            else:
                self.current_accel_data = 0
            self._limit_min_current_accel()
            time.sleep(0.02)

    def _correct_current_accel(self):
        if self.accel_data > self.current_accel_data:
            self.accel_data += 1
        else:
            self.accel_data -= 1
    
    def _increase_based_on_threshold(self):
        if self.current_accel_data <= Param.THRESH_ACCEL_VAL:
            self.current_accel_data += Param.INCREASE_VAL
        else:
            self.current_accel_data += (int)(Param.INCREASE_VAL / 4)

    def _limit_max_current_accel(self):
        if self.current_accel_data > Param.MAX_ACCEL_VAL:
            self.current_accel_data = Param.MAX_ACCEL_VAL
    
    def _limit_min_current_accel(self):
        if self.current_accel_data < 0:
            self.current_accel_data = self.accel_data + Param.APS_INIT_VAL

    def _limit_cruise_data(self):
        if self.cruise_accel_data < self.aps_accel_data:
            self.cruise_accel_data = self.aps_accel_data
        
        if self.cruise_accel_data > Param.MAX_ACCEL_VAL:
            self.cruise_accel_data = Param.MAX_ACCEL_VAL

    def limit_aps_data(self):
        if self.aps_accel_data < Param.APS_INIT_VAL:
            self.aps_accel_data = Param.APS_INIT_VAL
        elif self.aps_accel_data > Param.MAX_ACCEL_VAL:
            self.aps_accel_data = Param.MAX_ACCEL_VAL

    def connect(self) -> bool:
        while True:
            if not self._open(): continue
            if self._is_xbox(): break
        self.axis = self._get_axis()
        self.buttons = self._get_buttons()
        return True

    def _open(self) -> bool:
        try:
            print('Opening %s...' % self._get_dev_file)
            self._dev_file = open(self._get_dev_file, 'rb')
            self.is_connect = True
            return True
        except FileNotFoundError:
            self.is_connect = False
            print(f"controller device with index {self.index} was not found!")
            self.reset_data()
            time.sleep(2)

    @property
    def _get_dev_file(self) -> str:
        return "/dev/input/js{idx}".format(idx=self.index)

    def _is_xbox(self) -> bool:
        buf = array.array('B', [0] * 64)
        ioctl(self._dev_file, 0x80006a13 + (0x10000 * len(buf)), buf) 
        xbox_name = buf.tobytes().rstrip(b'\x00').decode('utf-8') 
        print('Device name: %s' % xbox_name)
        if "Generic" in xbox_name or "Microsoft" in xbox_name:
            return True
        return False

    def _get_axis(self) -> list:
        buf = array.array('B', [0])
        ioctl(self._dev_file, 0x80016a11, buf)  # JSIOCGaxis
        num_axis = buf[0]
        buf = array.array('B', [0] * 0x40)
        ioctl(self._dev_file, 0x80406a32, buf)  # JSIOCGAXMAP
        axis_map = []
        for axis in buf[:num_axis]:
            axis_name = Axis.axis_names.get(axis, 'unknown(0x%02x)' % axis)
            if axis_name is not None:
                axis_map.append(axis_name)
        return axis_map

    def _get_buttons(self) -> list:
        buf = array.array('B', [0])
        ioctl(self._dev_file, 0x80016a12, buf)  # JSIOCGBUTTONS
        num_buttons = buf[0]
        buf = array.array('H', [0] * 200)
        ioctl(self._dev_file, 0x80406a34, buf)  # JSIOCGBTNMAP
        buttons_map = []
        for btn in buf[:num_buttons]:
            btn_name = Button.button_names.get(btn, 'unknown(0x%03x)' % btn)
            if btn_name is not None:
                buttons_map.append(btn_name)
        return buttons_map

    def event_loop(self):
        while True:
            event = self._get_event()
            if event is None: break
            if event is not None and not event.is_init:
                self._process_event(event)

    def _get_event(self) -> ControllerEvent:
        try:
            buf = self._dev_file.read(8)
        except ValueError as e:
            print(e)
            self._dev_file.close()
            return
        except OSError as e:
            print(e)
            self._dev_file.close()
            return
        else:
            if buf:
                time_, value, type_, number = struct.unpack("IhBB", buf)
                is_init = bool(type_ & Joy.JS_EVENT_INIT)
                return ControllerEvent(
                    time=time_, type=type_, number=number, value=value, is_init=is_init
                )

    def _process_event(self, event: ControllerEvent):
        button, axis = None, None
        if event.type == Joy.JS_EVENT_BUTTON and event.value:
            button = self._button_event(event)
            self._convert_button(event, button)
            self._set_cruise_accel_data()
        if event.type == Joy.JS_EVENT_AXIS:
            axis = self._axis_event(event)
            self._convert_axis(axis)
            self._get_axis_data(event)
        self._change_cruise_mode()

    def _button_event(self, event: ControllerEvent):
        button = self.buttons[event.number]
        button = Button.button_redefine.get(button, None)
        return button

    def _axis_event(self, event: ControllerEvent):
        axis = self.axis[event.number]
        axis = Axis.axis_redefine.get(axis, None)
        return axis

    def _convert_button(self, event, button):
        if button == 'WHEEL_REAR':
            self.pushed_wheel = button
        if button == 'WHEEL_ALL':
            self.pushed_wheel = button
        if button == 'WHEEL_FRONT':
            self.pushed_wheel = button
        if button == 'ESTOP_OFF':
            self.pushed_estop = button
        if button == 'ESTOP_ON':
            self.pushed_estop = button
        if button == 'CRUISE_DOWN':
            self.pushed_cruise = button
        if button == 'CRUISE_UP':
            self.pushed_cruise = button
        # print(self.pushed_wheel, self.pushed_estop, self.pushed_cruise) 

    def _change_cruise_mode(self):
        if self.pushed_cruise:
            self.is_cruise = True

        if self.accel_data != 0 or \
            self.pushed_gear == 'GEAR_N' or \
            self.gear_data == 'ESTOP_ON':

            self.is_cruise = False
            self.pushed_cruise = None
        # print(self.accel_data, self.is_cruise)

    def _set_cruise_accel_data(self):
        if self.is_thread:
            self.cruise_accel_data = self.result_accel_data
            self.is_thread = False 
        else:
            if self.pushed_cruise == 'CRUISE_DOWN':
                self.cruise_accel_data -= int(Param.CRUISE_VAL / 2)
            if self.pushed_cruise == 'CRUISE_UP':
                self.cruise_accel_data += Param.CRUISE_VAL
        self._limit_cruise_data()

    def choose_accel_mode(self):
        if self.is_cruise:
            self.current_accel_data = self.cruise_accel_data
            self.result_accel_data = self.cruise_accel_data
        else:
            self.result_accel_data = self.current_accel_data

    def prevent_accel(self):
        if self.brake_data != 0 or \
            self.pushed_estop == 'ESTOP_ON' or \
            self.gear_data == 'GEAR_N': 
            self.current_accel_data = 0
            self.result_accel_data = 0

    def _convert_axis(self, axis):
        if axis == 'ACCEL':
            self.pushed_accel = axis
        if axis == 'STEER':
            self.pushed_steer = axis
        if axis == 'BRAKE':
            self.pushed_brake = axis
        if axis == 'GEAR_N':
            self.pushed_gear = axis
        if axis == 'GEAR_D_R':
            self.pushed_gear = axis       
        # print(self.pushed_accel, self.pushed_steer, self.pushed_brake, self.pushed_gear) 

    def _get_axis_data(self, event):
        self._get_accel_data(event)
        self._get_brake_data(event)
        self._get_steer_data(event)
        self._get_gear_data(event)

    def _get_accel_data(self, event):
        if event.number == 2 and self.pushed_accel:
            self.accel_data = event.value + 32767

    def _get_brake_data(self, event):
        if event.number == 5 and self.pushed_brake:
            self.brake_data = event.value + 32767

    def _get_steer_data(self, event):
        if event.number == 3 and self.pushed_steer:
            self.steer_data = event.value
        # TODO
        # DEADZONE 
        # https://github.com/ros-drivers/joystick_drivers/blob/main/joy/src/joy_node.cpp)
        
    def _get_gear_data(self, event):
        if event.number == 6:
            self.gear_data = 'GEAR_N'

        if event.number == 7 :
            if event.value == 32767:
                self.gear_data = 'GEAR_R' 
            if event.value == -32767:
                self.gear_data = 'GEAR_D'

    def reset_data(self):
        self.pushed_wheel = 'WHEEL_ALL'
        self.pushed_estop = 'ESTOP_OFF'

        self.pushed_gear = None
        self.pushed_cruise = None
        self.pushed_accel = None
        self.pushed_steer = None
        self.pushed_brake = None

        self.is_cruise = False

        self.accel_data = 0
        self.brake_data = 0
        self.steer_data = 0
        self.gear_data = 'GEAR_N'

def active_count(data: int) -> int:
    data += 1
    if data >= 256: data = 0
    return data

def main():
    xbox = Xbox(0)
    xbox.start()
    packet = Packet()
    while True:
        if xbox.is_connect:
            packet.alive = active_count(packet.alive)

            xbox.limit_aps_data()
            if xbox.accel_data != 0 :
                xbox.is_cruise = False
            if xbox.accel_data < 0 :
                xbox.accel_data = 0
            elif xbox.accel_data !=0:
                xbox.cruise_accel_data = Param.APS_INIT_VAL

            if xbox.current_accel_data < Param.APS_INIT_VAL:
                xbox.current_accel_data = Param.APS_INIT_VAL

            if xbox.brake_data != 0 or \
                xbox.pushed_estop == 'ESTOP_ON' or \
                xbox.gear_data == 'GEAR_N': 
                xbox.cruise_accel_data = Param.APS_INIT_VAL
                xbox.current_accel_data = 0
                xbox.result_accel_data = 0
                xbox.aps_accel_data = 0
             
            if xbox.brake_data == 0:
                xbox.choose_accel_mode()
            
            accel_value = xbox.current_accel_data.to_bytes(
                2, byteorder="little", signed=False)
            brake_value = xbox.brake_data.to_bytes(
                2, byteorder="little", signed=False)
            steer_value = xbox.steer_data.to_bytes(
                2, byteorder="little", signed=True)

            packet.accel_data[1] = accel_value[1]
            packet.brake_data[0] = brake_value[0]
            packet.brake_data[1] = brake_value[1]
            packet.steer_data[0] = steer_value[0]
            packet.steer_data[1] = steer_value[1]
            # TODO
            # packet.steer_data[2] = exp_value[0]
            # packet.steer_data[3] = exp_value[1]

            send_packet = packet.makepacket(
                estop = xbox.pushed_estop, 
                gear = xbox.gear_data,
                wheel = xbox.pushed_wheel)

            print(f"{xbox.is_thread}\t{xbox.is_cruise}\t{send_packet}")
            # print(f"{xbox.current_accel_data}")
            xbox.pre_accel_data = xbox.accel_data

            time.sleep(0.02)
        else:
            pass


if __name__ == "__main__":
    main()
