import settings
import threading
import time
from relais_client import RelaisClient


class DoorOperation(threading.Thread):

    def __init__(self, lock, op):
        self.lock = lock
        self.op = op

        super(DoorOperation, self).__init__()
    
    def run(self):

        if not self.lock.acquire( False ):
            print "Operation currently in progress. Exiting thread"
            return False

        pp = RelaisClient( settings.relais_host, settings.relais_port, username=settings.relais_user, password=settings.relais_pass )

        if self.op == True:
            self.open_door( pp )   
        elif self.op == False:
            self.close_door( pp )

        self.lock.release()


    def open_door(self, pp):

        # set door summer
        pp.setPort(2, 1)
        time.sleep(3)
        pp.setPort(2, 0)

        #open the door
        pp.setPort(0, 1)
        time.sleep(0.1)
        pp.setPort(0, 0)

    def close_door(self, pp):
        
        #close the door
        pp.setPort(1, 1)
        time.sleep(0.1)
        pp.setPort(1, 0)


