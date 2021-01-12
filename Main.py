import paho.mqtt.client as mqtt
from pyA20.gpio import gpio
from pyA20.gpio import port
import dht22
import datetime
import PostMan
import singletonRegulateur
import PerpetualTimer
import threading
import sys
import Main
import singletonHistorian
import singletonProtocol
import FileManager
# Import the module and
import pyky040
import tm1637
import ADS1115
from math import log
import logging
import pyowm

from logging.handlers import RotatingFileHandler

logger = None

# from segmentsDisplay import Display

beta = 3950.0
Vcc = 3.3
R = 100000.0
r0 = 100000.0
t0 = 298.0
display_i = 0

my_encoder = None
instance = None
disp = None
owm = None


class Singleton(object):
    def __new__(cls, *args, **kw):
        if not hasattr(cls, '_instance'):
            orig = super(Singleton, cls)
            cls._instance = orig.__new__(cls)
        return cls._instance


Historian = singletonHistorian.Historian()
Protocol = singletonProtocol.Protocol()
GestionnaireTimer = None


class gestionnaireTimer(Singleton):
    displayDelay = 4
    timeUpdateData = 8
    timeRegulation = 0.5
    timeCheckProg = 1
    timeManuelMode = 3600
    timeSendTempData = 1800
    Regulateur = singletonRegulateur.Regulateur()

    timerDisplay = None
    timerSend = None
    timerRegule = None
    timerCheckProg = None
    timerManuelMode = None
    timerSendTemps = None

    def __init__(self, client):
        try:
            Main.logger.info("INIT GESTIONNAIRE TIMER")
            if isinstance(self.timerDisplay, PerpetualTimer.PerpetualTimer):
                self.timerDisplay.cancel()
            if isinstance(self.timerSend, PerpetualTimer.PerpetualTimer):
                self.timerSend.cancel()
            if isinstance(self.timerRegule, PerpetualTimer.PerpetualTimer):
                self.timerRegule.cancel()
            if isinstance(self.timerCheckProg, PerpetualTimer.PerpetualTimer):
                self.timerCheckProg.cancel()
            if isinstance(self.timerManuelMode, PerpetualTimer.PerpetualTimer):
                self.timerManuelMode.cancel()
            if isinstance(self.timerSendTemps, PerpetualTimer.PerpetualTimer):
                self.timerSendTemps.cancel()
            # idem for display timer
            self.client = client
            self.timerDisplay = PerpetualTimer.PerpetualTimer(self.displayDelay, self.display, "null")
            self.timerDisplay.start()
            self.timerSend = PerpetualTimer.PerpetualTimer(self.timeUpdateData, self.send_msg, self.client)
            self.timerSend.start()
            self.timerRegule = PerpetualTimer.PerpetualTimer(self.timeRegulation, self.regule, 15)
            self.timerRegule.start()
            self.timerCheckProg = PerpetualTimer.PerpetualTimer(self.timeCheckProg, self.checkDate, "null")
            self.timerCheckProg.start()
            self.timerManuelMode = threading.Timer(self.timeManuelMode, self.cancelManuelMode)
            self.timerManuelMode.start()
            self.timerSendTemps = PerpetualTimer.PerpetualTimer(self.timeSendTempData, self.sendTempsData, "null")
            self.timerSendTemps.start()
        except:
            print(sys.exc_info())

    def resetTimers(self):
        if isinstance(self.timerDisplay, PerpetualTimer.PerpetualTimer):
            self.timerDisplay.cancel()
        if isinstance(self.timerSend, PerpetualTimer.PerpetualTimer):
            self.timerSend.cancel()
        if isinstance(self.timerRegule, PerpetualTimer.PerpetualTimer):
            self.timerRegule.cancel()
        if isinstance(self.timerCheckProg, PerpetualTimer.PerpetualTimer):
            self.timerCheckProg.cancel()
        if isinstance(self.timerManuelMode, PerpetualTimer.PerpetualTimer):
            self.timerManuelMode.cancel()

        self.timerDisplay = PerpetualTimer.PerpetualTimer(self.displayDelay, self.display, "null")
        self.timerDisplay.start()
        self.timerSend = PerpetualTimer.PerpetualTimer(self.timeUpdateData, self.send_msg, self.client)
        self.timerSend.start()
        self.timerRegule = PerpetualTimer.PerpetualTimer(self.timeRegulation, self.regule, 15)
        self.timerRegule.start()
        self.timerCheckProg = PerpetualTimer.PerpetualTimer(self.timeCheckProg, self.checkDate, "null")
        self.timerCheckProg.start()
        self.timerManuelMode = threading.Timer(self.timeManuelMode, self.cancelManuelMode)
        self.timerManuelMode.start()

    def sendTempsData(self, null):
        try:
            observation = owm.weather_at_place(singletonHistorian.Historian().city)
            w = observation.get_weather()
            temperature = w.get_temperature('celsius').get("temp")
            print(temperature)
            singletonHistorian.Historian().addReleaseCityData(temperature)
        except:
            print(sys.exc_info())
            Main.Main.logger.info(sys.exc_info())
        singletonHistorian.Historian().addConsigneTemp(None)
        singletonHistorian.Historian().addReleaseData(None)
        singletonHistorian.Historian().addDateData(datetime.datetime.now().strftime("%Y%m%d%H%M%S"))
        FileManager.writeTempData()

    def display(self, null):
        temp = singletonHistorian.Historian().getActualCommandTemp()
        now = datetime.datetime.now()
        try:
            if Main.display_i == 1:
                Main.disp.set_doublepoint(False)
                Main.disp.set_values([(temp / 10) % 10, temp % 10, 'o', 'C'])
                Main.display_i = 0
            elif Main.display_i == 0:
                Main.disp.set_doublepoint(True)
                Main.disp.set_values([(now.hour / 10) % 10, now.hour % 10, (now.minute / 10) % 10, now.minute % 10])
                Main.display_i = 1
        except:
            print(sys.exc_info())
            Main.Main.logger.info(sys.exc_info())

    def readData(self, instance):
        try:
            byte_array = ADS1115.read_ADC(0)
            value = (byte_array[0] << 8) | byte_array[1]
            tension = (value * 0.1875) / 1000.0
            rt = (tension / Vcc * R) / (1.0 - tension / Vcc)
            temp = (log(rt / r0) / beta) + (1.0 / t0)
            temp = 1.0 / temp
            result = instance.read()
            singletonHistorian.Historian().actualTemp = round(temp - 273, 1)
            if result.is_valid():
                singletonHistorian.Historian().actualHumidity = result.humidity
        except:
            Main.Main.logger.info(sys.exc_info())

    def checkDate(self, null):
        try:
            singletonRegulateur.Regulateur().checkDate()
        except:
            print(sys.exc_info())

    def cancelManuelMode(self):
        Historian.manuelMode = False

    def updateData(self):
        try:
            self.send_msg(self.client)
        except:
            print(sys.exc_info())

    def send_msg(self, client):
        try:
            PostMan.send_msg(client)
        except:
            print(sys.exc_info())

    def regule(self, tempCommand):
        self.Regulateur.regule(tempCommand, self.client)

    def launchReguleTimer(self, tempCommand):
        self.timerRegule.cancel()
        self.timerRegule = PerpetualTimer.PerpetualTimer(self.timeRegulation, self.regule, tempCommand)
        self.timerRegule.start()

    def sendTempData(self):
        try:
            PostMan.send_msg_temp_data(client, singletonHistorian.Historian().values,
                                       singletonHistorian.Historian().date,
                                       singletonHistorian.Historian().valuesTempCity,
                                       singletonHistorian.Historian().consigneTemp,
                                       singletonHistorian.Historian().workedTime,
                                       singletonHistorian.Historian().dateStart)
        except:
            print(sys.exc_info())

    def _getTimerSend(self):
        return self.timerSend

    def _getTimerRegule(self):
        return self.timerRegule

    def _setTimerSend(self, timerSend):
        self.timerSend = timerSend

    def _setTimerRegule(self, timerRegule):
        self.timerSend = timerRegule


PIN_TEMP = port.PA6
PIN_RELAY = port.PA0
PIN_LED = port.PA3

PIN_DIO = port.PA19
PIN_CLK = port.PA18

# variables
tempCommand = 15
broker = "m12.cloudmqtt.com"
login = "vaqibjet"
password = "BAXSjqcv_1vi"
encoder_value = None
idClient = "client-01"

APPID = '74be88781b6c233e202169c47b6bf892'

timerCancelDisp = None
first = 1
temp = None
timerDisplayEmpty = None


def my_callback(scale_position):
    try:
        if Main.first:
            Main.my_encoder.set_counter(singletonHistorian.Historian().getActualCommandTemp())
        if isinstance(Main.timerCancelDisp, threading._Timer):
            Main.timerCancelDisp.cancel()
        Main.timerCancelDisp = threading.Timer(5, Main.cancelRotDisp)
        Main.timerCancelDisp.start()
        Main.display_i = -1
        Main.temp = round(scale_position)
        Main.display_rotary_temp(round(scale_position))
        Main.first = 0

    except:
        Main.Main.logger.info(sys.exc_info())
    # disp.set_values([int((scale_position)/10)%10,int(scale_position)%10, 'o', 'C'])


def display_rotary_temp(scale_position):
    try:
        Main.disp.set_doublepoint(False)
        Main.disp.set_values([int(scale_position / 10) % 10, int(scale_position) % 10, 'o', 'C'])
    except:
        Main.Main.logger.info(sys.exc_info())


def pressed_callback():
    try:
        Main.cancelRotDisp()
        singletonHistorian.Historian().manuelMode = True
        singletonHistorian.Historian().actualMode = "manuelMode"
        singletonHistorian.Historian().setActualCommandTemp(int(Main.temp))
        Main.GestionnaireTimer.resetTimers()
    except:
        Main.Main.logger.info(sys.exc_info())
    # settempCommand = encoder_value
    # annulation watchdog


def cancelRotDisp():
    if (isinstance(Main.timerCancelDisp, threading._Timer)):
        Main.timerCancelDisp.cancel()
    Main.first = 1
    Main.display_i = 0


# initialisation des gpio

client = 0


def main():
    FileManager.readSavedData()
    FileManager.readTempData()
    Main.owm = pyowm.OWM(Main.APPID)  # You MUST provide a valid API key
    gpio.init()
    gpio.setcfg(PIN_RELAY, gpio.OUTPUT)
    gpio.setcfg(PIN_LED, gpio.OUTPUT)
    Main.instance = dht22.DHT22(pin=PIN_TEMP)
    Main.disp = tm1637.TM1637(PIN_CLK, PIN_DIO)
    Main.disp.set_brightness(2)
    Main.my_encoder = pyky040.Encoder(CLK=10, DT=2, SW=13)

    Main.logger = logging.getLogger()
    Main.logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s')
    file_handler = RotatingFileHandler('activity.log', 'a', 1000000, 1)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    Main.logger.addHandler(file_handler)
    Main.client = mqtt.Client(idClient)
    Main.client.on_connect = PostMan.on_connect
    Main.client.on_message = PostMan.on_message
    Main.client.on_subscribe = PostMan.on_subscribe
    Main.client.on_disconnect = PostMan.on_disconnect
    Main.client.username_pw_set(login, password)
    Main.client.connect(broker, 10222)
    Main.GestionnaireTimer = Main.gestionnaireTimer(Main.client)
    timerReadSensor = PerpetualTimer.PerpetualTimer(0.5, Main.GestionnaireTimer.readData, Main.instance)
    timerReadSensor.start()
    Protocol.setGestionnerTimerReset(Main.GestionnaireTimer.resetTimers)
    Protocol.setGestionnerTimerSendTempData(Main.GestionnaireTimer.sendTempData)

    Main.my_encoder.setup(scale_min=0, scale_max=25, step=0.5, chg_callback=my_callback, sw_callback=pressed_callback)
    my_thread = threading.Thread(target=Main.my_encoder.watch)
    # Launch the thread
    my_thread.start()
    Main.logger.info("Start program")

    PostMan.openConnection(Main.client)


if __name__ == "__main__":
    main()
