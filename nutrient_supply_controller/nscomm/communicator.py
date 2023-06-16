#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (c) 2021 FarmOS, Inc.
# All right reserved.
#
# Nutrient Supply Communicator
#

import os
import signal
import queue
from multiprocessing import Queue, Process
from collections import deque

from .registermap import RegisterMap, RegisterMapFactory
from .slave import NSSlave
from .log import log
from .code import AlertCode, StatCode

class Actuator:
    def __init__(self, devreg, register):
        self._devreg = devreg
        self._register = register
        self._addr, self._len, self._opid = devreg.getcontroladdress()
        log.info("Initialize act : " + str([self._addr, self._len, self._opid]))
        self._que = deque()
        self._prevopid = 0

    def makerequest(self):
        log.info("Actuator make request : " + str([self._opid, self._register[self._opid], self._prevopid]))
        if self._register[self._opid] != self._prevopid and self._register[self._opid] != 0:
           req = self._devreg.getcontrol(self._register[self._addr:self._addr + self._len])
           log.info("Received a request %s", req)
           if req["operation"] == 0:
               self._que = deque([req])
           else:
               self._que.append(req)
           self._prevopid = req["opid"]
        else:
            log.info ("Fail to make request.")

    def getrequest(self):
        return self._que.popleft()

    def checkrequest(self, idx):
        return self._que[idx]

class RequestManager:
    def __init__(self, defmap):
        self._register = [0] * defmap.getmaxsize()
        self._devmap = {}
        self._devs = []

        nd = defmap.getnode()
        acts = defmap.getactuators()
        for dev in [nd] + acts:
           _, _, opid = dev.getcontroladdress()
           dev = Actuator(dev, self._register)
           self._devs.append(dev)
           self._devmap[opid] = dev

    def update(self, addr, vals):
        for idx, val in enumerate(vals):
            self._register[addr + idx] = val

        if addr > 500:
            log.info("ReqMng received %s, %s", addr-1, vals)
        for opid in self._devmap.keys():
            if addr <= opid < addr + len(vals):
                log.info("ReqMng make request :" + str(opid))
                self._devmap[opid].makerequest()

    def noderequest(self):
        try:
            return self._devs[0].getrequest()
        except:
            return None

    def actrequest(self, idx):
        try:
            return self._devs[idx].getrequest()
        except:
            return None

    def shouldstopact(self, idx):
        try:
            req = self._devs[idx].checkrequest(0)
            if req["operation"] == 0:
                return req["opid"]
            else:
                return 0
        except:
            return 0

class NSCommunicator:
    def __init__(self, option, defmap):
        self._option = option
        self._defmap = defmap
        self._recvque = Queue()
        self._sendque = Queue()
        self._slave = NSSlave(option, self._sendque, self._recvque, defmap.getmaxsize())
        self._proc = Process(target=self._slave.execute)
        self._reqmng = RequestManager(defmap)

    def start(self, thd=True):
        if thd:
            self._slave.execute()
            self._proc = None
        else:
            self._proc.start()
        self._sendque.put(self._defmap.getnodeinfo())
        self._sendque.put(self._defmap.getdevinfo())

    def stop(self):
        if self._proc:
            os.kill(self._proc.pid, signal.SIGTERM)

    def listen(self):
        try:
            while True:
                addr, vals = self._recvque.get(True, 0.1)
                if addr > 500:
                    log.info("Communicator received %s, %s", addr-1, vals)
                self._reqmng.update(addr-1, vals)
        except queue.Empty:
            pass
        except Exception as ex:
            log.warning(str(ex))

    def getnodecontrol(self):
        self.listen()
        return self._reqmng.noderequest()

    def getnutcontrol(self):
        self.listen()
        return self._reqmng.actrequest(1)

    def shouldstop(self):
        self.listen()
        return self._reqmng.shouldstopact(1)

    def _set(self, reg, params):
        self.listen()
        addr, memory = reg.setstatus(params)
        self._sendque.put((addr, memory))

    def setnode(self, params):
        self.listen()
        self._set(self._defmap.getnode(), params)

    def setsensor(self, idx, params):
        self.listen()
        self._set(self._defmap.getsensor(idx), params)

    def setnut(self, params):
        self.listen()
        self._set(self._defmap.getactuator(0), params)

#option = {"method":"rtu", "host":"127.0.0.1", "port":2222}
    
def start_ns_communicator(option, defmap, thd=True):
    communicator = NSCommunicator(option, defmap)
    communicator.start(thd)
    return communicator

def stop_ns_communicator(communicator):
    communicator.stop()

def get_node_control_info(communicator):
    return communicator.getnodecontrol()
    
def get_nutrient_control_info(communicator):
    return communicator.getnutcontrol()
    
def get_default_register_map():
    return RegisterMapFactory.default_nutrient_supply_map()

def update_node_status(communicator, status):
    communicator.setnode(status)
    
def update_sensor_status(communicator, idx, status):
    communicator.setsensor(idx, status)
    
def update_nutrient_status(communicator, status):
    communicator.setnut(status)

def should_stop(communicator):
    return communicator.shouldstop()


if __name__ == "__main__":
    option = {"method":"tcp", "host":"192.168.1.194", "port":2222} 
    map = get_default_register_map()
    
    nscomm = NSCommunicator(option, map)
    nscomm.start(True)
    
    update_nutrient_status(nscomm, {"status" : 402, "area": 1, "alert": 0, "opid":2})
    update_sensor_status(nscomm, 0, {"status" : StatCode.READY.value, "value": 2.3})
    update_sensor_status(nscomm, 1, {"status" : StatCode.NEED_CALIBRATION.value, "value": 2.3})
    update_sensor_status(nscomm, 2, {"status" : StatCode.BUSY.value, "value": 3.5})
    update_node_status(nscomm, {"status" : 0, "opid": 1, "control": 3})
    
