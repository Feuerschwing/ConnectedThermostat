from pyA20.gpio import gpio
from pyA20.gpio import port
#from threading import Thread, RLock
import threading
PIN_RELAY = port.PA6
PIN_LED = port.PA10

verrou = threading.RLock()

class Regulateur:
    __instance = None
    _lock = threading.Lock()
    @staticmethod
    def getInstance():
        """ Static access method. """
        if Regulateur.__instance == None:
            with Regulateur._lock:
                if Regulateur.__instance == None:
                    Regulateur()
        return Regulateur.__instance

    def __init__(self):
        self.currentTemp = 15
        """ Virtually private constructor. """
        if Regulateur.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            Regulateur.__instance = self

    def regule(self, tempCommand):
        #currentTemp = sensor.getTemperature()
        currentTemp = self._getCurrentTemp()
        with verrou:
            if((tempCommand) > currentTemp):
                gpio.output(port.PA6, gpio.HIGH)
                gpio.output(port.PA10, gpio.HIGH)
            else:
                gpio.output(port.PA6, gpio.LOW)
                gpio.output(port.PA10, gpio.LOW)


    def _getCurrentTemp(self):
        return self.currentTemp

    def _setCurrentTemp(self, currentTemp):
        self.currentTemp = currentTemp
