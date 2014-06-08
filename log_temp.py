import serial, time, datetime, sys
from xbee import XBee
import time
import sqlite3


def get_tempature(data, format="C"):
	#iterate over data elements
	readings = []
	for item in data:
		readings.append(item.get('adc-0'))
	
	#start by averaging the data
	volt_average = sum(readings)/float(len(readings))
	
	#now calculate the proper mv
	#we are using a 3.3v usb explorer so the formula is slightly different
	tempature = ((volt_average*3.2258) - 500) / 10.0	

	if format=="F":
		#convert to farenheit
		tempature = (tempature * 1.8) + 32

	return tempature


def save_temp_reading (zonestr, temp):
    # I used triple quotes so that I could break this string into
    # two lines for formatting purposes
    curs.execute("INSERT INTO tempature_log values( (?), (?), (?) )", (int(time.time()), zonestr,temp))

    # commit the changes
    conn.commit()

SERIALPORT = "/dev/ttyAMA0"    # the com/serial port the XBee is connected to
BAUDRATE = 38400      # the baud rate we talk to the xbee
TEMPSENSE = 0       # which XBee ADC has current draw data
ROOM = "Room1"  # for now, when we add a second unit we will change this

conn=sqlite3.connect('tempature.db')

curs=conn.cursor()

ser = serial.Serial(SERIALPORT, BAUDRATE)

xbee = XBee(ser)
print 'Starting Up Tempature Monitor'
# Continuously read and print packets
while True:
    try:
        response = xbee.wait_read_frame()
        print response
        tempature = get_tempature(response['samples'], format="F")	
		
	#print our timestamp and tempature to standard_out
	print "{0}, {1}".format(int(time.time()), tempature)
	
	#save the tempature to the databse
	save_temp_reading(ROOM, tempature)
	
    except KeyboardInterrupt:
        break
        
ser.close()
