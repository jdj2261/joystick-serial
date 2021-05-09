class SerialException(OSError):
    """Base class for serial port related exceptions."""


class PortNotOpenError(SerialException):
    """Port is not open"""
    def __init__(self):
        super(PortNotOpenError, self).__init__('Attempting to use a port that is not open')
