import threading
import traceback

lock = threading.RLock()
LENGTH_DATA_RELEASE = 96


class Singleton(object):
    def __new__(cls, *args, **kw):
        if not hasattr(cls, '_instance'):
            orig = super(Singleton, cls)
            cls._instance = orig.__new__(cls)
        return cls._instance


class Historian(Singleton):
    prog = {}
    tempCommand = {}
    values = [None] * LENGTH_DATA_RELEASE
    date = [None] * LENGTH_DATA_RELEASE
    valuesTempCity = [None] * LENGTH_DATA_RELEASE
    consigneTemp = [None] * LENGTH_DATA_RELEASE
    city = "Les Sables d'Olonne"
    workedTime = 0
    dateStart = None
    stateBooler = 0
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(Singleton, cls).__new__(cls)
            cls.__instance.__initialized = False
        return cls.__instance

    def __init__(self):
        if self.__initialized: return
        self.__initialized = True
        print("INIT HISTORIAN")
        self.actualTemp = 20
        self.actualHumidity = 50
        self.prog = {
            "Monday": [0, 4, 12, 15],
            "Tuesday": [5, 5.5, 15, 22],
            "Wednesday": [2, 13, 15.5, 23],
            "Thursday": [0, 8, 16, 18],
            "Friday": [3, 6, 15, 20],
            "Saturday": [4, 8, 15, 19.5],
            "Sunday": [1, 5, 16.5, 20.5]
        }
        self.tempCommand = {"night": 17, "inHouse": 24, "outHouse": 22}
        self.actualCommandTemp = 17
        self.actualMode = ""
        self.manuelMode = False

    def setProg(self, day, hour1, hour2, hour3, hour4):
        try:
            print(day, hour1, hour2, hour3, hour4)
            self.prog[day] = [hour1, hour2, hour3, hour4]
        except Exception:
            traceback.print_exc()

    def setTempCommand(self, namePeriod, temp):
        try:
            if 25 > temp >= 15:
                self.tempCommand[namePeriod] = temp
            else:
                self.tempCommand[namePeriod] = 15
        except:
            print(sys.exc_info())

    def setActualCommandTemp(self, actualCommandTemp):
        with lock:
            self.actualCommandTemp = actualCommandTemp

    def addReleaseCityData(self, cityTemp):
        self.valuesTempCity.append(cityTemp)
        self.valuesTempCity = self.valuesTempCity[-LENGTH_DATA_RELEASE:]

    def addReleaseData(self, temp):
        if temp:
            self.values.append(temp)
        else:
            self.values.append(self.actualTemp)
        self.values = self.values[-LENGTH_DATA_RELEASE:]

    def addDateData(self, datetime):
        self.date.append(int(datetime))
        self.date = self.date[-LENGTH_DATA_RELEASE:]

    def addConsigneTemp(self, consigneTemp):
        if consigneTemp:
            self.consigneTemp.append(consigneTemp)
        else:
            self.consigneTemp.append(self.actualCommandTemp)
        self.consigneTemp = self.consigneTemp[-LENGTH_DATA_RELEASE:]

    def getTempCommand(self, namePeriod):
        with lock:
            return self.tempCommand[namePeriod]

    def getActualTemp(self):
        with lock:
            return self.actualTemp

    def getActualHumidity(self):
        with lock:
            return self.actualHumidity

    def getActualCommandTemp(self):
        with lock:
            return self.actualCommandTemp
