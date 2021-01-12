import singletonHistorian
import sys


def readSavedData():
    # Ouverture du fichier source
    src = open("data.csv", "r")
    for k in range(0, 7):
        data = src.readline().rstrip('\n\r').split(",")
        if k == 0:
            singletonHistorian.Historian().setTempCommand("night", int(data[5]))
            singletonHistorian.Historian().setTempCommand("inHouse", int(data[6]))
            singletonHistorian.Historian().setTempCommand("outHouse", int(data[7]))
        singletonHistorian.Historian().setProg(data[0], int(data[1]), int(data[2]), int(data[3]), int(data[4]))
    src.close()


def writeSavedData():
    try:
        # Ouverture du fichier destination
        dst = open("data.csv", "w")
        for cle, valeur in singletonHistorian.Historian().prog.items():
            if cle == "Monday":
                print(int(valeur[0]))
                dst.write("%s,%d,%d,%d,%d,%d,%d,%d\n" % (
                    cle, int(valeur[0]), int(valeur[1]), int(valeur[2]), int(valeur[3]),
                    singletonHistorian.Historian().getTempCommand("night"),
                    singletonHistorian.Historian().getTempCommand("inHouse"),
                    singletonHistorian.Historian().getTempCommand("outHouse")))
            else:
                dst.write("%s,%d,%d,%d,%d\n" % (cle, int(valeur[0]), int(valeur[1]), int(valeur[2]), int(valeur[3])))
        dst.close()
    except:
        print("write saved data")


def readTempData():
    try:
        src = open("tempData.csv", "r")
        for k in range(0, 5):
            data = src.readline().rstrip('\n\r').split(",")
            if data:
                for d in data:
                    if k == 0:
                        singletonHistorian.Historian().addReleaseData(int(d))
                    elif k == 1:
                        singletonHistorian.Historian().addDateData(int(d))
                    elif k == 2:
                        singletonHistorian.Historian().addReleaseCityData(int(d))
                    elif k == 3:
                        singletonHistorian.Historian().addConsigneTemp(int(d))
                if k == 4:
                    singletonHistorian.Historian().workedTime = int(data[0])
        src.close()
    except:
        print(sys.exc_info())


def writeTempData():
    try:
        print("Write temp data")
        # Ouverture du fichier destination
        dst = open("tempData.csv", "w")
        _releaseData = singletonHistorian.Historian().values
        for d in range(0, len(_releaseData)):
            if _releaseData[d]:
                if len(_releaseData) - 1 == d:
                    dst.write("%d" % _releaseData[d])
                else:
                    dst.write("%d," % _releaseData[d])
        dst.write("\n")
        _date = singletonHistorian.Historian().date
        for d in range(0, len(_date)):
            if _date[d]:
                if len(_date) - 1 == d:
                    dst.write("%d" % _date[d])
                else:
                    dst.write("%d," % _date[d])
        dst.write("\n")
        _cityData = singletonHistorian.Historian().valuesTempCity
        for d in range(0, len(_cityData)):
            if _cityData[d]:
                if d == len(_cityData) - 1:
                    dst.write("%d" % _cityData[d])
                else:
                    dst.write("%d," % _cityData[d])
        dst.write("\n")
        _consigneTemp = singletonHistorian.Historian().consigneTemp
        for d in range(0, len(_consigneTemp)):
            if _consigneTemp[d]:
                if len(_consigneTemp) - 1 == d:
                    dst.write("%d" % _consigneTemp[d])
                else:
                    dst.write("%d," % _consigneTemp[d])
        dst.write("\n")
        dst.write("%d" % singletonHistorian.Historian().workedTime)
        dst.close()
    except:
        print(sys.exc_info())
