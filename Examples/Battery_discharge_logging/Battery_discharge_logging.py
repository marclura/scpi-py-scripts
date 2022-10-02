#!/usr/bin/env python
#-----------------------------------------------------------------------------
# https://github.com/marclura/scpi-py-scripts
# Python scripts for Standard Commands for Programmable Instruments
#-----------------------------------------------------------------------------
import socket # for sockets
import sys # for exit
import time # for sleep
import csv # for file saving
from os.path import exists
from datetime import datetime
from array import *
import re
import numpy as np
#-----------------------------------------------------------------------------
# Device IP
ip = '192.168.3.51' # should match the instrument’s IP address Multimeter
port = 5025 # the port number of the instrument service
#-----------------------------------------------------------------------------
# CSV file setting
location = 'data'
filename = 'battery_discharge_'
battery_id = ''
header = ['Date', 'Time', 'I[A]', 'U[V]']    # setup the header of the CSV file as you need
#-----------------------------------------------------------------------------
# Variables
interval = 0
#-----------------------------------------------------------------------------



def SocketConnect(remote_ip, port):
    try:
        #create an AF_INET, STREAM socket (TCP)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error:
        print ('Failed to create socket.')
        sys.exit();

    try:
        #Connect to remote server
        s.connect((remote_ip , port))
    except socket.error:
        print ('failed to connect to ip ' + remote_ip)

    return s

def SocketQuery(Sock, command):

    feedback = False	#weather or not a feedback is expected
    reply = ""

    if("?" in command) == True:
        feedback = True

    cmd = bytes(command, 'ascii')

    try:
        #Send cmd string
        Sock.sendall(cmd)
        Sock.sendall(b'\n')
        time.sleep(1)
    except socket.error:
        #Send failed
        print ('Send failed')
        sys.exit()

    if feedback:
        reply = cleanqStr(Sock.recv(4096))

    return reply


def getDeviceIDN(s):
    IDN = SocketQuery(s, '*IDN?')
    print('\nDEVICE properly connected:\n' + IDN + '\n')

def SocketClose(s):
    #close the socket
    s.close()
    time.sleep(.300)

def cleanqStr(qStr):
    return eval(str(qStr.strip(b'\n')).strip('b'))


def main():
    global ip

    print("\n------ BATTERY DISCHARGE LOGGING STARTED ------\n")
    choice = input("Current IP address: " + ip + ' Press "Y" to change it or "N" to continue...')
    
    if choice == "Y":
        ip = input("Enter the IP address of the device: ")

    s = SocketConnect(ip, port)
    getDeviceIDN(s)


    # Setup of the file
    battery_id = input("\nType the battery ID to name the file accordingly: \n")

    date = datetime.now()

    path = location + '/' + filename + battery_id + "_" + date.strftime("%Y%m%d_%H%M%S") + ".csv"

    print('Filename: ' + path)

    # write the CSV header
    with open(path, 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)


    shunt_resistor = 0.997

    # define the SHUNT resistor value to calculate the current
    shunt_resistor = float(input("\nInput the value of the SHUNT Resistor in ohms: "))

    # definig the measue interval
    interval = int(input("\nType the interval time in seconds between each series of measurements: "))


    # setup of the channels

    print('\nSetting up the device ...')

    scan_mode = SocketQuery(s, 'ROUT:SCAN?')
    if(scan_mode == "OFF"):
        SocketQuery(s, 'ROUT:SCAN ON')	# enter in scan mode
    else:
        if(SocketQuery(s, 'ROUT:STAR?') == "ON"):
            SocketQuery(s, 'ROUT:STAR OFF')
    SocketQuery(s, 'ROUT:FUNC SCAN')
    SocketQuery(s, 'ROUT:DEL 1')	# 1 second of delay
    SocketQuery(s, 'ROUT:COUN 1')	# take one scan at the time only, not a sequence
    SocketQuery(s, 'ROUT:LIMI:LOW 1')
    SocketQuery(s, 'ROUT:LIMI:HIGH 2')
    SocketQuery(s, 'ROUT:CHAN 1,ON,DCV,20V,SLOW')
    SocketQuery(s, 'ROUT:CHAN 2,ON,DCV,20V,SLOW')

    print('done!')

    print('\nStarting the measurement!')


    run = True

    measuring_channels = int(SocketQuery(s, 'ROUT:LIMI:HIGH?')) - int(SocketQuery(s, 'ROUT:LIMI:LOW?'))
    # print('measuring_time: ' + str(measuring_time))

    while run == True:

        start = time.time()

        SocketQuery(s, 'ROUT:STAR ON')

        date = datetime.now()

        time.sleep(3 + measuring_channels*1)

        voltage_shunt = SocketQuery(s, 'ROUT:DATA? 1')
        voltage = SocketQuery(s, 'ROUT:DATA? 2')

        voltage_shunt = re.sub('([A-DF-Z]+|\s+|,+)', '', voltage_shunt)		#remove the unit from the string
        #print('cur: ' + voltage_shunt)
        voltage = re.sub('([A-DF-Z]+|\s+|,+)', '', voltage)
        #print('vol: ' + voltage)


        shunt_factor = 0.60752

        current = float(voltage_shunt) / shunt_resistor * shunt_factor
        voltage = float(voltage)

        current = round(current, 4)
        voltage = round(voltage, 4)

        current = np.format_float_positional(current)
        voltage = np.format_float_positional(voltage)

        _date = date.strftime("%d/%m/%Y")
        _time = date.strftime("%H:%M:%S")

        print(_date + " @ " + _time + " | I[A]: " + current + " | U[V]: " + voltage)
        SocketQuery(s, 'ROUT:STAR OFF')


        # write data to csv file
        with open(path, 'a', encoding='UTF8', newline='') as f:
            writer = csv.writer(f)            
            writer.writerow([_date, _time, current, voltage])




        while (time.time() - start < interval):
            pass



if __name__ == '__main__':
    proc = main()
