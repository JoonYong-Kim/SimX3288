#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (c) 2021 FarmOS, Inc.
# All right reserved.
#
# Nutrient Supply Slave
# this module is a modbus slave
#


import time
import queue
from multiprocessing import Queue
from threading import Lock, Thread

from pymodbus.version import version
from pymodbus.server.asynchronous import StartTcpServer, StartSerialServer
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.datastore import ModbusSparseDataBlock, ModbusSequentialDataBlock
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext
from pymodbus.transaction import ModbusRtuFramer, ModbusSocketFramer

from .log import log

class NSCallbackDataBlock(ModbusSequentialDataBlock):
    def __init__(self, queue, size):
        super(NSCallbackDataBlock, self).__init__(0x00, [0]*size)
        self._lock = Lock()
        self._que = queue

    def setValues(self, address, values):
        if address > 500:
            log.info("Receive address, value : %s, %s", address -1, values)
        with self._lock:
            super(NSCallbackDataBlock, self).setValues(address, values)
            if address > 500:
                log.info("Enque : %s, %s", address -1, values)
            self._que.put((address, values))

    def getValues(self, address, count):
        log.debug("Taken data from : %s, %s", address, count)
        with self._lock:
            return super(NSCallbackDataBlock, self).getValues(address, count=count)

class NSSlave:
    def __init__(self, option, recvqueue, sendqueue, size=1000):
        self._option = option
        self._datablock = NSCallbackDataBlock(sendqueue, size)
        self._que = recvqueue
        self._store = ModbusSlaveContext(hr=self._datablock)
        self._context = ModbusServerContext(slaves=self._store, single=True)
        self._identity = self.makeidentity()
        self._slavethd = Thread(group=None, target=self.startserver)
        self._listenerthd = Thread(group=None, target=self.startlistener)

    def makeidentity(self):
        identity = ModbusDeviceIdentification()
        identity.VendorName = 'FarmOS Inc.'
        identity.ProductCode = 'NSComm'
        identity.VendorUrl = 'http://farmos.co.kr'
        identity.ProductName = 'Nutirient Supply Communicator'
        identity.ModelName = 'NSComm'
        identity.MajorMinorRevision = version.short()
        return identity

    def startlistener(self):
        while True:
            try:
                address, values = self._que.get(True, 0.1)
                self._store.setValues(6, address, values)
                log.debug("update store %s %s", address, values)
            except queue.Empty:
                pass
            except Exception as ex:
                log.warning(str(ex))

    def startserver(self):
        if self._option["method"] == "tcp":
            conn = StartTcpServer(self._context, identity=self._identity, address=(self._option["host"], self._option["port"]), framer=ModbusSocketFramer)
        elif self._option["method"] == "rtu":
            conn = StartSerialServer(self._context, port=self._option["port"], baudrate=self._option["baudrate"], timeout=self._option["timeout"], framer=ModbusRtuFramer)
        else:
            log.warn("Not proper method : " + self._option["method"])

    def execute(self):
        log.debug("slave thread")
        self._slavethd.start()
        log.debug("listener thread")
        self._listenerthd.start()


if __name__ == "__main__":
    option = {"method":"tcp", "host":"127.0.0.1", "port":2222}
    rq = Queue()
    wq = Queue()
    slave = NSSlave(option, rq, wq)
    slave.execute()

    wq.put((1, [0, 0, 3, 2, 20, 21, 0, 0]))
    wq.put((101, [12, 12, 12, 16, 16, 16, 7, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 202]))
    wq.put((201, [0, 0, 1]))
    wq.put((204, [13107, 16403, 0]))
    wq.put((207, [13107, 16403, 101]))
    wq.put((401, [402, 3, 3, 222]))

    while True:
        addr, val = rq.get()
        print (addr, val)
