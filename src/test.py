import time
import sys, os
sys.path.append(os.path.dirname(__file__))


from ums_xbox.xbox import Xbox 
from ums_xbox.protocol import Packet
from ums_xbox.names import Param
from ums_serial.ums_serial import UmsSerial


def active_count(data: int) -> int:
    data += 1
    if data >= 256: data = 0
    return data

def convert_bytes(accel, brake, steer):
    ret_accel = accel.to_bytes(
        2, byteorder="little", signed=False)
    ret_brake = brake.to_bytes(
        2, byteorder="little", signed=False)
    ret_steer = steer.to_bytes(
        2, byteorder="little", signed=True)

    return ret_accel, ret_brake, ret_steer

def main():
    xbox = Xbox(0)
    xbox.start()
    packet = Packet()
    while True:
        if xbox.is_connect:
            packet.alive = active_count(packet.alive)

            if xbox.current_accel_data < Param.APS_INIT_VAL:
                xbox.current_accel_data = Param.APS_INIT_VAL

            xbox.prevent_accel()
            accel_value = xbox.current_accel_data.to_bytes(
                2, byteorder="little", signed=False)
            brake_value = xbox.brake_data.to_bytes(
                2, byteorder="little", signed=False)
            steer_value = xbox.steer_data.to_bytes(
                2, byteorder="little", signed=True)

            packet.accel_data[1] = accel_value[1]
            packet.brake_data[0] = brake_value[0]
            packet.brake_data[1] = brake_value[1]
            packet.steer_data[0] = steer_value[0]
            packet.steer_data[1] = steer_value[1]
            # TODO
            # packet.steer_data[2] = exp_value[0]
            # packet.steer_data[3] = exp_value[1]

            send_packet = packet.makepacket(
                estop = xbox.pushed_estop, 
                gear = xbox.gear_data,
                wheel = xbox.pushed_wheel)

            print(f"{xbox.is_cruise}\t{send_packet}")
            xbox.pre_accel_data = xbox.accel_data

            time.sleep(0.02)
        else:
            pass

if __name__ == "__main__":
    main()