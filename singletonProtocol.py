import json

# import singletonRegulateur
import datetime
import singletonHistorian
import FileManager
import traceback

json_message_Prog = """{
    "command": "progSchedule",
    "weekProg":
        {
            "Monday": [0, 240, 720, 900],
            "Tuesday": [50, 260, 800, 1400],
            "Thursday": [125, 400, 750, 1200],
            "Wednesday": [152, 200, 800, 1300],
            "Friday": [100, 350, 950, 1100],
            "Saturday": [150, 500, 900, 1100],
            "Sunday": [150, 450, 850, 1000]
        },
    "tempCommand":
        {
            "night": 17,
            "inHouse": 22,
            "outHouse": 19
        }
}"""
json_message_Prog1 = "{'command':'progSchedule'}"

json_message_askUpdateData = """{
    "command": "askUpdateData"
}"""

json_message_activeModeManuel = """{
    "command": "activeManuelMode",
    "consigne" : 22,
    "time" : 30
}"""

json_send_message = """{
    "command" : "sendData",
    "temperature" : 18,
    "humidity" : 41
}"""

# command that orangepi receives
ASK_UPDATE_DATA = "askUpdateData"
PROG_SCHEDULE_COMMAND = "progSchedule"
ACTIVE_MANUEL_MODE = "activeManuelMode"
ASK_SEND_DATA = "askSendData"
# data d by orangepi
SEND_DATA = "sendData"
SEND_BOOLER_STATE = "sendBoolerState"
SEND_TEMP_DATA = "sendTempData"


class Singleton(object):
    def __new__(cls, *args, **kw):
        if not hasattr(cls, '_instance'):
            orig = super(Singleton, cls)
            cls._instance = orig.__new__(cls)
        return cls._instance


class Protocol(Singleton):
    Historian = singletonHistorian.Historian()
    days = []
    periods = []
    __instance = None
    gestionnaireTimerReset = None
    gestionnaireTimerSendTempData = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(Singleton, cls).__new__(cls)
            cls.__instance.__initialized = False
        return cls.__instance

    def __init__(self):
        if self.__initialized: return
        self.__initialized = True
        print("INIT Protocol")
        self.days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        self.periods = ["night", "inHouse", "outHouse"]

    def decodeJsonTram(self, json_message):
        json_message = json_message.replace("'", '"')
        data = json.loads(json_message)
        if data["command"] == PROG_SCHEDULE_COMMAND:
            self.transformJsonProgData(data["weekProg"], data["tempCommand"])
        elif data["command"] == ASK_UPDATE_DATA:
            self.gestionnaireTimerReset()
        elif data["command"] == ACTIVE_MANUEL_MODE:
            try:
                self.gestionnaireTimerReset()
                singletonHistorian.Historian().manuelMode = True
                singletonHistorian.Historian().setActualCommandTemp(data["consigne"])
                singletonHistorian.Historian().actualMode = "manuelMode"
            except:
                print("b")
        elif data["command"] == ASK_SEND_DATA:
            print("receiveSend")
            singletonHistorian.Historian().city = data["city"]
            self.gestionnaireTimerSendTempData()

    def encodeJsonTram(self):
        return json.dumps({'command': SEND_DATA, 'temperature': singletonHistorian.Historian().actualTemp,
                           'humidity': singletonHistorian.Historian().actualHumidity,
                           'mode': singletonHistorian.Historian().actualMode,
                           'stateBooler': singletonHistorian.Historian().stateBooler}, indent=4)

    def encodeJsonTramTempData(self, value, date, cityValue, consigneTemp, workedTime, dateStart):
        return json.dumps({'command': SEND_TEMP_DATA, 'date': date, 'value': value, 'cityValue': cityValue,
                           'consigneTemp': consigneTemp, 'workedTime': workedTime, 'dateStart': dateStart}, indent=4)

    def transformJsonProgData(self, weekData, tempCommand):
        try:
            for day in self.days:
                singletonHistorian.Historian().setProg(day, int(weekData[day][0]), int(weekData[day][1]),
                                                       int(weekData[day][2]), int(weekData[day][3]))
            for period in self.periods:
                singletonHistorian.Historian().setTempCommand(period, tempCommand[period])
            FileManager.writeSavedData()
        except Exception:
            print(Exception)

    def setGestionnerTimerReset(self, gestionnaireTimerReset):
        self.gestionnaireTimerReset = gestionnaireTimerReset

    def setGestionnerTimerSendTempData(self, gestionnaireTimerSendTempData):
        self.gestionnaireTimerSendTempData = gestionnaireTimerSendTempData


"""
def main():
    print(singletonHistorian.Historian()._getProg())
    print(json_message_Prog)
    singletonProtocol.Protocol().decodeJsonTram(json_message_Prog)
    print(singletonHistorian.Historian()._getProg())


if __name__ == "__main__":
    main()"""
