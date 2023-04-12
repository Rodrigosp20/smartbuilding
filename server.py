import os
import socket

def main():
    os.chdir('Mosquitto_Server')
    hostname=socket.gethostname()   
    IPAddr=socket.gethostbyname(hostname)
    print(f'Your server ip address is:{IPAddr}')
    try:
        os.system('cmd /k "mosquitto -v -c mosquitto.conf"')
    except:
        print('runned')
        os.chdir(os.path.dirname(os.getcwd()))


if __name__ == '__main__':
    main()
