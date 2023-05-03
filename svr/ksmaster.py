#!/usr/bin/env python3
#
# -*- coding: utf-8 -*-
#
# Copyright (c) 2023 tombraid@snu.ac.kr
# All right reserved.
#

import time
import traceback
import json
import datetime
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
from pymodbus.client.sync import ModbusSerialClient
from pymodbus.client.sync import ModbusTcpClient
from pymodbus.exceptions import ConnectionException

from deamon import Runner, Daemon

class Connection:
    def __init__(self, option, logger):
        self._conn = None
        self._option = option
        self._logger = logger

    def connect(self):
        try:
            if self._option['method'] == 'rtu':
                self._conn = ModbusSerialClient(method='rtu', port=self._option['port'],
                        timeout=self._option['timeout'], baudrate=self._option['baudrate'])
                ret = self._conn.connect()
            elif self._option['method'] == 'tcp':
                self._conn = ModbusTcpClient(self._option['host'],
                        port=self._option['port'], timeout=self._option['timeout'])
                ret = self._conn.connect()
            else:
                ret = None
            return ret
        except Exception as ex:
            self._logger.warn("Fail to connect MODBUS [" + str(self._option) + "] : " + str(ex))
            return None

    def close(self):
        self._conn.close()

    def readregister(self, addr, count, unit):
        try:
            return self._conn.read_holding_registers(addr, count, unit=unit)
        except Exception as ex:
            self._logger.warn("fail to read holding registers[" + str(addr) + "] : "+ str(ex))
            return None

    def writeregister(self, addr, content, unit):
        try:
            res = self._conn.write_registers(addr, content, unit=unit)
            if res.isError():
                self._logger.warn("Fail to write register." + str(unit) + ","
                        + str(addr) + ":" + str(res))
                return False
            else:
                return True
        except Exception as ex:
            self._logger.warn("fail to write holding registers[" + str(addr) + "] : " + str(ex))
            return False


class KSMaster(Runner):
    def __init__(self, option, logger):
        self._option = option
        self._logger = logger
        self._client = None
        self._connected = False
        self._modbus = [None, None]
        self._msgq = deque()

    def connect(self):
        try:
            self._client = mqtt.Client()
            self._client.loop(.1)

            self._client.on_message = self.onmsg
            self._client.on_socket_close = self.onclose
            self._client.on_disconnect = self.onclose

            opt = self._option["mqtt"]

            self._client.connect(opt["host"], opt["port"], opt["keepalive"])
            self._client.subscribe("simx/#" , 2)
            self._client.loop_start()
            self._connected = True
        except Exception as ex:
            self._logger.warn("fail to connect mqttserver : " + str(ex))
            self._connected = False
        return self._connected

    def close(self):
        self._client.loop_stop()
        self._connected = False

    def onclose(self, client, udata, sock):
        self._logger.warn("close mqtt connection.")
        self._connected = False

    def process(self):
        while True:
            try:
                topic, msg = self._msgq.popleft()
            except:
                return

            if topic == 'simx/reset':
                self._option["modbus"] = json.loads(msg)
                self._modbus = self.connectmodbus()
            elif topic == 'simx/write':
                self.write(json.loads(msg))
            elif topic == 'simx/read':
                self.read(json.loads(msg))

    def run(self, debug=False):


    def onmsg(self, client, obj, blk):
        self._logger.info("Received '" + str(blk.payload) + "' on topic '"
              + blk.topic + "' with QoS " + str(blk.qos))
        try:
            self._msgq.append((blk.topic, blk.payload))

        except Exception as ex:
            self._logger.warn("fail to call onmsg: " + str(ex) + " "  + blk.payload)
            

    def _connectmodbus(self, idx):
        if self._modbus[idx]:
            self._modbus[idx].close()
        self._modbus[idx] = Connection(self._option["modbus"]["sim" if idx == 0 else "real"], self._logger)
        self._modbus[idx].connect()

    def connectmodbus(self):
        if "sim" in self._option["modbus"]:
            self._connectmodbus(0)
        if "real" in self._option["modbus"]:
            self._connectmodbus(1)

    def write(self, msg):
        ret = [None, None]
        if self._modbus[0]: 
            ret[0] = self._modbus[0].write(msg["addr"], msg["content"], self._option["modbus"]["sim"]["unit"])
        if self._modbus[1]: 
            ret[1] = self._modbus[1].write(msg["addr"], msg["content"], self._option["modbus"]["real"]["unit"])
        msg["ret"] = ret
        self.publish("simx/res", msg)

    def read(self, msg):
        ret = [None, None]
        if self._modbus[0]:
            ret[0] = self._modbus[0].readregister(msg["addr"], msg["count"], self._option["modbus"]["sim"]["unit"])
        if self._modbus[1]:
            ret[1] = self._modbus[1].readregister(msg["addr"], msg["count"], self._option["modbus"]["real"]["unit"])
        msg["ret"] = ret
        self.publish("simx/reg", msg)

    def publish(self, topic, msg):
        try:
            publish.single(topic, payload=json.dumps(msg), qos=2,
                hostname=self._option["mqtt"]["host"],
                port=self._option["mqtt"]["port"])
        except Exception as ex:
            self._logger.warn("publish " + str((topic, msg)) + " exception : " + str(ex))

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage : python ksmaster.py [start|stop|restart|run]")
        sys.exit(2)

    option = {
        "mqtt" : {"host": "127.0.0.1", "port": 1883, "keepalive": 60},
        "modbus": {
            "sim" : {"port": "/dev/ttySIM", "baudrate": 9600, "unit":1},
            "real" : {"port": "/dev/ttyUSB0", "baudrate": 9600, "unit":1}
        }
    }

    master = KSMaster(option)
    daemon = Daemon("ksmaster", master)

    if 'start' == mode:
        daemon.start()
    elif 'stop' == mode:
        daemon.dstop()
    elif 'restart' == mode:
        daemon.restart()
    elif 'run' == mode:
        daemon.run()
    else:
        print("Unknown command")
        sys.exit(2)
    sys.exit(0)


