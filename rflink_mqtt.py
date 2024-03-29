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

def clear_bit(value, bit_index):
    return value & ~(1 << bit_index)

if (len(sys.argv) != 2):
    print("Wrong number of args, try 'rflink_mqtt <port>'. Port can be like '/dev/ttyUSB0'")
    sys.exit(0)
prt = sys.argv[1]
print("Using port " + prt)

ser = serial.Serial(
 port=prt,
 baudrate = 57600,
 parity=serial.PARITY_NONE,
 stopbits=serial.STOPBITS_ONE,
 bytesize=serial.EIGHTBITS,
 timeout=1
)
mqttdata = {}

while 1:
 try:   
  x=ser.readline()
 except KeyboardInterrupt:
  print ("Exit")
  sys.exit(0)
 except:
  print ("Unexpected error:", sys.exc_info()[0])

 if x[:5] != "20;00" and len(x) >= 20:	# Ignore start message from Rflink
  # Extract data from Rflink and create a Mqtt message
  x=x.rstrip()
  #print("Got data")
  print ("x: " + str(x))
  # Can look like:
  # 20;00;Nodo RadioFrequencyLink - RFLink Gateway V1.1 - R
  # 20;02;Firstline;ID=0085;TEMP=0079;
  # 20;01;DKW2012;  ID=0022;TEMP=00a6;HUM=69;WINSP=0056;WINGS=00ab;RAIN=2871;WINDIR=0004;BAT=OK;
  # 20;05;Alecto V2;ID=0069;TEMP=0113;HUM=36;WINSP=0000;WINGS=0000;RAIN=0000;BAT=OK;
  # 20;57;Xiron;ID=5801;TEMP=800f;HK
  # 0BF;Xiron;ID=5801;TEMP=8022;HUM=84;BAT=OK
  # 20;BE;UPM_Esic;ID=0001;TEMP=00ac;HUM=30;BAT=OK;
  # 20;2D;Digitech;ID=0216;TEMP=00c1;BAT=LOW
  try:
    x = str(x)
    # To test:
    #x="20;05;Alecto V2;ID=0069;TEMP=8032;HUM=36;WINSP=0000;WINGS=0000;RAIN=0000;BAT=OK;"
    #x: b'20;01;Xiron;ID=5801;TEMP=800b;HUM=86;BAT=OK;'
    # -5.0 = 50dec = 0032h. High bit high indicates negative, thus = 8032.  
    #print(x);
    inputdata = x.split(';')
    listLength = len(inputdata)
    #print (listLength)	# UPM = 8 parts. 
    if (listLength>5):
        if(inputdata[1] != "00"):
          mqttdata["NAME"] = inputdata[2]
          
          for item in inputdata:
            entity = item.split("=")
            #print (item + "(len:" + str(len(entity)) + ")")
            if(len(entity)>1):
            
              if(entity[0] == "TEMP"):
              #if(entity[0] != ""):
                #print("TEMP: ")
                #print(entity[1])
                #entity[1] = "8032";  	# = -5.0C
                sign = entity[1][:1]	# Highest bit is set when negative temperature
                
                if (sign == '8'):
                    #print("Negative value")
                    charsign = "-"
                    #print (int(entity[1],16))
                    offset = int("8000", 16)
                    
                    hexsum = int(entity[1],16) - offset
                    #print ("hex")
                    #print (hex(hexsum))
                    dec = int(str(hexsum), 16) / 10
                    #print("dec: ")
                    #print(dec)                   
                    comptemp = charsign + str(dec)
                    mqttdata[entity[0]] = comptemp
                    #print (comptemp)
                else:
                    dec = int(str(entity[1]), 16) / 10
                    mqttdata[entity[0]] = str(dec)
              elif (entity[0] == "ID"):              
                mqttdata["ID"] = entity[1]
              elif (entity[0] == "HUM"):              
                mqttdata["HUM"] = entity[1]
              elif (entity[0] == "BAT"):
                mqttdata["BAT"] = entity[1]  
          jsondata = json.dumps(mqttdata)
          print (jsondata)
          
          print ("Send mqtt")

          try:
            full_topic = MQTT_TOPIC + "/" + mqttdata["NAME"] + "_" + mqttdata["ID"] 
            mqtt_client = mqtt.Client()
            #mqtt_client.username_pw_set(config.MQTT_USER, config.MQTT_PASS)
            mqtt_client.connect(MQTT_HOST, MQTT_PORT)
            mqtt_client.publish(full_topic, jsondata)
          except:
            print ("Unexpected error:", sys.exc_info()[0])
        
  except AttributeError:
    traceback.print_exc()
  
  #print("Done")ssh 
