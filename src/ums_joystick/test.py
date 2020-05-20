#!/usr/bin/env python
# -*- coding: utf-8 -*-
from key_reader import *

dev_directory = '/dev/input'
fn = '/dev/video0'
if __name__ == "__main__":
    print("start")
    jr = JoystickReader()

    jr.joy_check()
    
    jr.joy_open(fn)
