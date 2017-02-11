#!/usr/bin/env python
from __future__ import print_function
from subprocess import call
import sys
import serial
import datetime
from cobs import cobs
import struct
import csv
import json
import ctypes

csv_caption = ['rfid','ex','ey','ez','ax','ay','az','graspa','graspb','graspc','key','wear','lastnr']
stdaddr = '00:06:66:4F:B8:91'
port = '/dev/rfcomm0'
rate = 115200

def unpack_pkg(stream):
	pkg = struct.unpack('12sffffffHHHB', stream)
	flags.asbyte = pkg[10]
	pkg = list(pkg)
	pkg = tuple(pkg[:-1] + [flags.b.key,flags.b.wear,flags.b.lastnr])
	return pkg

c_uint8 = ctypes.c_uint8
class Flags_bits(ctypes.LittleEndianStructure):
	_fields_ = [
		("key", c_uint8, 1),
		("wear", c_uint8, 1),
		("lastnr", c_uint8, 1),
	]
class Flags(ctypes.Union):
	_fields_ = [("b", Flags_bits),
		("asbyte", c_uint8)]
flags = Flags()

def ftread(): # Fault tolerant read for connection loss
	global ser
	while True:
		try:
			return ser.read()
		except serial.serialutil.SerialException:
			ser.close()
			ser = serial.Serial(port, rate, timeout=1)
			pass

if __name__=='__main__':
	global ser
	addr = str(raw_input("MAC[%s]: " % stdaddr))
	if len(addr) is 0:
		addr = stdaddr
	call(['rfcomm', 'bind', port, '%s' % addr])
#	call(['chmod', 'a+r', port]) # unnecessary after usermod -a -G dialout <user>
	try:
		ser = serial.Serial(port, rate, timeout=1)
		print("opened " + ser.portstr)
	except serial.SerialException:
		print('could not open port')
		sys.exit(1)
		pass
	with open(datetime.datetime.now().strftime("%y-%m-%d_%H-%M-%S") + '.txt', 'w+') as f:
		csv_f = csv.writer(f)
		csv_f.writerow(csv_caption)
		line = ""
		try:
			while True: # truncate first incomplete packet
				if ftread() == '\0':
					break
			while True:
				c = ftread()
				if c == '\0': # got packet separator
					try:
						pkg = unpack_pkg(cobs.decode(line))
						print('%8.3f %+8.3f %+8.3f   ' % (pkg[1], pkg[2], pkg[3]), end='')
						print('%+7.3f %+7.3f %+7.3f   ' % (pkg[4], pkg[5], pkg[6]), end='')
						print('%4d %4d %4d   ' % (pkg[7], pkg[8], pkg[9]), end='')
						print('%d %d %d  ' % (pkg[10], pkg[11], pkg[12]), end='')
						print('%12s' % (pkg[0]))
						csv_f.writerow(pkg)
					except (cobs.DecodeError, struct.error):
						pass
					line = ""
				else:
					line += c
		except KeyboardInterrupt:
			pass
		f.close()
	ser.close()
	call(['rfcomm', 'release', port, '%s' % addr])
