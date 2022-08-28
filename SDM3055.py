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
#-----------------------------------------------------------------------------
# Device IP
remote_ip = "192.168.3.51" # should match the instrument’s IP address
port = 5025 # the port number of the instrument service
#-----------------------------------------------------------------------------
# CSV file setting
location = ''
filename = 'M1'
header = ['time', 'VDC']    # setup the header of the CSV file as you need
#-----------------------------------------------------------------------------
# Measurements parameters
count = 5   # amount of measurements
interval = 1    # interval betwween measurements in seconds s
# type of measurement, refer to https://bit.ly/3R07mlq
measlist = [['Voltage DC', 'MEAS:VOLT:DC?'], ['Current DC', 'MEAS:CURR:DC?'], ['Voltage AC', 'MEAS:VOLT:AC?'], ['Current AC', 'MEAS:CURR:AC?'], ['Temperature', 'MEAS:TEMP?'], ['Frequency', 'MEAS:FREQ?'], ['Resistance 2-wire', 'MEAS:RES?'], ['Resistance 4-wire', 'MEAS:FRES?'], ['Capacitance', 'MEAS:CAP?']]
#-----------------------------------------------------------------------------
# Variables

def SocketConnect():
    try:
        #create an AF_INET, STREAM socket (TCP)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error:
        print ('Failed to create socket.')
        sys.exit();
        156 / 158
    try:
        #Connect to remote server
        s.connect((remote_ip , port))
    except socket.error:
        print ('failed to connect to ip ' + remote_ip)
    return s

def SocketQuery(Sock, cmd):
    
    try :
        #Send cmd string
        Sock.sendall(cmd)
        Sock.sendall(b'\n')
        time.sleep(1)
    except socket.error:
        #Send failed
        print ('Send failed')
        sys.exit()
    reply = Sock.recv(4096)
    return reply

def SocketClose(Sock):
    #close the socket
    Sock.close()
    time.sleep(.300)

def cleanqStr(qStr):
    return eval(str(qStr.strip(b'\n')).strip('b'))

def getDeviceIDN(s):
    IDN = SocketQuery(s, b'*IDN?')
    print('DEVICE:\n' + cleanqStr(IDN))

 
def main():
    global remote_ip
    global port
    global count
    # Body: send the SCPI commands *IDN? 10 times and print the return message
    s = SocketConnect()
    getDeviceIDN(s);

    println('\n*******************************\nSCPI python: automation measurement\n*******************************\n')

    print('\nMEASUREMENTS PARAMETERS:\n')

    count = input('Enter the amount (a number) of measures you want to do: ')
    interval = input('Enter the interval in seconds between measurement: ')

    
    print('\nMeasurement types:\n')

    for i in range(len(measlist)):
        print(str(i) + ": " + measlist[i][0])

    meassel = int(input('\nSelect the measurement type from the list above (enter the line number): '))

    measurement = measlist[meassel][1]


    filename = ''
    filename = input('\nEnter the name of the csv file for the data that you want to use: ')

    while(len(filename) < 2):
        filename = input('Filename too short, try again: ')


    # crete the csv file with the header
    path = location + filename + ".csv"

    print('Data storage location: ' + path)

    if exists(path):
        key = input('\nWARNING:\nFile already exists! Press "ENTER" to override and continue or CTRL+C to Cancel\n')


    with open(path, 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['time', measlist[meassel][0]])

    print('Measurements parameters\nCount: ' + str(count) + '\nInterval: ' + str(interval) + ' seconds\nMeasurement: ' + measlist[meassel][0] + '\n')

    input('Press "Enter" to start')

    print('\nMeasures:\n')

    for i in range(int(count)):
        qStr = SocketQuery(s, bytes(measurement, 'ascii'))
        qStr = cleanqStr(qStr)
        date = datetime.now()

        # log measurements
        print (str(i+1) + " of " + str(count) + " | " + date.strftime("%d/%m/%Y") + " @ " + date.strftime("%H:%M:%S") + " | " + measlist[meassel][0] + ": " + qStr)

        # write data to csv file
        with open(path, 'a', encoding='UTF8', newline='') as f:
            writer = csv.writer(f)            
            writer.writerow([date, qStr])

        # interval time    
        time.sleep(int(interval))
    
    SocketClose(s)

    print('\nMeasures done!\n')

    input('Press "Enter" to exit')
 
if __name__ == '__main__':
    proc = main()
