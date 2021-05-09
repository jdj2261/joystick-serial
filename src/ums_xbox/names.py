#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
@ Created Date: May 15. 2020
@ Updated Date: May  4. 2021
@ Author: Dae Jong Jin 
@ Description: Xbox joystick axis, button name
'''

class Joy:
    def __repr__(self):
        return "<{cls}>".format(cls=self.__class__.__name__)
        
    JS_EVENT_BUTTON = 0x01
    JS_EVENT_AXIS = 0x02
    JS_EVENT_INIT = 0x80

class Param(Joy):
    def __init__(self) -> None:
        super().__init__()

    def __repr__(self):
        return "<.{cls}>".format(cls=self.__class__.__name__)

    MAX_ACCEL_VAL = 40000 
    THRESH_ACCEL_VAL = 25000
    INCREASE_VAL = 100 
    DECREASE_VAL = 200 
    APS_INIT_VAL = 2500 
    CRUISE_VAL = 5000
    LIMIT_STEER_VAL = 32700 

class Axis(Joy):
    def __init__(self):
        super().__init__()

    def __repr__(self):
        return "<Xbox.{cls}>".format(cls=self.__class__.__name__)

    axis_names = {
        0x02 : 'z',     # Accel
        0x03 : 'rx',    # Steer
        0x04 : 'ry',    # Empty
        0x05 : 'rz',    # Brake
        0x10 : 'hat0x', # Gear N
        0x11 : 'hat0y', # Gear D, R
    }

    axis_redefine = {
        'z' : 'ACCEL',     # Accel
        'rx': 'STEER',    # Steer
        'rz': 'BRAKE',    # Brake
        'hat0x': 'GEAR_N', # Gear N
        'hat0y': 'GEAR_D_R', # Gear D, R
    }


class Button(Joy):
    def __init__(self):
        super().__init__()

    def __repr__(self):
        return "<Xbox.{cls}>".format(cls=self.__class__.__name__)

    button_names = {
        # WHEEL
        0x130 : 'a',        # Backward
        0x131 : 'b',        # Empty
        0x133 : 'x',        # Fourth
        0x134 : 'y',        # Forward

        # ESTOP
        0x136 : 'tl',       # Off
        0x137 : 'tr',       # On
        0x13c : 'mode',     # On

        # CRUISE
        0x13a : 'select',   # Speed Up
        0x13b : 'start',    # Speed Down
    }

    button_redefine = {
        'a' : 'WHEEL_REAR',
        'x' : 'WHEEL_ALL',
        'y' : 'WHEEL_FRONT',
        'tl': 'ESTOP_OFF',
        'tr': 'ESTOP_ON',
        'mode': 'ESTOP_ON',
        'select': 'CRUISE_DOWN',
        'start': 'CRUISE_UP',
    }
