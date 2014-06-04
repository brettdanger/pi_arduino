import serial, time, datetime, sys
from xbee import XBee

SERIALPORT = "/dev/ttyAMA0"    # the com/serial port the XBee is connected to
BAUDRATE = 38400      # the baud rate we talk to the xbee
TEMPSENSE = 0       # which XBee ADC has current draw data

ser = serial.Serial(SERIALPORT, BAUDRATE)

xbee = XBee(ser)
print 'Starting Up Tempature Monitor'
# Continuously read and print packets
while True:
    try:
        response = xbee.wait_read_frame()
        print response

	
#	test = xbee.find_packet()
#	print test
    except KeyboardInterrupt:
        break
        
ser.close()
