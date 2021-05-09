import threading
import random
import time    


class Process(threading.Thread):        

    def __init__(self):
        threading.Thread.__init__(self)      
        self.t = 0    

    def run(self):          
        self.leave = False
        print("\n it's running ...\n\n")            
        while self.leave == False:  
            print("Number : {0}".format(self.t))
            print("Done!")
            time.sleep(1)   

operate = None
operate = Process()    
operate.start() 
while True:
    inputt = input("   START : 1 \n   STOP\t : 0 \n   QUIT\t : 2 \n")       
    try:
        if int(inputt) == 1:
            if operate is None:
                operate = Process()    
                operate.start()    
                operate.t = 1         
        elif int(inputt) == 0:
            if operate is not None:
                operate.leave = True
                operate.t = 2
                operate.join() # wait on process end
                operate = None
        elif int(inputt) == 2:
            if operate is not None:
                operate.leave = True
                operate.join() # wait on process end
            break
    except:
        print(" Wrong input, try egain...\n")