import paho.mqtt.client as mqtt
import time
import re
import socket

def onMessage(client, userdata, message):
    print("Received in the topic("+str(message.topic)+"): "+ str(message.payload.decode("utf-8")))

def onLog(client, userdata, level, buf):
    print("log: ",buf)

def onConnect(client, userdata, flags, rc):
    if (rc == 0):
        client.connected = True
    else:
        print("Error connecting Returned code:",rc)
        client.reconnect()

def connectToServer(id:str, port: int, debug: bool, onMessageFunc = None):
    client = mqtt.Client(id)
    client.on_connect=onConnect
    if (debug is True):
        client.on_log = onLog
    if (onMessageFunc is None):
        client.on_message = onMessage
    else:
        client.on_message = onMessageFunc

    client.connected = False
    
    #start a routine to check messages in the subscrived topics
    client.connect(host=socket.gethostbyname(socket.gethostname()), port= port)

    client.loop_start()
    while (not client.connected):
        time.sleep(0.5)

    return client

def stringToDict(string, pattern):
    regex = re.sub(r'{(.+?)}', r'(?P<_\1>.+)', pattern)
    values = list(re.search(regex, string).groups())
    keys = re.findall(r'{(.+?)}', pattern)
    _dict = dict(zip(keys, values))
    return _dict