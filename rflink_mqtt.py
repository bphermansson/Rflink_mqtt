#!/usr/bin/env python

''' 
This code reads weather data from a Rflink (http://www.rflink.nl) and sends out data via Mqtt.
'''
import time
import serial
import paho.mqtt.client as mqtt
import json

MQTT_HOST = '192.168.1.79'
MQTT_PORT = 1883
MQTT_USER = 'emonpi'
MQTT_PASS = 'emonpimqtt2016'
MQTT_TOPIC = 'Rflink'

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
  #print x
  inputdata = x.split(';')

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
  batt = inputdata[9].split('=')
  batt = batt[1]

  # Convert temp from hex format to human readable
  '''
  http://www.rflink.nl/blog2/protref
  TEMP=9999 => Temperature celcius (hexadecimal), high bit contains negative sign, needs division by 10 (0xC0 = 192 decimal = 19.2 degrees)
                      => (example negative temperature value: 0x80DC, high bit indicates negative temperature 0xDC=220 decimal the client '''

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
  data['bat'] = batt
  
  jsondata = json.dumps(data)

  full_topic = MQTT_TOPIC + "/" + data['device']  

  mqtt_client = mqtt.Client()
  mqtt_client.username_pw_set(MQTT_USER, MQTT_PASS)
  mqtt_client.connect(MQTT_HOST, MQTT_PORT)
  mqtt_client.publish(full_topic, jsondata)
