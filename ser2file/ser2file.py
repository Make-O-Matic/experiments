#!/usr/bin/env python3
import sys
import serial
import datetime

if __name__=='__main__':
	try:
		ser = serial.Serial('COM1', 115200, timeout=1)
		print("opened " + ser.portstr)
	except serial.SerialException:
		print('could not open port')
		sys.exit(1)
		pass
	f = open(datetime.datetime.now().strftime("%y-%m-%d_%H-%M-%S") + '.csv', 'w+')
	f.write('10ms;x;y;z;delta\n')
	i = 0
	line = ser.readline().decode('utf-8') # Truncate first read line
	try:
		while True:
			line = ser.readline().decode('utf-8')
			if line:
				f.write(str(i) + ';' + line)
				i = i + 1
			print(line)
	except KeyboardInterrupt:
		pass

	f.close()
	ser.close()
