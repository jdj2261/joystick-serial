from key_reader import *

dev_directory = '/dev/input'
fn = '/dev/input/js0'
if __name__ == "__main__":
    print("start")
    jr = JoystickReader()

    jr.joy_check(dev_directory)
    
    jr.joy_open(fn)
