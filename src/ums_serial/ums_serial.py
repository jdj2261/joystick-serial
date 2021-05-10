#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
@ Created Date: May 15. 2020
@ Updated Date: May  4. 2021
@ Author: Dae Jong Jin 
@ Description: Serial Communication
'''

import serial, serial.tools.list_ports
import time
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from exception.exception import PortNotOpenError

class UmsSerial:
    def __init__(self, port: str, baudrate: int, timeout: float):
        self.port = port
        self.device = None
        self._serial = serial.Serial(baudrate=baudrate, timeout=timeout)

    def __repr__(self) -> str:
        return "<{cls}>".format(cls=self.__class__.__name__)
    
    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        self.disconnect()
    
    def connect(self) -> bool:
        while not self._serial.isOpen():
            ports = self.find_comports()
            for port in ports:
                if self.port == port.device:
                    self._serial.port = self.port
            try:
                self._serial.open()
            except Exception as e:
                print("checking serial port...")
                time.sleep(1)

        if self._serial.isOpen():
            return True
        return False

    def disconnect(self) -> bool:
        try:
            self._serial.close()
        except AttributeError:
            print("open_comport has not been called yet!")
            return False
        else:
            print("Closing...")
            return True

    @staticmethod
    def find_comports() -> list:
        # Make a list of all available ports on the system
        available_ports = list(serial.tools.list_ports.comports())
        ports = [port for port in available_ports]
        return ports

    def isOpen(self):
        return self._serial.isOpen()

    def write(self, data):
        if not self.isOpen():
            raise PortNotOpenError()

        self._serial.write(serial.to_bytes(data))

    @property
    def read(self, length):
        return self._serial.read(length)

    @property
    def readline(self):
        return self._serial.readline()