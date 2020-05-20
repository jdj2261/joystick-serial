import serial
# byte 
# test = bytes(10)
# test = "test"
# test = test.encode()
# print(test)

'''
packet definition
LENGTH : 14bytes
0 1 2   3     4    5      6     7      8      9      10      11     12   13
S T X ESTOP GEAR WHEEL SPEED0 SPEED1 STEER0 STEER1 ALIVE CHECKSUM ETX0 ETX1

S → 0x53 
T → 0x54
X → 0x58
ESTOP → 0x00 : OFF,           0x01 : ON
GEAR  → 0x00 : forward drive, 0x01 : neutral,     0x02 : backward drive
WHEEL → 0x00 : forward wheel, 0x01: fourth wheel, 0x02 : backward wheel
SPEED → -32768 ~ 32768 //actual speed
STEER → -32768 ~ 32768 // actual steering degree
ALIVE → 0 ~ 255        // increasing each one step 
Checksum → E-STOP + GEAR + WHEEL + SPEED0 + SPEED1 + STEER0 + STEER1
ETX0 → 0x0D
ETX1 → 0x0A 
'''
port = '/dev/opencm'
try :
    ser = serial.Serial(port,9600)
except serial.serialutil.SerialException as e:
    print(e)

ESTOP = {'PRESSED' : 0x00, 'PUSH' : 0x01 }
GEER = [0x00, 0x01, 
WHEEL = 0x00
ALIVE = 0x00
CHECKSUM = 0x00

speed_data = 1024
steer_data = 1024
speed_data = speed_data.to_bytes(2, byteorder="little")
steer_data = steer_data.to_bytes(2, byteorder="little")

packet_data = [0 for i in range(14)]
packet_data = [0x53, 0x54, 0x58, ESTOP[0], GEER, WHEEL, speed_data[0], speed_data[1], steer_data[0], steer_data[1], ALIVE, CHECKSUM, 0x0D, 0x0A]
bytearray_data = bytearray(packet_data)
bytes_data = bytes(packet_data)

print(packet_data)

print(bytearray_data)
print(bytes_data)
# ser.write(serial.to_bytes(packet_data))



