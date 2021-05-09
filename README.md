# JOYSTICK SERIAL

[TOC]

## Description

This package is for serial communication by connecting a joystick to the Raspberry Pi 3.



## Protocol

Data ordering : Little Endian

Data Transfer Rate : 50Hz (0.02 ms) 

<img width="964" alt="protocol" src="https://user-images.githubusercontent.com/35681273/96358150-f02c1f00-113e-11eb-94fb-4b5fd8878e36.png">



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



## Update 방법

### 1. 필요한 것

1. 모니터, HDMI 선, 보조배터리 
2. 키보드, 마우스
3. usb



### 2. 업데이트 방법

1. usb에 joystick-serial 파일을 복사
2. 라즈베리파이에 usb, 모니터, 키보드 및 마우스 연결
   - 모니터를 연결했음에도 화면이 안나오면 라즈베리파이 전원을 껐다 다시 켠다.

3. 폴더를 클릭하여 /home/pi 경로로 들어간다.

4. joystick-serial, joystick-res 폴더가 있음을 확인.

5. 기존의 joystick-serial 파일을 바탕화면이나 다른 디렉토리에 백업을 해둔 후 삭제.

6. usb에 복사한 joystick-serial을 /home/pi 안에 복사한다.



### 3. 업데이트 확인

1. 터미널을 열어 /opt/joystick/joystick.sh 명령어를 치거나, 재부팅을 하여 확인

2. 첨부한 사진 (업데이트 시 화면.jpeg)과 비슷하게 나오면 업데이트가 된 것.

    - speed_val, steer_val, fitting_steer_val, packet 문자열과 값이 출력된다.
    
    - speed_val, packet 문자열과 값만 출력되면 업데이트가 안 된것!!!



2. 