hexa_list = ["0x50","0x53"]
for i, x in enumerate(hexa_list):
    print(x, end="")
    if i % 0x10 == 0x0f:
        print()
print()