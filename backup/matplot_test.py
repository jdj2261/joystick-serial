from matplotlib import pyplot as plt
import numpy as np
import math

   
# x = np.linspace(1, 32767, 100)
# y = np.exp(x)
x = np.arange(1,32767)
y = pow((x/32767),2) * 32767 * (x / abs(x))
# y = 1.2* pow(1.043,x) - 1.2 + 0.2 * (x)

plt.plot(x,y,'r')
plt.show()

print(y)