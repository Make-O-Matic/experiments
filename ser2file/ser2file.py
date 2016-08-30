#!/usr/bin/env python3
import sys
import serial
import datetime
from cobs import cobs
import struct
import csv
import json
import ctypes

csv_caption = ['rfid','ex','ey','ez','ax','ay','az','myo','key','sw','capsens','lastnr']
def unpack_pkg(stream):
	pkg = struct.unpack('12sffffffHB', stream)
	flags.asbyte = pkg[8]
	pkg = list(pkg)
	pkg = tuple(pkg[:-1] + [flags.b.key,flags.b.sw,flags.b.capsens,flags.b.lastnr])
	return pkg

c_uint8 = ctypes.c_uint8
class Flags_bits(ctypes.LittleEndianStructure):
	_fields_ = [
		("key", c_uint8, 1),
		("sw", c_uint8, 1),
		("capsens", c_uint8, 1),
		("lastnr", c_uint8, 1),
	]
class Flags(ctypes.Union):
	_fields_ = [("b", Flags_bits),
		("asbyte", c_uint8)]
flags = Flags()

if __name__=='__main__':
	try:
		ser = serial.Serial('/dev/ttyUSB1', 115200, timeout=1)
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
			while True:
				if ser.read() == '\0':
					break
			while True:
				c = ser.read()
				if c == '\0':
					pkg = unpack_pkg(cobs.decode(line))
					print(json.JSONEncoder().encode(pkg))
					csv_f.writerow(pkg)
					line = ""
				else:
					line += c
		except KeyboardInterrupt:
			pass
		f.close()
	ser.close()
