# JOYSTICK SERIAL



## Description

This package is for serial communication by connecting a joystick to the Raspberry Pi 3.



## Protocol

Data ordering : Little Endian

Data Transfer Rate : 50Hz (0.02 ms) 



## Package

### 1) ums_joystick

- names.py
  - joystick's buttons, axises dictionary
- protocol.py
  - packet's elements definition
- key_reader.py
  - joystick connection check & event process

### 2) ums_serial

- reader.py
  - Undefined
- writer.py
  - Serial Write (Type : bytes)



## Main

### umd_serial.py

- main
- Serial connection check, Serial process



## EXECUTION

```
$ cd scripts
$ python3 joystick_serial

or

$ python3 umd_serial.py
```


