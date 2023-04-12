import copy
import sys
import paho.mqtt.client as mqtt
import time
from mqtt_functions import *
import inquirer
import os
from tabulate import tabulate


def onMessage(client, userdata, message):
    topic = str(message.topic)
    content = str(message.payload.decode("utf-8"))
    keys = topic.split('/')
    subject, house, room = keys[0], keys[3], keys[5]

    if (room not in rooms[house]):
        rooms[house].insert(0,room)

    houseRooms = houses[house]
    roomInfo = houseRooms.setdefault(room,DEFAULTVALUES)

    if (subject == 'status'): #status update on the room

        param = keys[1]
        if (param == 'ac'):
            if (content in ['heating','cooling','off']):
                roomInfo['ac'] = content
            else:
                print(f'Invalid AC status: {content}')
            return

        if (param == 'light'):
            if (content in ['on','off']):
                roomInfo['light_toggle'] = content
            else:
                print(f'Invalid Light status: {content}')
            return
            
        if (param == 'vent'):
            if (content in ['on','off']):
                roomInfo['vent'] = content
            else:
                print(f'Invalid Vent status: {content}')
            return

    if (subject == 'sensor'): #sensorial upldates on the room
        param = keys[1]
        try:
            value = int(content)
        except:
            print(f'Invalid {param} value: {content}')
            return
        
        roomInfo[param] = value
        if (param == 'human' or param == 'light'): # light logic
            if (roomInfo['human'] <= 0 and roomInfo['light_toggle'] == True):
                client.publish(f'light/house/{house}/room/{room}','off', retain = True)
            
            if (roomInfo['human'] > 0 and value < roomInfo['light_threshold'] and  roomInfo['light_toggle'] == 'off'):
                client.publish(f'light/house/{house}/room/{room}','on', retain = True)
            
            if (roomInfo['human'] > 0 and value > roomInfo['light_threshold'] and  roomInfo['light_toggle'] == 'on'):
                client.publish(f'light/house/{house}/room/{room}','off', retain = True)
    return


DEFAULTVALUES = {'human':0, 'temp': 10, 'co2':10, 'light': 10, 'ac':'off', 'vent':'off', 'light_toggle':'off', 'light_threshold' : 10, 'version':1}


def main():

    try:
        client = connectToServer(id = 'management_app', port = 1883, debug = False, onMessageFunc= onMessage)
    except:
        print(f'Error connecting to mqtt server!')
        return

    print(f'Welcome to the Management System!')

    global houses, rooms
    houses = {}
    rooms = {}

    mainMenu(client)

    client.loop_stop()
    print('Exiting...')

def clearScreen():
    clear = lambda: os.system('cls')
    clear()

def mainMenu(client):
    
    while True:
        clearScreen()

        house_lst = []
        for house in houses.keys():
            house_lst.append((f'Enter {house} house',house))

        actions = [('Register a house','Register')]
        actions.extend(house_lst)
        actions.append('Exit')

        res = inquirer.list_input("Select one action",choices= actions)
        
        if (res == 'Exit'):
            break
    
        if (res == 'Register'):
            house = inquirer.text(message='What\'s house\'s name')
            houses[house] = {}
            rooms[house] = ['Back']
            client.subscribe(f'sensor/version/house/{house}/room/+')
            client.subscribe(f'sensor/temp/house/{house}/room/+')
            client.subscribe(f'sensor/co2/house/{house}/room/+')
            client.subscribe(f'sensor/light/house/{house}/room/+')
            client.subscribe(f'sensor/human/house/{house}/room/+')
            client.subscribe(f'status/light/house/{house}/room/+')
            client.subscribe(f'status/ac/house/{house}/room/+')
            client.subscribe(f'status/vent/house/{house}/room/+')
            continue

        menuHouse(res, client)


def menuHouse(house, client):
    while True:
        room = inquirer.list_input(f"Check {house}'s rooms",choices= rooms[house])

        if (room != 'Back'):
            while(True):
                res = inquirer.list_input(f"Select a option in {room}", choices = [('Log room info','Log'), ('Update Sensor','Update'), ('Change AVAC parameters','AVAC'), ('Change Light Threshold','Light'), 'Back'])
                
                if (res == 'Back'):
                    break

                if (res == 'Log'):
                    try:
                        logRoom(house, room, client)
                    except:
                        continue
                
                if (res == 'Light'):
                    try:
                        houses[house][room]['light_threshold'] = int(inquirer.text("Insert value"))
                    except:
                        print('Invalid value')
                    continue

                if (res == 'Update'):
                    client.publish(f'sensor/house/{house}/room/{room}','update', retain = False)
                    continue
                    
                if (res == 'AVAC'):
                    while(True):
                        param = inquirer.list_input(f"Select a parameter to edit", choices = [('Maximum Temperature with humans','max_human'), ('Minimum Temperature with humans','min_human'), ('Maximum Temperature without humans','max_empty'),('Minimum Temperature without humans','min_empty'), ('Minimum CO2 level','safe_co2'), ('Maximum CO2 level','max_co2'), 'Back'])
                        if param == 'Back':
                            break
                        
                        value = inquirer.text("Insert value")
                        client.publish(f'avac/{param}/house/{house}/room/{room}', value)
                    continue
        
        if(room == 'Back'):
            break
        
def compareRoomState(prev, now):
    for key in prev.keys():
        if (prev[key] != now[key]):
            return False
    return True


def logRoom(house, room, client):
    
    while True:
        prevInfo = copy.deepcopy(houses[house][room])
        clearScreen()
        table = []
        for key in prevInfo:
            table.append([key,prevInfo[key]])
        print(tabulate(table))

        
        info = houses[house][room]
        while (compareRoomState(prevInfo, info)):
            time.sleep(0.5)

    

    



if __name__ == '__main__':
    main()