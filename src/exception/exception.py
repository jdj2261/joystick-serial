#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@ Created Date: May 3. 2021
@ Author: Dae Jong Jin 
@ Description: Custom exception class
'''
# This is not used, but it is easy to degug.
# so create and use it if necessary.
class SerialException(OSError):
    """Base class for serial port related exceptions."""

class PortNotOpenError(SerialException):
    """Port is not open"""
    def __init__(self):
        super(PortNotOpenError, self).__init__('Attempting to use a port that is not open')
