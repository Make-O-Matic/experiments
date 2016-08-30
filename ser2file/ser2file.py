#!/usr/bin/env python3
import sys
import serial
import datetime
from cobs import cobs
import struct
import csv
import json

csv_caption = ['rfid','ex','ey','ez','ax','ay','az','myo','keyswcaplastnr']
def unpack_pkg(stream):
	pkg = struct.unpack('12sffffffHB', stream)
	return pkg

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
