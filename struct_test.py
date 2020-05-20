import struct

from itertools import zip_longest # or zip_longest in Python 3.x

def grouper(iterable, n, fillvalue=None):
    "Collect data into fixed-length chunks or blocks"
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx
    args = [iter(iterable)] * n
    return zip_longest(fillvalue=fillvalue, *args) # see comment above


# byte 
# test = bytes(10)
# test = "test"
# test = test.encode()
# print(test)

test = 15151
left_data = test.to_bytes(2, byteorder="little",signed=True)
test2 = -1514
right_data = test2.to_bytes(2, byteorder="little",signed=True)


test_list = [0 for i in range(14)]
test_list[0] = 0x53
test_list[1] = 0x53
test_list[2] = 0x58
test_list[3] = 0x00
test_list[4] = 0x00
test_list[5] = 0x00
test_list[6] = left_data[0]
test_list[7] = left_data[1]
test_list[8] = right_data[0]
test_list[9] = right_data[1]
test_list[10] = 154
test_list[11] = sum(test_list[3:5])
test_list[12] = 0x0D
test_list[13] = 0x0A

test3 = format(0xA, "#04x")
print(test3)

print(bytearray(test_list))
print(bytes(test_list))
print(len(bytes(test_list)))
print(test)


# x = bytes([67, 128])
# print(''.join(r'\x'+hex(letter)[2:] for letter in bytes(test_list)))
# print(''.join(hex(letter) for letter in test_list))
# print(''.join(hex(letter) for letter in test_list).replace("0x",""))
print(", ".join("0x{:02x}".format(num) for num in test_list))

test = ",".join("0x{:02x}".format(num) for num in test_list)

print(test)
test = test.split(",")
result = bytes([int(x,0) for x in test])

print(result)


# packet = bytearray(test)
# print(packet)


# byte_array = bytearray.fromhex(str(test))
# print(byte_array)


# test = "00"
# byte_array = bytearray.fromhex(test)
# print(byte_array)

# print(len(byte_array))

# test.encode()
# print(len(test.encode()))
# print(len(test.encode()))


# hexes = ["0x{0}".format("".join(t)) for t in grouper(test, 2)]
# print(hexes)
# print(len(hexes))

# a = 65535 
# # a = hex(65535)

# a = struct.pack(">l",a)
# a = hex(int(a.hex(),16))
# a = a.encode()

# a = a & 

# print(hex(0xff00))
# # a = bytes(a.encode())
# # a = a & 0xff00


# print(a)
# print(bytes(test_list))dd
# print(len(test))
# packet = bytearray(test_list)
# print(packet)
# print(bytearray(test_list))
# print(len(test_list))

# packet = packet.encode()
# packet[0] = "0x01".encode()
# packet[0] = int('45', 16)
# packet[1] = int('ea', 16) # R
# packet[4] = int('cc', 16)

# test = packet.hex().encode()
# print(hex(packet))
# print(len(test))



# test1 = struct.pack(">i",22)

# test1 = hex(int(test1.hex(),16))
# #print(test1)

def change_hex(data):
    data = struct.pack(">i",data)
    data = hex(int(data.hex(),16))
    return data

result = change_hex(256)
#print(result)


# test2 = struct.pack("i", 1).hex()

# test = test1 + test2
# test = struct.pack("iii", test)
# test = test
# test = test.encode("utf-8")

# #print(test)
# test1 = "asdf".encode("hex")
# test1 = hex(int(test1,16))
# #print (test1)

# test2 = '0x2'
# test = int(test1, 16) + int(test2, 16)
# #print (test)