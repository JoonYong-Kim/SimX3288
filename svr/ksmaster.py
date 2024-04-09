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
from collections import deque

from pymodbus.client.sync import ModbusSerialClient
from pymodbus.client.sync import ModbusTcpClient
from pymodbus.exceptions import ConnectionException

from daemon import Runner, Daemon

class Connection:
    def __init__(self, option, logger):
        self._conn = None
        self._option = option
        self._logger = logger
        self._isconnected = False

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

            self._isconnected = ret
            return ret
        except Exception as ex:
            self._logger.warning("Fail to connect MODBUS [" + str(self._option) + "] : " + str(ex))
            self._isconnected = False
            return None

    def close(self):
        self._isconnected = False
        self._conn.close()

    def readregister(self, addr, count, unit):
        try:
            res = self._conn.read_holding_registers(addr, count, unit=unit)
            if res is None or res.isError():
                self._logger.warning ("Fail to read register : " + str(res))
                return None
            if len(res.registers) != count:
                self._logger.warning("Count is not matched : " + str(res.registers))
            return res.registers

        except Exception as ex:
            self._logger.warning("fail to read holding registers[" + str(addr) + "] : "+ str(ex))
            self._isconnected = False
            return None

    def writeregister(self, addr, content, unit):
        try:
            res = self._conn.write_registers(addr, content, unit=unit)
            if res.isError():
                self._logger.warning("Fail to write register." + str(unit) + "," + str(addr) + ":" + str(res))
                return False
            else:
                return True
        except Exception as ex:
            self._logger.warning("fail to write holding registers[" + str(addr) + "] : " + str(ex))
            self._isconnected = False
            return False

    def isconnected(self):
        return self._isconnected

    def check(self):
        if self._isconnected is True:
            return True
        else:
            self._logger.info("disconnected?? try to connect~"  + self._option["port"])
            return self.connect()

class KSMaster(Runner):
    def __init__(self, option, mode):
        self._option = option
        self._mode = mode       # 1 : sim, 2 : real, 3: sim & real
        self._client = None
        self._connected = False
        self._modbus = [None, None]
        self._msgq = deque(maxlen=7)
        self._isrunning = False
        self._keywords = ["sim", "real"]

    def connect(self):
        try:
            try:
                self._client = mqtt.Client()
            except:
                self._client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)

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
            self._logger.warning("fail to connect mqttserver : " + str(ex))
            self._connected = False
        return self._connected

    def resetmsgq(self):
        self._msgq = deque(maxlen=7)

    def close(self):
        self._client.loop_stop()
        self._connected = False
        if self._modbus[0]:
            self._modbus[0].close()
        if self._modbus[1]:
            self._modbus[1].close()
        self._modbus = [None, None]

    def onclose(self, client, udata, sock):
        self._logger.warning("close mqtt connection.")
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
                self._logger.info("write " + str(msg) + "' on topic '" + topic)
                self.write(json.loads(msg))
            elif topic == 'simx/read':
                self._logger.info("read " + str(msg) + "' on topic '" + topic)
                self.read(json.loads(msg))
            else:
                self._logger.info(str(msg) + "' on topic '" + topic)

    def onmsg(self, client, obj, blk):
        #self._logger.info("Received '" + str(blk.payload) + "' on topic '" + blk.topic + "' with QoS " + str(blk.qos))
        try:
            self._msgq.append((blk.topic, blk.payload))

        except Exception as ex:
            self._logger.warning("fail to call onmsg: " + str(ex) + " "  + blk.payload)
            
    def _connectmodbus(self, idx):
        if self._modbus[idx]:
            self._modbus[idx].close()
        self._modbus[idx] = Connection(self._option["modbus"]["sim" if idx == 0 else "real"], self._logger)
        self._modbus[idx].connect()

    def connectmodbus(self):
        if self._mode == 1:
            self._connectmodbus(0)  # sim
            if self._modbus[1]:
                self._modbus[1].close()
        elif self._mode == 2:
            if self._modbus[0]:
                self._modbus[0].close()
            self._connectmodbus(1)  # real
        elif self._mode == 3:
            self._connectmodbus(0)  # sim
            self._connectmodbus(1)  # real

    def write(self, msg):
        ret = [None, None]
        time.sleep(0.1)
        if self._modbus[0]: 
            # 시뮬레이터의 unit 은 항상 1
            ret[0] = self._modbus[0].writeregister(msg["addr"], msg["content"], 1)
            if ret[0] is False:
                self._modbus[0].check()
                self.resetmsgq()

        if self._modbus[1]: 
            ret[1] = self._modbus[1].writeregister(msg["addr"], msg["content"], msg["unit"])
            if ret[1] is False:
                self._modbus[1].check()
                self.resetmsgq()

        msg["ret"] = ret
        self.publish("simx/res", msg)

    def read(self, msg):
        ret = [None, None]
        time.sleep(0.1)
        if self._modbus[0]: 
            # 시뮬레이터의 unit 은 항상 1
            ret[0] = self._modbus[0].readregister(msg["addr"], msg["count"], 1)
            if ret[0] is None:
                self._modbus[0].check()
                self.resetmsgq()

        if self._modbus[1]: 
            ret[1] = self._modbus[1].readregister(msg["addr"], msg["count"], msg["unit"])
            if ret[1] is None:
                self._modbus[1].check()
                self.resetmsgq()

        msg["ret"] = ret
        self.publish("simx/reg", msg)

    def publish(self, topic, msg):
        try:
            publish.single(topic, payload=json.dumps(msg), qos=2,
                hostname=self._option["mqtt"]["host"],
                port=self._option["mqtt"]["port"])
        except Exception as ex:
            self._logger.warning("publish " + str((topic, msg)) + " exception : " + str(ex))

    def stop(self):
        self._isrunning = False

    def initialize(self):
        self.connect()
        self.connectmodbus()

    def run(self, debug=False):
        self._isrunning = not debug 

        n = 0
        while self._isrunning:
            if n % 50:
                if self.checkmode() is True:
                    self.finalize()
                    self.initialize()
                n = 0

            self.process()
            time.sleep(0.1)
            n = n + 1

    def finalize(self):
        self.close()

    def checkmode(self):
        try:
            fp = open("../mode/ui.mode", "r")
            mode = int(fp.readline())
            fp.close()
            if mode != self._mode:
                self._logger.info("Running mode was changed : " + str(mode))
                self._mode = mode
                return True
        except Exception as ex:
            self._logger.warning("check mode exception : " + str(ex))
        return False

if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage : python3 ksmaster.py [start|stop|restart|run]")
        sys.exit(2)

    option = {
        "mqtt" : {"host": "127.0.0.1", "port": 1883, "keepalive": 60},
        "modbus": {
            "sim" : {"method": "rtu", "port": "/dev/ttySim1", "baudrate": 9600, "timeout":3},
            "real" : {"method": "rtu", "port": "/dev/ttyUSB0", "baudrate": 9600, "timeout":3}
        }
    }

    runtype = sys.argv[1]
    master = KSMaster(option, 1)
    daemon = Daemon("ksmaster", master, runtype)

    if 'start' == runtype:
        daemon.start()
    elif 'stop' == runtype:
        daemon.dstop()
    elif 'restart' == runtype:
        daemon.restart()
    elif 'run' == runtype:
        daemon.run()
    else:
        print("Unknown command")
        sys.exit(2)
    sys.exit(0)


