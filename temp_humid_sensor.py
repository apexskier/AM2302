from subprocess import Popen, PIPE
from threading import Thread
import time, datetime
import RPi.GPIO as GPIO
import os

class Thermostat(object):
    def __init__(self, pin, target_temp):
        self.TARGET_TEMP = target_temp
        self.current_temp = None
        self.last_time = None
        self.RELAY = pin
        self.RUNNING = True
        self.HEAT_ON = False

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.RELAY, GPIO.OUT)
        GPIO.output(self.RELAY, False)

    def run(self):
        def run_():
            while self.RUNNING:
                th_cmd = Popen(["./temp_humid_sensor", str(4)], stdout=PIPE)
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
