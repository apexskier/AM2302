from subprocess import Popen, PIPE, call
from threading import Thread
import getpass
import time, datetime
import os
import wiringpi2 as wiringpi
import _cwd
#wiringpi.wiringPiSetupGpio()
wiringpi.wiringPiSetupSys()

class Thermostat(object):
    def __init__(self, out_pin, in_pin, target_temp=55):
        self.target_temp = target_temp
        self.current_temp = None
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

    def run(self):
        def run_():
            while self.running:
                th_cmd = Popen(["sudo", self.PATH + "/temp_humid_sensor", str(self.INPUT)], stdout=PIPE)
                th_out, th_err = th_cmd.communicate()

                if th_out and th_out != "err":
                    self.last_time = time.strftime("%H:%M:%S")
                    temp, humid = th_out.split(',')
                    self.current_temp = (9.0 / 5.0) * float(temp) + 32
                    if self.current_temp < self.target_temp - 2 and not self.heat_on:
                        self.heat_on = True
                        wiringpi.digitalWrite(self.THERM, 1)
                    elif self.current_temp >= self.target_temp and self.heat_on:
                        self.heat_on = False
                        wiringpi.digitalWrite(self.THERM, 0)

                time.sleep(10)
        self.t = Thread(target=run_)
        return self.t

    def set(self, target_temp):
        self.target_temp = float(target_temp)
        if self.current_temp and self.current_temp < self.target_temp - 2 and not self.heat_on:
            self.heat_on = True
            wiringpi.digitalWrite(self.THERM, 1)
        elif self.current_temp >= self.target_temp and self.heat_on:
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

    def off(self):
        self.running = False
        wiringpi.digitalWrite(self.THERM, 0)

if __name__ == '__main__':
    import signal
    thermostat = Thermostat(17, 4)
    tt = thermostat.run()

    def sig_handler(signal, frame):
        print("Waiting for Thermostat to finish.")
        tt.join()
        sys.exit(0)
    signal.signal(signal.SIGINT, sig_handler)

    try:
        tt = thermostat.run()
        tt.start()
        for i in range(0, 5):
            print(thermostat.get_temp(), thermostat.get_last_time())
            time.sleep(5)
        tt.join()
    finally:
        pass
