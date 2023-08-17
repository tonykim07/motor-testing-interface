
from threading import Timer, Lock

class TimeLoop():

    def __init__(self, time_interval, function, *args, **kwargs): 
        self.lock = Lock()
        self.timer = None
        self.time_interval = time_interval
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.running = False
        self.start_loop()

    def setup(self): 
        self.running = False
        self.start_loop()
        self.function(*self.args, **self.kwargs)

    def start_loop(self): 
        self.lock.acquire()
        if not self.running: 
            self._timer = Timer(self.time_interval, self.setup)
            self._timer.start()
            self.running = True
        self.lock.release()
        
    def stop_loop(self): 
        self.timer.cancel()
        self.running = False