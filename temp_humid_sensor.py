from subprocess import Popen, PIPE, call
import threading
import getpass
import time, datetime
import os
import logging
import wiringpi2 as wiringpi
import _cwd

#wiringpi.wiringPiSetupGpio()
wiringpi.wiringPiSetupSys()

class Thermostat(object):
    def __init__(self, out_pin, in_pin, target_temp=55):
        self.graphlogger = logging.getLogger(__name__)
        self.graphlogger.setLevel(logging.INFO)

        # create a file handler
        graphhandler = logging.FileHandler('thermostat.log')
        graphhandler.setLevel(logging.INFO)

        # create a logging format
        graphformatter = logging.Formatter('{"time": "%(asctime)s", %(message)s},')
        graphhandler.setFormatter(graphformatter)

        # add the handlers to the logger
        self.graphlogger.addHandler(graphhandler)

        self.target_temp = target_temp
        self.current_temp = None
        self.temp = None
        self.humid = None
        self.last_time = None
        self.THERM = out_pin
        self.INPUT = in_pin
        self.running = True
        self.heat_on = False
        self.OUT = 1
        self.IN = 0
        self.PWM = 0

        self.PATH = str(_cwd).split()[3][1:-10]

        call(["gpio", "export", str(self.THERM), "out"])
        call(["gpio", "export", str(self.INPUT), "in"])

        wiringpi.digitalWrite(self.THERM, 0)

        self.timer = threading.Timer(1, self.tick)
        self.timer.start()

    def __repr__(self):
        return 'thermostat'

    def tick(self):
        if self.running:
            self.timer.cancel()
            self.timer = threading.Timer(60 * 5, self.tick)
            self.timer.start()

        th_cmd = Popen(["sudo", self.PATH + "/temp_humid_sensor", str(self.INPUT)], stdout=PIPE)
        th_out, th_err = th_cmd.communicate()

        if th_out and th_out != "err":
            self.last_time = time.strftime("%Y-%m-%d %H:%M:%S")
            temp, humid = th_out.split(',')
            self.temp = temp
            self.humid = humid
            self.current_temp = (9.0 / 5.0) * float(temp) + 32
            if self.current_temp < self.target_temp - 2 and not self.heat_on:
                self.heat_on = True
                wiringpi.digitalWrite(self.THERM, 1)
            elif self.current_temp >= self.target_temp and self.heat_on:
                self.heat_on = False
                wiringpi.digitalWrite(self.THERM, 0)

        if self.temp and self.humid and self.target_temp:
            self.graphlogger.info('"temp": {}, "humid": {}, "target": {}, "mtime": "{}"'.format(
                self.temp,
                self.humid,
                self.target_temp,
                self.last_time
            ))

    def set(self, target_temp):
        self.target_temp = float(target_temp)
        if self.current_temp and self.current_temp < self.target_temp and not self.heat_on:
            self.heat_on = True
            wiringpi.digitalWrite(self.THERM, 1)
        elif self.current_temp > self.target_temp and self.heat_on:
            self.heat_on = False
            wiringpi.digitalWrite(self.THERM, 0)

    def get(self):
        return self.current_temp
    def get_last_time(self):
        if self.last_time:
            return self.last_time
        else:
            return None
    def get_target(self):
        return self.target_temp

    def get_status(self):
        return self.heat_on

    def off(self):
        self.timer.cancel()
        self.running = False
        wiringpi.digitalWrite(self.THERM, 0)

if __name__ == '__main__':
    import signal
    def sig_handler(signal, frame):
        print("Stopping")
        thermostat.off()
        #sys.exit(0)
    signal.signal(signal.SIGINT, sig_handler)

    thermostat = Thermostat(17, 4)
