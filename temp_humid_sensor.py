from subprocess import Popen, PIPE, call
from threading import Thread
import getpass
import time, datetime
import os
import wiringpi
GPIO = wiringpi.GPIO(wiringpi.GPIO.WPI_MODE_SYS)

class Thermostat(object):
    def __init__(self, out_pin, in_pin, target_temp=55):
        self.TARGET_TEMP = target_temp
        self.current_temp = None
        self.last_time = None
        self.RELAY = out_pin
        self.INPUT = in_pin
        self.RUNNING = True
        self.HEAT_ON = False

        user = getpass.getuser()
        call(["/usr/local/bin/gpio", "export", str(self.RELAY), "out"])
        call(["/usr/local/bin/gpio", "export", str(self.INPUT), "in"])

        GPIO.pinMode(self.RELAY, GPIO.OUTPUT)
        GPIO.pinMode(self.RELAY, GPIO.INPUT)
        GPIO.digitalWrite(self.RELAY, GPIO.LOW)

    def run(self):
        def run_():
            while self.RUNNING:
                th_cmd = Popen(["sudo", "./temp_humid_sensor", str(self.INPUT)], stdout=PIPE)
                th_out, th_err = th_cmd.communicate()

                if th_out != "err":
                    self.last_time = time.strftime("%H:%M:%S")
                    temp, humid = th_out.split(',')
                    self.current_temp = (9.0 / 5.0) * float(temp) + 32
                    if self.current_temp < self.TARGET_TEMP - 2 and not self.HEAT_ON:
                        self.HEAT_ON = True
                        GPIO.output(self.RELAY, self.HEAT_ON)
                    elif self.current_temp >= self.TARGET_TEMP and self.HEAT_ON:
                        self.HEAT_ON = False
                        GPIO.output(self.RELAY, self.HEAT_ON)

                time.sleep(10)
        self.t = Thread(target=run_)
        return self.t

    def set_(self, target_temp):
        self.TARGET_TEMP = float(target_temp)
        if self.current_temp and self.current_temp < self.TARGET_TEMP - 2 and not self.HEAT_ON:
            self.HEAT_ON = True
            GPIO.output(self.RELAY, self.HEAT_ON)
        elif self.current_temp >= self.TARGET_TEMP and self.HEAT_ON:
            self.HEAT_ON = False
            GPIO.output(self.RELAY, self.HEAT_ON)


    def get_temp(self):
        return self.current_temp
    def get_last_time(self):
        if self.last_time:
            return " (" + self.last_time + ")"
        else:
            return None
    def get_target(self):
        return self.TARGET_TEMP

    def to_off(self):
        self.RUNNING = False
        GPIO.output(self.RELAY, False)

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
