from time import sleep
from queue import Queue
from threading import Thread 

messageQueue = Queue(1)

class myThread(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.name = "I'm thread"
        self.is_alive = False
    
    def kill(self):
        self.is_alive = False

    def run(self):
        self.is_alive = True
        while (self.is_alive):
            print("Thread id: %d" % (self.native_id))
            sleep(1)

def popFromQueue():
    while True:
        msg = messageQueue.get()
        if msg == "END":
            print("Ending...")
            break
        else:
            print("Message: -%s-" % msg)

def pushToQueue():
    while True:
        if messageQueue.empty():
            msg = input(">>> ")
            messageQueue.put(msg)
            if msg == "END":
                break
    print("Exiting...")

if __name__ == "__main__":
    inputThread = Thread(target=pushToQueue)
    outputThread = Thread(target=popFromQueue)

    outputThread.start()
    inputThread.start()

    inputThread.join()
    outputThread.join()