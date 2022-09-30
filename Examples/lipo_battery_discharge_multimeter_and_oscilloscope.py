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
sdm_ip = "192.168.3.51" # should match the instrument’s IP address Multimeter
port = 5025 # the port number of the instrument service
sds_ip = "192.168.3.50"	# multimeter
#-----------------------------------------------------------------------------
# CSV file setting
location = ''
filename = 'lipo_1500_4ohms_discharge'
header = ['time', 'VDC', 'DCI']    # setup the header of the CSV file as you need
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
    print('\nDEVICE properly connected:\n' + IDN)

def SocketClose(s):
    #close the socket
    s.close()
    time.sleep(.300)

def cleanqStr(qStr):
    return eval(str(qStr.strip(b'\n')).strip('b'))


def main():
	global sdm_ip
	global sds_ip
	count = 0

	sdm = SocketConnect(sdm_ip, port)
	getDeviceIDN(sdm)

	#sds = SocketConnect(sds_ip, port)
	#getDeviceIDN(sds)

	#interval = int(input("Interval in seconds (s) of the measurements: \n"))

	date = datetime.now()

	path = filename + "_" + date.strftime("%Y%m%d_%H%M%S") + ".csv"

	print('Filename: ' + path)

	# write the CSV header
	with open(path, 'w', encoding='UTF8', newline='') as f:
		writer = csv.writer(f)
		writer.writerow(['time', 'I[A]', 'U[V]'])


	#input('\nPress "Enter" to start the measurements\n')

	print('Measurement started...\n')

	# setup the channels
	"""
	print('STAT? ' + cleanqStr(SocketQuery(sdm, bytes('ROUT:STAT?', 'ascii'))))
	SocketQuery(sdm, bytes('ROUT:SCAN ON', 'ascii'))
	SocketQuery(sdm, bytes('ROUT:STAR ON', 'ascii'))
	print(cleanqStr(SocketQuery(sdm, bytes('ROUT:DATA? 1', 'ascii'))))
	print(cleanqStr(SocketQuery(sdm, bytes('ROUT:DATA? 2', 'ascii'))))
	SocketQuery(sdm, bytes('ROUT:STAR OFF', 'ascii'))
	"""

	while True:
		command = ""

		if command == "":
			command = input("Enter command: ")
			print(SocketQuery(sdm, command))

	"""
	while(True):
		SocketQuery(sdm, bytes('ROUT:FUNC STEP', 'ascii'))
		SocketQuery(sdm, bytes('ROUT:LIMI:LOW 1', 'ascii'))
		SocketQuery(sdm, bytes('ROUT:LIMI:HIGH 2', 'ascii'))
		SocketQuery(sdm, bytes('ROUT:DEL 1', 'ascii'))
		SocketQuery(sdm, bytes('ROUT:CHAN 1,ON,DCV,200V,SLOW', 'ascii'))
		SocketQuery(sdm, bytes('ROUT:CHAN 2,ON,DCV,200V,SLOW', 'ascii'))
		SocketQuery(sdm, bytes('ROUT:COUN 1', 'ascii'))
		SocketQuery(sdm, bytes('ROUT:STAR ON', 'ascii'))

		# SDM (current I[A])
		current = SocketQuery(sdm, bytes('ROUT:DATA? 1', 'ascii'))
		current = cleanqStr(current)

		# SDM (voltage U[V])		
		current = SocketQuery(sdm, bytes('ROUT:DATA? 2', 'ascii'))
		current = cleanqStr(current)

		SocketQuery(sdm, bytes('ROUT:SCAN OFF', 'ascii'))

		# SDS (voltage U[V])
		#voltage = SocketQuery(sds, bytes(measurement, 'ascii'))
		#voltage = cleanqStr(voltage)


		# time
		date = datetime.now()

		# count
		count = count + 1

		# log measurements
		print (str(count) + " | " + date.strftime("%d/%m/%Y") + " @ " + date.strftime("%H:%M:%S") + " | I[A]: " + current + ' | V[V]' + voltage)

		# write data to csv file
		with open(path, 'a', encoding='UTF8', newline='') as f:
		    writer = csv.writer(f)            
		    writer.writerow([date, current, voltage])

		# interval time    
		time.sleep(int(interval))
	"""






if __name__ == '__main__':
    proc = main()