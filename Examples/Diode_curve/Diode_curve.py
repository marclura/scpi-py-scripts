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
import matplotlib.pyplot as plt

#-----------------------------------------------------------------------------
# Device IP
ip = '192.168.3.229' # should match the instrument’s IP address Multimeter
port = 5025 # the port number of the instrument service
#-----------------------------------------------------------------------------
# CSV file setting
location = r'data'
filename = 'diode_curve'
battery_id = ''
header = ['U[V]', 'I[A]']    # setup the header of the CSV file as you need
#-----------------------------------------------------------------------------
# Variables
interval = 1
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

    feedback = False  #weather or not a feedback is expected
    reply = ""

    if("?" in command) == True:
        feedback = True

    cmd = bytes(command, 'ascii')

    try:
        #Send cmd string
        Sock.sendall(cmd)
        Sock.sendall(b'\n')
        time.sleep(0.5)
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

    print("\n------ DIODE CURVE ------\n")
    choice = input("Current IP address: " + ip + ' Press "Y" to change it or "N" to continue...')
    
    if choice == "Y":
        ip = input("Enter the IP address of the device: ")

    s = SocketConnect(ip, port)
    getDeviceIDN(s)


    # Setup of the file
    item_id = input("\nDiode name to name the file accordingly: \n")
    

    save_file = input("Do you wnat to save the file? Default -> NO. If yes type 'y'");


    # setup of the channels
    
    current_limit = float(input("Indicate the I[A] current limit: "))
    voltage_limit = float(input("Indicate the U[V] voltage limit: "))
    voltage_increment = float(input("Indicate the voltage increment: "))
    
    print("Values choosed | current_limit: " + str(current_limit) + "A, voltage_limit: " + str(voltage_limit) + "V, voltage_increment: " + str(voltage_increment) + "V")

    print('\nSetting up the device ...')

    SocketQuery(s, 'INST CH1')
    SocketQuery(s, 'OUTP CH1,OFF')
    SocketQuery(s, 'CH1:CURR ' + str(current_limit))
    SocketQuery(s, 'CH1:VOLT 0.0')
    
    print('done!')
    
    input("Click SPACE to start the measurement");

    SocketQuery(s, 'OUTP CH1,ON');

    print('\nStarting the measurement!')
    
    date = datetime.now()

    path = location + '/' + filename + item_id + "_" + date.strftime("%Y%m%d_%H%M%S") + ".csv"

    print('Filename: ' + path)

    # write the CSV header
    with open(path, 'w+', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)

    
    curr_voltage = 0;
    
    run = True
    
    array_x = []
    array_y = []
    
    id_measure = 1
    


    # to run GUI event loop
    plt.ion()
    
    # here we are creating sub plots
    figure, ax = plt.subplots(figsize=(10, 8))
    line1, = ax.plot(array_x, array_y)
    ax.set_xlim(left=0, right=float(voltage_limit))
    ax.set_ylim(bottom=0, top=float(current_limit))
    
    # setting title
    plt.title(item_id, fontsize=20)
    plt.xlabel("U[V]")
    plt.ylabel("I[A]")
    
    # updating data values
    line1.set_xdata(array_x)
    line1.set_ydata(array_y)
    line1.set_linewidth(3)
    line1.set_color('b')
    
    # drawing updated values
    figure.canvas.draw()
    
    # This will run the GUI event
    # loop until all UI events
    # currently waiting have been processed
    figure.canvas.flush_events()
        
    

    while run == True:

        start = time.time()

        # print("Current voltage setup: " + str(curr_voltage))
        SocketQuery(s, 'CH1:VOLT ' + str(curr_voltage))
        voltage = SocketQuery(s, 'MEAS:VOLT? CH1')
        current = SocketQuery(s, 'MEAS:CURR? CH1')
        

        print(str(id_measure) + ":\tU[V]: " + voltage + " | I[A]: " + current)


        if (save_file == 'y'):
            # write data to csv file
            with open(path, 'a', encoding='UTF8', newline='') as f:
                writer = csv.writer(f)            
                writer.writerow([voltage, current])


        array_x.append(float(voltage))
        array_y.append(float(current))
        
        # updating data values
        line1.set_xdata(array_x)
        line1.set_ydata(array_y)
        
        # drawing updated values
        figure.canvas.draw()
        
        # This will run the GUI event
        # loop until all UI events
        # currently waiting have been processed
        figure.canvas.flush_events()
        
        if(curr_voltage > voltage_limit):
            run = False

        curr_voltage = curr_voltage + voltage_increment
        id_measure = id_measure + 1
        


    # swith off the power supply output!
    SocketQuery(s, 'OUTP CH1,OFF')
    
    # plt.show()
    
    
    
if __name__ == '__main__':
    proc = main()

