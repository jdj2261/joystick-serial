from matplotlib import pyplot as plt
import numpy as np
import math

   
# x = np.linspace(1, 32767, 100)
# y = np.exp(x)
x = np.arange(-32767, 32767)
# y = (pow((x/32767),2) * 32767 * (x / abs(x)))*8
y = (pow((x/32767),2) * 32767 * (x / abs(x)))*8

# y = 1.2* pow(1.043,x) - 1.2 + 0.2 * (x)
y1 = np.exp(0.0021*x)

plt.plot(x,y,'b')
plt.plot(x,y1,'r')
plt.show()

print(y)

x = 0
y = x/abs(x)

print(y)