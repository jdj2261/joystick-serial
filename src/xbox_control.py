#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
@ Created Date: May 15. 2020
@ Updated Date: May 03. 2021  
@ Author: Dae Jong Jin 
@ Description: TODO
'''

import time
import sys, os
sys.path.append(os.path.dirname(__file__))

from ums_xbox.xbox import Xbox 
from ums_xbox.protocol import Packet
from ums_xbox.names import Param
from ums_serial.ums_serial import UmsSerial

# dev_port = "/dev/serial0"
class XboxControl:
    def __init__(self, port_name, baudrate, timeout, testmode):
        self.ums_ser = UmsSerial(port_name, baudrate, timeout, testmode)
        self.xbox = Xbox(0)
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
                if self.ums_ser.connect():
                    self._send_xbox_data()
            except OSError as e :
                self.ums_ser.disconnect()
            time.sleep(0.5)
    
    def _send_xbox_data(self):
        while True:
            if self.xbox.is_connect:
                self.packet.alive = self._active_count(self.packet.alive)
                self._control_accel()

                accel_val, brake_val, steer_val = self._convert_bytes(
                        self.xbox.current_accel_data,
                        self.xbox.brake_data,
                        self.xbox.steer_data
                )

                self.packet.accel_data[1] = accel_val[1]
                self.packet.brake_data[0] = brake_val[0]
                self.packet.brake_data[1] = brake_val[1]
                self.packet.steer_data[0] = steer_val[0]
                self.packet.steer_data[1] = steer_val[1]
                # TODO
                # packet.steer_data[2] = exp_value[0]
                # packet.steer_data[3] = exp_value[1] 

                send_packet = self.packet.makepacket(
                            estop = self.xbox.pushed_estop, 
                            gear = self.xbox.gear_data,
                            wheel = self.xbox.pushed_wheel)

                print(f"{self.xbox.is_cruise}\t{send_packet}")
                self.ums_ser.write(send_packet)

                self.xbox.pre_accel_data = self.xbox.accel_data
                time.sleep(0.02)
            else:
                pass

    def _control_accel(self):
        self.xbox.limit_aps_data()

        if self.xbox.accel_data != 0 :
            self.xbox.is_cruise = False
        if self.xbox.accel_data < 0 :
            self.xbox.accel_data = 0
        elif self.xbox.accel_data !=0:
            self.xbox.cruise_accel_data = Param.APS_INIT_VAL

        if self.xbox.brake_data != 0 or \
            self.xbox.pushed_estop == 'ESTOP_ON' or \
            self.xbox.gear_data == 'GEAR_N': 
            self.xbox.accel_data = 0
            self.xbox.current_accel_data = 0
            self.xbox.result_accel_data = 0

        if self.xbox.current_accel_data < Param.APS_INIT_VAL:
            self.xbox.current_accel_data = Param.APS_INIT_VAL
        self.xbox.prevent_accel()

        if self.xbox.brake_data == 0:
            self.xbox.choose_accel_mode()

    def _active_count(self, data: int) -> int:
        data += 1
        if data >= 256: data = 0
        return data

    def _convert_bytes(self, accel, brake, steer):
        ret_accel = accel.to_bytes(
            2, byteorder="little", signed=False)
        ret_brake = brake.to_bytes(
            2, byteorder="little", signed=False)
        ret_steer = steer.to_bytes(
            2, byteorder="little", signed=True)

        return ret_accel, ret_brake, ret_steer

def main():
    port_name = "/dev/ttyACM0"
    baudrate = 9600
    timeout = 0.1
    testmode = True
    xc = XboxControl(port_name, baudrate, timeout, testmode)
    xc.exec()

if __name__ == "__main__":
    main()