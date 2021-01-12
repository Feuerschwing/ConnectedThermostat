import paho.mqtt.client as mqtt
import sys
import singletonProtocol

topic = "sensorsData"

Protocol = singletonProtocol.Protocol()


def on_message(client, userdata, message):
    Protocol.decodeJsonTram(str(message.payload.decode("utf-8")))


def on_connect(client, userdata, flags, rc):
    print("connected")
    client.connected_flag=True
    client.subscribe("androidDevice")


def on_disconnect(client, packet, exc=None):
    print("DISCONNECTED")
    logging.info('[DISCONNECTED {}]'.format(client._client_id))


def on_subscribe(client, mid, qos):
    print("subscribe")


def send_msg(client):
    try:
        client.publish(topic, Protocol.encodeJsonTram())
    except :
        print(sys.exc_info())


def send_msg_temp_data(client, data, date, cityData, consigneTemp, workedTime, dateStart):
    print("send temp data")
    try:
        client.publish(topic, Protocol.encodeJsonTramTempData(data, date, cityData, consigneTemp, workedTime, dateStart))
    except :
        print(sys.exc_info())


def openConnection(client):
    client.loop_forever()
