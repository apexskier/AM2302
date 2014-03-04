from subprocess import call
import threading, datetime
import am2302_ths

class Sensor(object):
    def __init__(self, pin):
        self.current_temp = None
        self.temp = None
        self.humid = None
        self.last_time = None
        self.INPUT = pin

        call(["gpio", "export", str(self.INPUT), "in"])

        self.timer = threading.Timer(0, self.tick)
        self.timer.start()

    def tick(self):
        try:
            temp = am2302_ths.get_temperature(self.INPUT)
            if temp:
                self.last_time = datetime.datetime.now()
                self.temp = temp
            self.timer = threading.Timer(10, self.tick)
            self.timer.start()
        except:
            self.off()
            print("Error reading from sensor.")

    def get(self):
        return self.temp

    def get_last_time(self):
        return self.last_time

    def off(self):
        self.timer.cancel()

    def __del__(self):
        self.off()
