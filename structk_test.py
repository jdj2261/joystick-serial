import struct


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