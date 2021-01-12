from pyA20.gpio import gpio
from pyA20.gpio import port
from threading import Thread, RLock
import threading
import sys
import datetime
import time
import singletonHistorian
import PostMan
import datetime

verrou = threading.RLock()


class Singleton(object):
    def __new__(cls, *args, **kw):
        if not hasattr(cls, '_instance'):
            orig = super(Singleton, cls)
            cls._instance = orig.__new__(cls, *args, **kw)
        return cls._instance


class Regulateur(Singleton):
    __instance = None
    flag_enable = 1
    elapsed = 0
    start = 0

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(Singleton, cls).__new__(cls)
            cls.__instance.__initialized = False
        return cls.__instance

    def __init__(self):
        if self.__initialized: return
        self.__initialized = True
        print("INIT REGULATEUR")
        dateStart = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        singletonHistorian.Historian().dateStart = dateStart

    def regule(self, tempCommand, client):
        tempCommand = singletonHistorian.Historian().getActualCommandTemp()
        actualTemp = singletonHistorian.Historian().getActualTemp()

        with verrou:
            if tempCommand > actualTemp:
                if self.flag_enable:
                    singletonHistorian.Historian().stateBooler = 1
                    self.flag_enable = 0
                    gpio.output(port.PA3, gpio.HIGH)
                    gpio.output(port.PA0, gpio.HIGH)
                    self.start = time.time()
            else:
                if self.flag_enable == 0:
                    singletonHistorian.Historian().stateBooler = 0
                    self.flag_enable = 1
                    gpio.output(port.PA3, gpio.LOW)
                    gpio.output(port.PA0, gpio.LOW)
                    self.elapsed += time.time() - self.start
                    singletonHistorian.Historian().workedTime += self.elapsed
                # gpio.output(port.PA2, gpio.LOW)

    def checkDate(self):
        day = datetime.datetime.now().strftime("%A")
        actualHour = int(datetime.datetime.now().strftime("%H")) * 60 + int(datetime.datetime.now().strftime("%M"))
        prog = singletonHistorian.Historian().prog[day]
        if not singletonHistorian.Historian().manuelMode:
            if actualHour <= prog[0]:
                singletonHistorian.Historian().actualMode = "nightMode"
                singletonHistorian.Historian().setActualCommandTemp(
                    singletonHistorian.Historian().getTempCommand("night"))
            elif prog[0] < actualHour <= prog[1]:
                singletonHistorian.Historian().actualMode = "insideMode"
                singletonHistorian.Historian().setActualCommandTemp(
                    singletonHistorian.Historian().getTempCommand("inHouse"))
            elif prog[1] < actualHour <= prog[2]:
                singletonHistorian.Historian().actualMode = "outsideMode"
                singletonHistorian.Historian().setActualCommandTemp(
                    singletonHistorian.Historian().getTempCommand("outHouse"))
            elif prog[2] < actualHour <= prog[3]:
                singletonHistorian.Historian().actualMode = "insideMode"
                singletonHistorian.Historian().setActualCommandTemp(
                    singletonHistorian.Historian().getTempCommand("inHouse"))
            elif prog[3] < actualHour < 1440:
                singletonHistorian.Historian().actualMode = "nightMode"
                singletonHistorian.Historian().setActualCommandTemp(
                    singletonHistorian.Historian().getTempCommand("night"))
