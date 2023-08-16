# Rflink_mqtt
This code reads weather data from a Rflink (http://www.rflink.nl) and sends out data via Mqtt. Includes a control script for Systemd.
Can also be started with pm2

Install - npm install pm2@latest -g
Start this script - pm2 start rflink_mqtt.py
Save status for autostart - pm2 save
