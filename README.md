# joystick-serial

This package is for serial communication by connecting a joystick to the Raspberry Pi 3.

It is a package used to control the Unmmaned Solution Shuttle, With:US.

![top](http://www.unmansol.com/images/sub02/top.jpg)

## Install

### Pip Install

~~~
$ pip install gitpython
~~~

## Run

~~~
$ cd script
$ ./joystick_control
~~~

If you only want to check the joystick data, Run it like this.

~~~
$ cd scirpt
$ ./joystick_control -t
~~~

## Example

If the xbox controller is connected, it looks like this.

<left><img src="doc/joystick_execute.png"></left>

If it is connected in test mode, it looks like this.

<left><img src="doc/joystick_test.png"></left>

If the xbox controller is disconnected and reconnected, it looks like this.

<left><img src="doc/not_connected_joystick.png"></left>



## Operation Manual

<img src="doc/operation_manual1.png" alt="image-20210511135124181" style="zoom:60%;" />



<img src="doc/operation_manual2.png" alt="image-operation_manual2" style="zoom:60%;" />

