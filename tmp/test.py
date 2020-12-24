
import time
from multiprocessing import Pool ,Process, Queue
from threading import Thread
import queue
import sys
 
class TestClass():

    def __init__(self):
        self.ctr = 0
        self.t = 0
        self.isThread = True
        # self.operate = True

    def test_process(self):
        # if self.operate == True:
        while self.isThread:
            data = self.t
            print("Data : %d"%data,end='')
            self.ctr += 1
            print("     ", self.ctr)
            time.sleep(0.5)
        
    def test_2(self):
        operate = self

        try:

            t = Thread(target=operate.test_process)
            t.daemon = True
            t.start()
            while True:
                stop_char=input("Enter 'q' to quit ")
                if stop_char.lower() == "s":
                    if operate is not None:
                        print("Input s")
                        operate.isThread = False
                        t.join()
                        operate = None
                        # self.operate = False
                        # t.join()
                elif stop_char.lower() == "r":
                    if operate is None:
                        operate = TestClass()
                        t = Thread(target=operate.test_process)
                        t.daemon = True
                        t.start()
                        operate.t = 1
                elif stop_char.lower() == "q":
                    print("pressed q")
                    exit(0)
                    break

            print("terminate process")
        except (KeyboardInterrupt, SystemExit):
            print ('\n! Received keyboard interrupt, quitting threads.\n')
            sys.exit()

if __name__ == '__main__':
    ## run function in the background

    CT = TestClass()
    CT.test_2()
