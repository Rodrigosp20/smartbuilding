import sys
import paho.mqtt.client as mqtt
import time
from mqtt_functions import *
from tabulate import tabulate

DEFAULTVALUES = {'min_temp_True': 13, 'max_temp_True':25, 'safe_co2':5, 'max_co2':15,'min_temp_False': 9, 'max_temp_False':23, 'human':False, 'state_ac':False,'state_vent':False}

def onMessage(client, userdata, message):
    topic = str(message.topic)
    content = str(message.payload.decode("utf-8"))

    topicSplit = topic.split('/')
    id= topicSplit[0]
    roomId = topicSplit[5]

    if (id == 'avac'): # modification message

        param = convertParam(topicSplit[1])
        if param == None:
            return
        
        roomInfo = room.setdefault(roomId, DEFAULTVALUES)
        try:
            roomInfo[param] = int(content)
            print(F'{topicSplit[1]} was successfully changed to {content} in room {roomId}')
            checkLimits(roomId)
        except:
            print(f'{content} isn\'t a valid value')
        return
    
    if (id == 'sensor'): # sensor update message
        stimulus = topicSplit[1]
        try:
            value = int(content)
        except:
            print(f'Invalid {stimulus} value: {content}')
            return

        roomInfo = room.setdefault(roomId, DEFAULTVALUES)

        if stimulus == 'human':
            if value <= 0:
                roomInfo['human'] = False
            else:
                roomInfo['human'] = True
            return

        human = roomInfo['human']

        if stimulus == 'temp':
            if (roomInfo[f'min_temp_{human}'] > value):
                room[roomId]['state_ac'] = True
                client.publish(f'{topicAc}{roomId}', 'heating', retain = True)
                print(f'Room {roomId} is heating')
                return
            if (roomInfo[f'max_temp_{human}'] < value):
                room[roomId]['state_ac'] = True
                client.publish(f'{topicAc}{roomId}', 'cooling', retain = True)
                print(f'Room {roomId} is cooling')
                return
            if(roomInfo['state_ac']):
                room[roomId]['state_ac'] = False
                client.publish(f'{topicAc}{roomId}', 'off', retain = True)
                print(f'Room {roomId} ac is turned off')
                return


        if stimulus == 'co2':
            if (roomInfo['safe_co2'] > value and roomInfo['state_vent']):
                room[roomId]['state_vent'] = False
                client.publish(f'{topicVent}{roomId}', 'off', retain = True)
                print(f'Room {roomId} vent is turned off')
                return
            if (roomInfo['max_co2'] < value):
                room[roomId]['state_vent'] = True
                client.publish(f'{topicVent}{roomId}', 'on', retain = True)
                print(f'Room {roomId} vent is working')
                return
            if (roomInfo['state_vent']):
                room[roomId]['state_vent'] = False
                client.publish(f'{topicVent}{roomId}', 'off', retain = True)
                print(f'Room {roomId} vent is turned off')
                return
        return
    
def convertParam(param):
    if param == 'max_human':
        return 'max_temp_True'
    if param == 'max_empty':
        return 'max_temp_False'
    if param == 'min_human':
        return 'min_temp_True'
    if param == 'min_empty':
        return 'min_temp_False'
    if param == 'max_co2':
        return 'max_co2'
    if param == 'safe_co2':
        return 'safe_co2'
    return None

def checkLimits(roomId):
    lim = room[roomId]
    headers = ['-------------------------','Min','Max']
    table = [['Temperature With Humans',lim['min_temp_True'], lim['max_temp_True']], ['Temperature Without Humans', lim['min_temp_False'], lim['max_temp_False']], ['Co2 Levels',lim['safe_co2'], lim['max_co2']]]
    print(tabulate(table,headers, tablefmt="psql"))
    

def main():
    if (len(sys.argv) != 2):
        print('Invalid number of arguments...\nExisting...')
        return
    
    homeName = sys.argv[1]
    
    global room, topicAc, topicVent
    
    topicTemp = f'sensor/temp/house/{homeName}/room/+'
    topicCo2 = f'sensor/co2/house/{homeName}/room/+'
    topicHuman = f'sensor/human/house/{homeName}/room/+'
    topicMod = f'avac/+/house/{homeName}/room/+'
    topicAc = f'status/ac/house/{homeName}/room/'
    topicVent = f'status/vent/house/{homeName}/room/'

    room = {}
    
    try:
        client = connectToServer(id = f'avac_unit_{homeName}', port = 1883, debug = False, onMessageFunc= onMessage)
    except:
        print('Error connecting to the server.')
        return
    
    print(f'Welcome to Multiroom AVAC System of {homeName}\'s house!')
    
    client.subscribe(topicMod)
    print(f'Subscribed to the modification topics: {topicMod}')
    client.subscribe(topicTemp)
    print(f'Subscribed to the Temperature Update Topic: {topicTemp}')
    client.subscribe(topicCo2)
    print(f'Subscribed to the CO2 Update Topic: {topicCo2}')
    client.subscribe(topicHuman)
    print(f'Subscribed to the Human Update Topic: {topicHuman}')
    
    try:
        input()
    except:
        pass
    
    client.loop_stop()
    print('Exiting...')


if __name__ == '__main__':
    main()