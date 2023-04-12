import sys
import paho.mqtt.client as mqtt
import time
from mqtt_functions import *


def onMessage(client, userdata, message):
    topic = str(message.topic)
    content = str(message.payload.decode("utf-8"))
    
   
    roomId = topic.split('/')[4]
   
    if (content in ['on','off']):
        client.publish(f'{topicOut}/{roomId}', f'{content}', retain = True)
        print(f'Light is now {content} in room {roomId}')
        return
    
    print(f'Invalid command: {content}')


def main():
    if (len(sys.argv) != 2):
        print('Invalid number of arguments...\nExisting...')
        return
    
    homeName = sys.argv[1]

    global topicIn , topicOut
    topicIn= f"light/house/{homeName}/room/+"
    topicOut = f'status/light/house/{homeName}/room'
    
    try:
        client = connectToServer(id = f'light_unit_{homeName}', port = 1883, debug = False, onMessageFunc= onMessage)
    except:    
        print('Error connecting to the server.')
        return
    
    print(f'Welcome to Multiroom Light System of {homeName}\'s house!')
    print('Successfully connect to the Mqtt Server')
    print(f'Subscibed to the topics: {topicIn}')
    client.subscribe(topicIn)

    try:
        input()
    except:
        pass
    
    client.loop_stop()
    print('Exiting...')


if __name__ == '__main__':
    main()