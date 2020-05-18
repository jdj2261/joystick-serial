import struct



# byte 
# test = bytes(10)
# test = "test"
# test = test.encode()
# print(test)


test_list = [0 for i in range(10)]
test_list[0] = 0xea
test_list[1] = 0xaa
test_list[2] = 0xaa


test = 15
left_data = test.to_bytes(2, byteorder="big")
print(left_data[1])

test_list[3] = left_data[0]
test_list[4] = left_data[1]

right_data = test.to_bytes(2, byteorder="big")
print(right_data[1])

test_list[5] = right_data[0]
test_list[6] = right_data[1]

print(bytearray(test_list))
print(bytes(test_list))



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