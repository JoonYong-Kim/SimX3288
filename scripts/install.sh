#/bin/bash

apt install -y socat mosquitto mosquitto-clients

echo "# Place your local configuration in /etc/mosquitto/conf.d/
#
# A full description of the configuration file is at
# /usr/share/doc/mosquitto/examples/mosquitto.conf.example

pid_file /run/mosquitto/mosquitto.pid

persistence false
persistence_location /var/lib/mosquitto/

log_dest file /var/log/mosquitto/mosquitto.log

include_dir /etc/mosquitto/conf.d

listener 1883
listener 9001
protocol websockets
allow_anonymous true
" > /etc/mosquitto/mosquitto.conf

service mosquitto restart

cp virtualport.service /lib/systemd/system/
systemctl daemon-reload
service virtualport start
systemctl enable virtualport

cp simweb.service /lib/systemd/system/
systemctl daemon-reload
service simweb start
systemctl enable simweb

cp ksmaster.service /lib/systemd/system/
systemctl daemon-reload
service ksmaster start
systemctl enable ksmaster

cp ns2023.service /lib/systemd/system/
systemctl daemon-reload
service ns2023 start
systemctl enable ns2023

pip3 install paho.mqtt pymodbus twisted pygments prompt_toolkit
