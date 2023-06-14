#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (c) 2021 FarmOS, Inc.
# All right reserved.
#
# Register Map
#

import struct

class Parcel:
    KEYWORDS_FLOAT = ["value", "EC", "pH", "vfloat"]
    KEYWORDS_INT = ["state-hold-time", "remain-time", "hold-time", "on-sec", "time", "vint", "epoch"]

    def __init__(self, addr, codes):
        self._addr = addr
        self._codes = codes
        self._length = 0
        self._opid = None
        for code in codes:
            if code in Parcel.KEYWORDS_FLOAT or code in Parcel.KEYWORDS_INT:
                self._length = self._length + 2
            else:
                if code == "opid":
                    self._opid = self._addr + self._length 
                self._length = self._length + 1

    def toregister(self, dictarg):
        reg = []
        for key in self._codes:
            val = dictarg[key]
            if key in Parcel.KEYWORDS_FLOAT:
                reg.extend(struct.unpack('HH', struct.pack('f', val)))
            elif key in Parcel.KEYWORDS_INT:
                reg.extend(struct.unpack('HH', struct.pack('i', val)))
            else:
                reg.append(val)
        return (self._addr, reg)

    def getaddress(self):
        return (self._addr, self._length, self._opid)

    def fromregister(self, reg):
        idx = 0
        dictret = {}
        for key in self._codes:
            if key in Parcel.KEYWORDS_FLOAT:
                val = struct.unpack('f', struct.pack('HH', reg[idx], reg[idx+1]))[0]
                idx = idx + 2
            elif key in Parcel.KEYWORDS_INT:
                val = struct.unpack('i', struct.pack('HH', reg[idx], reg[idx+1]))[0]
                idx = idx + 2
            else:
                val = reg[idx]
                idx = idx + 1
            dictret[key] = val
        return dictret

class DeviceRegister:
    def __init__(self, stataddr, statcodes, ctrladdr = None, ctrlcodes = None):
        self._statpacel = Parcel(stataddr, statcodes)
        if ctrladdr is None:
            self._ctrlpacel = None
        else:
            self._ctrlpacel = Parcel(ctrladdr, ctrlcodes)
        self._used = True

    def notuse(self):
        self._used = False

    def isusable(self):
        return self._used

    def setstatus(self, dictarg):
        return self._statpacel.toregister(dictarg)

    def getstatusaddress(self):
        return self._statpacel.getaddress()

    def getstatus(self, reg):
        return self._statpacel.fromregister(reg)

    def setcontrol(self, dictarg):
        if self._ctrlpacel:
            return self._ctrlpacel.toregister(dictarg)
        return (None, None)

    def getcontroladdress(self):
        if self._ctrlpacel:
            return self._ctrlpacel.getaddress()
        return (None, None, None)

    def getcontrol(self, reg):
        if self._ctrlpacel:
            return self._ctrlpacel.fromregister(reg)
        return None

class RegisterMap:
    def __init__(self, nodeinfo, devinfo, node, sensors, actuators):
        self._nodeinfo = nodeinfo
        self._devinfo = devinfo
        self._node = node
        self._sensors = sensors
        self._actuators = actuators

    def getnodeinfo(self):
        return (1, self._nodeinfo)

    def getdevinfo(self):
        return (101, self._devinfo)

    def getnode(self):
        return self._node
    
    def getsensor(self, idx):
        return self._sensors[idx]

    def getactuator(self, idx):
        return self._actuators[idx]

    def getactuators(self):
        return self._actuators

    def getmaxsize(self):
        act = self._actuators[-1]
        addr, length, opid = act.getcontroladdress()
        return addr + length + 1

class DefaultNutrientRegisterMap(RegisterMap):
    def remove_sensor(self, idx):
        self._sensors[idx].notuse()
        self._devinfo[idx] = 0

    def change_nutrient_supply(self, level):
        self._nodeinfo[3] = level + 1
        self._devinfo[-1] = level + 201

class RegisterMapFactory:
    @staticmethod
    def default_nutrient_supply_map():
        nodeinfo = [0, 0, 3, 2, 20, 21, 0, 0]
        devinfo = [12, 12, 12, 16, 16, 16, 7, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 202]
        node = DeviceRegister(201, ["status", "opid", "control"], 501, ["operation", "opid", "control"])
        sensors = [
            DeviceRegister(204, ["value", "status"]),
            DeviceRegister(207, ["value", "status"]),
            DeviceRegister(210, ["value", "status"]),
            DeviceRegister(213, ["value", "status"]),
            DeviceRegister(216, ["value", "status"]),
            DeviceRegister(219, ["value", "status"]),
            DeviceRegister(222, ["value", "status"]),
            DeviceRegister(225, ["value", "status"]),
            DeviceRegister(228, ["value", "status"]),
            DeviceRegister(231, ["value", "status"]),
            DeviceRegister(234, ["value", "status"]),
            DeviceRegister(237, ["value", "status"]),
            DeviceRegister(240, ["value", "status"]),
            DeviceRegister(243, ["value", "status"]),
            DeviceRegister(246, ["value", "status"]),
            DeviceRegister(249, ["value", "status"]),
            DeviceRegister(252, ["value", "status"]),
            DeviceRegister(255, ["value", "status"]),
            DeviceRegister(258, ["value", "status"]),
            DeviceRegister(261, ["value", "status"])
        ]
        actuators = [DeviceRegister(401, ["status", "area", "alert", "opid", "remain-time"], 504, ["operation", "opid","start-area", "stop-area", "on-sec", "EC", "pH"])]

        return DefaultNutrientRegisterMap(nodeinfo, devinfo, node, sensors, actuators)
    
if __name__ == "__main__":
    # user
    defmap = RegisterMapFactory.default_nutrient_supply_map()
    defmap.remove_sensor(2)
    defmap.change_nutrient_supply(2)


    # inside library
    # writing sensor info : update_sensor_status (communicator, 0, {"status" : 0, "value": 2.3})
    print('when a user called a function : update_sensor_status (communicator, 0, {"status" : 0, "value": 2.3})')
    sensor = defmap.getsensor(0)
    addr, memory = sensor.setstatus({"status" : 0, "value" : 2.3})

    print ("write data to store from", addr, "content", memory)

    # read node control : get_node_control_info(communicator)
    node = defmap.getnode()
    addr, length, opid = node.getcontroladdress()

    print ()
    print ("read data from store at", addr, "until", length)

    print ("if reading data is", [2, 123, 2])
    ret = node.getcontrol([2, 123, 2])
    print ("it could change.", ret)
