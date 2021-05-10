import time, threading
 
class MyExample(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.__suspend = False
        self.__exit = False
 
    def run(self):
        while True:
            ### Suspend ###
            while self.__suspend:
                time.sleep(0.5)
                 
            ### Process ###
            print ('Thread process !!!')
 
            ### Exit ###
            if self.__exit:
                break
            time.sleep(1)
    def mySuspend(self):
        self.__suspend = True
         
    def myResume(self):
        self.__suspend = False
         
    def myExit(self):
        self.__exit = True
 
 
lock = threading.Lock()
th = MyExample()
th.start()
time.sleep(1)
 
### suspend 
th.mySuspend()
with lock:
    print ('Suspend Thread ....')
time.sleep(1)
 
### resume
th.myResume()
with lock:
    print ('Resume Thread ....')
time.sleep(1)
 
### exit
th.myExit()
