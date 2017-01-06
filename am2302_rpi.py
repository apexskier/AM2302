import threading, datetime
import am2302_ths

class Sensor(object):
    def __init__(self, pin):
        self.current_temp = None
        self.temp = None
        self.humid = None
        self.last_time = None
        self.INPUT = pin

        self.timer = threading.Timer(0, self._tick)
        self.timer.start()

    def _tick(self):
        try:
            temp = am2302_ths.get_temperature(self.INPUT)
            humid = am2302_ths.get_humidity(self.INPUT)
            if temp:
                self.last_time = datetime.datetime.now()
                self.temp = temp
            if humid:
                self.last_time = datetime.datetime.now()
                self.humid = humid
            self.timer = threading.Timer(10, self._tick)
            self.timer.start()
        except:
            self.off()
            print("Error reading from sensor.")

    def get(self, data="temp"):
        if data is "temp":
            return self.temp
        elif data is "humid":
            return self.humid
        elif data is "both":
            return (self.temp, self.humid)

    def get_last_time(self):
        return self.last_time

    def off(self):
        self.timer.cancel()

    def __del__(self):
        self.off()
