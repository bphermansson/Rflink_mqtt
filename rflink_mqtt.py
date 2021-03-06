#!/usr/bin/env python

''' 
This code reads weather data from a Rflink (http://www.rflink.nl) and sends out data via Mqtt.
https://github.com/bphermansson/Rflink_mqtt
'''
import time
import serial
import paho.mqtt.client as mqtt
import json
import config
import sys
import traceback

MQTT_HOST = '192.168.1.190'
MQTT_PORT = 1883
MQTT_TOPIC = 'Rflink'

'''
Set username and password for Mqtt-server in a file called "config.py":
MQTT_USER = 'user'
MQTT_PASS = 'pass'
'''

ser = serial.Serial(
 port='/dev/ttyACM0',
 baudrate = 57600,
 parity=serial.PARITY_NONE,
 stopbits=serial.STOPBITS_ONE,
 bytesize=serial.EIGHTBITS,
 timeout=1
)

while 1:
 x=ser.readline()
 
 if len(x) > 60: # Ignore start message from Rflink
  # Extract data from Rflink and create a Mqtt message
  x=x.rstrip()
  print (x)
  # Can look like:
  # 20;01;DKW2012;  ID=0022;TEMP=00a6;HUM=69;WINSP=0056;WINGS=00ab;RAIN=2871;WINDIR=0004;BAT=OK;
  # 20;05;Alecto V2;ID=0069;TEMP=0113;HUM=36;WINSP=0000;WINGS=0000;RAIN=0000;BAT=OK;

  try:
    x = str(x)
    inputdata = x.split(';')
    name = inputdata[2]
    id = inputdata[3].split('=')
    id = id[1]
    temp = inputdata[4].split('=')
    temp = temp[1]
    hum = inputdata[5].split('=')
    hum = hum[1]
    winsp = inputdata[6].split('=')
    winsp = winsp[1]
    wings = inputdata[7].split('=')
    wings = wings[1]
    rain = inputdata[8].split('=')
    rain = rain[1]
    if (name == "DKW2012"):
      winddir = inputdata[9].split('=')
      winddir = winddir[1]
      batt = inputdata[10].split('=')
      batt = batt[1]
    else:
      batt = inputdata[9].split('=')
      batt = batt[1]
      winddir = "NA"	# This unit doesnt measure wind direction
  except AttributeError:
    traceback.print_exc()

  # Convert temp from hex format to human readable
  '''
  http://www.rflink.nl/blog2/protref
  TEMP=9999 => Temperature celcius (hexadecimal), high bit contains negative sign, needs division by 10 (0xC0 = 192 decimal = 19.2 degrees)
                      => (example negative temperature value: 0x80DC, high bit indicates negative temperature 0xDC=220 decimal the client '''

  try:
    temphex = temp[1:] # Get last three chars
    #print temphex
    tempdec = int(temphex,16)	# Convert to decimal
    #print tempdec	# Temp * 10
    tempf = tempdec / float(10) # Force tempf to be a float to preserve decimals
    sign = temp[:1]	# Highest bit is set when negative temperature
    if (sign == '8'):
  	  charsign = "-"
    else:
  	  charsign = ""
  	  
    comptemp = charsign + str(tempf)
    #print comptemp

    data = {}
    data['count'] = inputdata[1]
    data['device'] = inputdata[2]
    data['id'] = id
    data['temp'] = comptemp
    data['hum'] = hum
    data['winsp'] = winsp
    data['wings'] = wings
    data['rain'] = rain
    data['winddir'] = winddir
    data['bat'] = batt
  except AttributeError:
    traceback.print_exc()
  
  jsondata = json.dumps(data)

#  print ("Send mqtt")

  full_topic = MQTT_TOPIC + "/" + data['device']  
  try:
    mqtt_client = mqtt.Client()
#    mqtt_client.username_pw_set(config.MQTT_USER, config.MQTT_PASS)
    mqtt_client.connect(MQTT_HOST, MQTT_PORT)
    mqtt_client.publish(full_topic, jsondata)
  except:
    print ("Unexpected error:", sys.exc_info()[0])
