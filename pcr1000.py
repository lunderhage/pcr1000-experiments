#!/usr/bin/python3

# A simple proof of concept to control the most basic functions of the
# PCR1000.

import serial
import enum
import re
import subprocess
from prompt_toolkit.contrib.shortcuts import get_input

Filters =  {'2K8': '00', '6K': '01', '15K': '02', '50K': '03', '230K': '04'}
ModulationModes = {'LSB': '00', 'USB': '01', 'AM': '02', 'CW': '03', 'FM': '05', 'WFM': '06'}


class PCR1000():

	def __init__(self):
		self.mode = ModulationModes['WFM']
		self.filter = Filters['230K']
		self.frequency = 107100000
		self.serial = serial.Serial(
		        port="/dev/ttyS0",
		        baudrate=9600
		)
		print("Using ", self.serial.portstr, "...")

	def start(self):
		print("Issuing Power-On command...")
		self._sendCommand("H101")
		self._sendCommand("H101")
		self._sendCommand("G105");

		self.serial.close();
		self.serial = serial.Serial(
	        	port="/dev/ttyS0",
			baudrate=38400,
		)
		self.serial.setRTS(True)
		self.serial.setDTR(True)
		self._sendCommand("H101")

	def stop(self):
		self._sendCommand("H100")
		self.serial.setRTS(False)
		self.serial.setDTR(False)
		self.serial.close()	

	def step(self, step):
		print("Stepping frequency " + step)
		self.frequency += self._parseFrequency(step)
		self.setFrequency(self.frequency)

	def sweep(self, range, step):
		print("Sweeping " + range + " in steps of " + step)

	def _parseFrequency(self, frequency):
		try:
                	return int(frequency)
		except:
                	try:
                		return int(float(frequency) * 1000000)
                	except:
                		print("Invalid frequency input: \"", frequency, "\"")
                		return 0

	def setFrequency(self, frequency: str):
		frequencyHz = self._parseFrequency(frequency)
		if (frequencyHz >= 50000 or frequencyHz <= 1300000000):
			self.frequency = frequencyHz
			command = self._constructKCommand()
			self._sendCommand(command)
		else:
			print("Frequency out of range")

	def setModulationMode(self, mode):
		mode = mode.upper()
		if (mode in ModulationModes):
			self.mode = ModulationModes[mode]
			command = self._constructKCommand()
			self._sendCommand(command)
		else:
			print("Invalid mode.")

	def setFilter(self, filter):
		filter = filter.upper()
		if (filter in Filters):	
			self.filter = Filters[filter] 
			command = self._constructKCommand()
			self._sendCommand(command)
		else:
			print("Invalid filter.")

	def setVolume(self, volume: int):
		if (volume >= 0 or volume <= 255):
			self._sendCommand("J40" + hex(volume)[2:].upper())
		else:
			 print("Volume out of range! (0-255)")

	def setSquelch(self, squelch: int):
		if (squelch >= 0 or squelch <= 255):
                        self._sendCommand("J41" + hex(squelch)[2:].upper())
		else:
			print("Squelch out of range! (0-255)")


	def _sendCommand(self, command):
		print("Sending command: " + command)
		self.serial.write(bytearray(command+"\n", "ascii"))
		self.serial.flush()

	def _constructKCommand(self):
		return "K0" + str(self.frequency).zfill(10) + self.mode + self.filter + "00"

	def startStream(self):
		pass
		# Command: gst-launch-1.0 -v alsasrc ! "audio/x-raw, format=S16LE,rate=44100,channels=1" ! audioconvert ! vorbisenc quality=0.9 ! oggmux ! tcpserversink host=0.0.0.0 port=8000

	def stopStream(self):
		pass


print ("PCR1000 Test... \n")

pcr = PCR1000()

pcr.start()
pcr.setFrequency(118100000)
pcr.setModulationMode("am")
pcr.setFilter("15k")
pcr.setVolume(100)
pcr.startStream()


while(1==1):
	commandLine = get_input("Command: ")
	command = re.search("(\w+)", commandLine).group(1)
	match = re.search("\w+(.*)", commandLine)
	if (match == None):
		arguments = []
	else:
		arguments = match.group(1).split(" ")
	#arguments = re.search("\s+(.*)", commandLine).group(1)
	#test = arguments.split(" ")
	#print("Test: ", test, type(test))
	print("Exec command: " + str(command) + " Arguments: " + str(arguments))

	if (command == None):
		break;
	elif (command == "exit"):
		break;
	elif (command == "freq"):
		freq = arguments[1]
		pcr.setFrequency(freq)
	elif (command == "vol"):
		vol = int(arguments[1])
		pcr.setVolume(vol)
	elif (command == "squelch"):
		squelch = int(arguments[1])
		pcr.setSquelch(squelch)
	elif (command == "filter"):
		filter = arguments[1]
		pcr.setFilter(filter)
	elif (command == "mode"):
		mode = arguments[1]
		pcr.setModulationMode(mode)
	elif (command == "step"):
		step = arguments[1]
		pcr.step(step)
	elif (command == "sweep"):
		range = arguments[1]
		step = arguments[2]
		pcr.sweep(range, step)
	else:
		print("Unknown command");
	
pcr.stop()
