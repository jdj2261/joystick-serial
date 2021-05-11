#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@ Created Date: May 15. 2020
@ Updated Date: May 03. 2021  
@ Author: Dae Jong Jin 
@ Description: Integrate serial communication and xbox control
'''

import time
import sys, os
sys.path.append(os.path.dirname(__file__))

from ums_xbox.xbox import Xbox 
from ums_xbox.protocol import Packet
from ums_serial.ums_serial import UmsSerial

class XboxControl:
    def __init__(self, port_name, baudrate, timeout, testmode, daedzone):
        self.is_testmode = testmode
        self.ums_ser = UmsSerial(port_name, baudrate, timeout)
        self.xbox = Xbox(index=0, deadzone=daedzone)
        self.packet = Packet()

    def __repr__(self) -> str:
        return "<{cls}>".format(cls=self.__class__.__name__)
    
    def __call__(self):
        return self.exec()

    def exec(self):
        self.xbox.start()
        self._main_loop()

    def _main_loop(self):
        while True:
            try:
                if self.ums_ser.connect(self.is_testmode):
                    self._send_xbox_data()
            except OSError as e:
                print(e)
                self.ums_ser.disconnect()
            time.sleep(0.5)

    def _send_xbox_data(self):
        while True:
            if self.xbox.is_connect:
                self.packet.alive = self._active_count(self.packet.alive)
                self._control_accel()

                accel_val, brake_val, steer_raw_val, steer_modified_val = self._convert_bytes(
                        self.xbox.current_accel_data,
                        self.xbox.brake_data,
                        self.xbox.steer_raw_data,
                        self.xbox.steer_modified_data)

                self.packet.accel_data[1] = accel_val[1]
                self.packet.brake_data[0] = brake_val[0]
                self.packet.brake_data[1] = brake_val[1]
                self.packet.steer_data[0] = steer_raw_val[0]
                self.packet.steer_data[1] = steer_raw_val[1]
                self.packet.steer_data[2] = steer_modified_val[0]
                self.packet.steer_data[3] = steer_modified_val[1] 

                send_packet = self.packet.makepacket(
                            estop = self.xbox.pushed_estop, 
                            gear = self.xbox.gear_data,
                            wheel = self.xbox.pushed_wheel)

                if self.is_testmode:
                    print(f"{send_packet}")
                else:
                    self.ums_ser.write(send_packet)

                self.xbox.pre_accel_data = self.xbox.accel_data
                time.sleep(0.02)
            else:
                pass

    def _control_accel(self):
        self.xbox.limit_aps_data()
        self.xbox.limit_accel_data()
        self.xbox.limit_steer_data()
        self.xbox.initialize_accel()

        if self.xbox.accel_data != 0: 
            self.xbox.release_cruise_mode()
        if self.xbox.brake_data == 0: 
            self.xbox.choose_cruise_mode()

    def _active_count(self, data: int) -> int:
        data += 1
        if data >= 256: data = 0
        return data

    def _convert_bytes(self, accel, brake, *args):
        ret_accel = accel.to_bytes(
            2, byteorder="little", signed=False)
        ret_brake = brake.to_bytes(
            2, byteorder="little", signed=False)
        ret_raw_steer = args[0].to_bytes(
            2, byteorder="little", signed=True)
        ret_modified_steer = args[1].to_bytes(
            2, byteorder="little", signed=True)

        return ret_accel, ret_brake, ret_raw_steer, ret_modified_steer

def main():
    port_name = "/dev/ttyAMA0"
    baudrate = 9600
    timeout = 0.1
    testmode = True
    deadzone = 0.05
    xc = XboxControl(port_name, baudrate, timeout, testmode, deadzone)
    xc.exec()

if __name__ == "__main__":
    main()