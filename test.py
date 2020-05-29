import time
from multiprocessing import Pool ,Process, Queue
from threading import Thread
import queue
import sys
 
class TestClass():

    def __init__(self):
        self.ctr = 0
        self.t = 0


    def test_process(self):
        while True:
            data = self.t
            print(data)
            self.ctr += 1
            print("     ", self.ctr)
            time.sleep(0.02)

    # def test_queue(self, q):
        
    #     while True:
    #         try:
    #             # data = self.t
    #             data = q.get(block=False)
    #             print("q : {0}".format(data))
    #             self.ctr += 1
    #             print("     ", self.ctr)
    #             time.sleep(1)
    #         except queue.Empty:
    #             pass
    
    def test_2(self):


        # p = Process(target=self.test_process)
        # p.start()
        # p = Pool()
        # p.map(self.test_1, self.t)
        # q = Queue()
        # # q.get()
        # test = Process(target=self.test_queue, args=(q,))
        # test.start()
        try:
            t = Thread(target=self.test_process)
            t.daemon = True
            t.start()
            while True:
                # print(self.t)
                stop_char=input("Enter 'q' to quit ")
                # print(t)
                if stop_char.lower() == "q":
                    # t.join()
                    print("pressed q")
                    exit(0)
                    break
                if stop_char.lower() == "u":
                    print("Input u")
                    self.t = 2
                if stop_char.lower() == "e":
                    print("Input u")
                    self.t = 3
                # q.put(self.t, False)
                    ## do something else
            print("terminate process")
        except (KeyboardInterrupt, SystemExit):
            print ('\n! Received keyboard interrupt, quitting threads.\n')
            sys.exit()

        # q.close()
        # q.join_thread()
        # test.join()
        if t.is_alive():
            t.join()

        # if p.is_alive():
        #     # print("finished")
        #     p.terminate()

 
if __name__ == '__main__':
    ## run function in the background

    CT = TestClass()
    CT.test_2()
    # global t
    # t = 1
    # CT=TestClass()
    # p = Process(target=CT.test_f)
    # p.start()

    # ## will not exit if function finishes, only when
    # ## "q" is entered, but this is just a simple example
    # stop_char=""
    # # while stop_char.lower() != "q":   
    # while True:
    #     stop_char=input("Enter 'q' to quit ")
    #     # print(t)
    #     if stop_char.lower() == "q":
    #         print("pressed q")
    #         break
    #     if stop_char.lower() == "u":
    #         print("Input u")
    #         t = 2
    #     if stop_char.lower() == "e":
    #         print("Input u")
    #         t = 3
    #         ## do something else
    # print("terminate process")
    # if p.is_alive():
    #     # print("finished")
    #     p.terminate()