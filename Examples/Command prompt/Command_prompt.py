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
ip = '' # should match the instrument’s IP address Multimeter
port = 5025 # the port number of the instrument service
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

    ip = input("Enter the IP address of the device: ");

    s = SocketConnect(ip, port)
    getDeviceIDN(s)


    while True:
        command = ""

        if command == "":
            command = input("Enter command: ")
            print(SocketQuery(s, command))


if __name__ == '__main__':
    proc = main()
