#!/usr/bin/env python3
#
# -*- coding: utf-8 -*-
#
# Copyright (c) 2023 FarmOS, Inc.
# All right reserved.
#
#

import json
import random
import time
from datetime import datetime
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish

import nscomm.communicator as nss
from nscomm.log import log

from daemon import Daemon, Runner

# option = {"method":"rtu", "port":"/dev/ttyNSCOMM", "baudrate": 9600}

class MQTTLogger:
    def info(self, msg):
        publish.single("ns2023/log", payload=msg, qos=2, hostname="127.0.0.1")

class NutSim:
    def __init__(self, mqttlog):
        self._nd = {"status" : 0, "opid" : 0, "control" : 1}
        self._nut = {"status" : 0, "opid" : 0, "area": 0, "alert": 0, "remain-time": 0}
        self._cmd = {"opid": 0, "operation" : 0, "start-area": 0, "stop-area": 0, "on-sec": 0, "EC": 0, "pH": 0}

        self._maxarea = 5

        self._pec = 0.5
        self._pph = 7.0
        self._rad = 0
        self._flow = [0] * (self._maxarea + 1)

        self._nsec = self.getnsec()
        self._mqlog = mqttlog
        self.loadstatus()

    def savestatus(self):
        try:
            fp = open("conf/nut.stat", "w")
            status = {"time": str(datetime.now().date()), "nd" : self._nd, "nut" : self._nut, "sen" : [self._pec, self._pph, self._flow]}
            fp.write(json.dumps(status))
            fp.close()
        except:
            self._mqlog.info ("Fail to save status")

    def loadstatus(self):
        try:
            fp = open("conf/nut.stat", "r")
            status = json.loads(fp.read())
            fp.close()
        except:
            return

        if str(datetime.now().date()) == status["time"]:
            self._nd = status["nd"]
            self._nut = status["nut"]
            self._pec = status["sen"][0]
            self._pph = status["sen"][1]
            self._flow = status["sen"][2]
            self._mqlog.info ("Status reloaded!!")
        else:
            self._mqlog.info ("Old Status was not reloaded!!")


    def getstatus(self):
        return [self._nd, self._nut, self._pec, self._pph, self._rad, self._flow]

    def setcontrol(self, cmd):
        self._mqlog.info ("Changing the control : " + str(cmd))
        if cmd["operation"] != 2:
            self._mqlog.info ("Operation [" + str(cmd["operation"]) + "] is not valid")
            return False

        if cmd["opid"] == self._nd["opid"]:
            self._mqlog.info("OPID is not changed")
            return False

        if cmd["control"] not in (1, 2):
            self._mqlog.info ("Control [" + str(cmd["control"]) + "] is not valid")
            return False

        self._nd["opid"] = cmd["opid"]
        self._nd["control"] = cmd["control"]
        self._mqlog.info ("Changed the control : " + str(self._nd))
        return True

    def setcommand(self, cmd):
        self._mqlog.info ("Received a Command: " + str(cmd))
        if self._nd["control"] != 2:
            self._mqlog.info ("Control of node is not remote." + str(self._nd["control"]))
            return False

        if cmd["operation"] not in (401, 0, 402, 403):
            self._mqlog.info ("Operation [" + str(cmd["operation"]) + "] is not valid")
            return False

        if cmd["opid"] == self._cmd["opid"]:
            self._mqlog.info("OPID is not changed" + str(cmd["opid"]))
            return False

        if cmd["operation"] in (402, 403):
            if cmd["start-area"] > cmd["stop-area"]:
                self._mqlog.info("start-area should be smaller than stop-area.")
                return False
            if cmd["stop-area"] > self._maxarea:
                self._mqlog.info("This simulator has " + str(self._maxarea) + " area. stop-area should be smaller than " + str(self._maxarea + 1) +".")
                return False
            if cmd["start-area"] < 1:
                self._mqlog.info("start-area should be bigger than 0.")
                return False
            if cmd["on-sec"] < 1:
                self._mqlog.info("on-sec should be bigger than 0.")
                return False

        if cmd["operation"] == 403: 
            if cmd["EC"] < 0 or cmd["EC"] > 5:
                self._mqlog.info("EC range is not proper.")
                return False
            if cmd["pH"] < 0 or cmd["pH"] > 14:
                self._mqlog.info("pH range is not proper.")
                return False

        self._cmd = cmd
        if cmd["operation"] == 401:
            # set 1회 관수
            self._cmd["EC"] = 2.3
            self._cmd["pH"] = 6.0
            self._cmd["start-area"] = 1
            self._cmd["stop-area"] = self._maxarea
            self._cmd["on-sec"] = 30

        elif cmd["operation"] == 402:
            self._cmd["EC"] = 0.5
            self._cmd["pH"] = 7.0

        if self._cmd["operation"] == 0:
            # 정지라면 상태도 바로 중지
            self._nut = {"status" : 0, "opid" : cmd["opid"], "area": 0, "alert": 0, "remain-time": 0}
        else:
            self._nut = {"status" : 401, "opid" : cmd["opid"], "area": 0, "alert": 0, "remain-time": 0}

        self._mqlog.info ("Excuting the command : " + str(self._cmd) + " " + str(self._nut))
        return True

    def getnsec(self):
        now = datetime.now()
        return (now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()

    def updatesensors(self, gap, nsec):
        # update EC
        if self._cmd["operation"] in (401, 402, 403):
            self._pec = self._pec + (self._cmd["EC"] - self._pec) * 0.6
            self._pph = self._pph + (self._cmd["pH"] - self._pph) * 0.6

        # rad
        if 21600 < nsec < 64800: 
            self._rad = (nsec - 21600) / 21600 * 1200
        else:
            self._rad = 0

        #self._mqlog.info ("Updating Sensors : " + str([self._pec, self._pph, self._rad]))

    def updatenut(self, gap, nsec):
        smargin = 0.1
        if self._cmd["operation"] in (401, 402, 403):
            if self._nut["status"] == 401:  
                # not started
                if self._cmd["EC"] - smargin <= self._pec <= self._cmd["EC"] + smargin and self._cmd["pH"] - smargin <= self._pph <= self._cmd["pH"] + smargin:
                    # start
                    self._nut["status"] = 402
                    self._nut["area"] = self._cmd["start-area"]
                    self._nut["remain-time"] = self._cmd["on-sec"]
                else:
                    # waiting for a while
                    pass
            elif self._nut["status"] == 402:
                self._nut["remain-time"] = self._nut["remain-time"] - gap
                tmp = int(gap * 10)        # 초당 10L
                self._flow[0] = self._flow[0] + tmp
                self._flow[self._nut["area"]] = self._flow[self._nut["area"]] + tmp

                if self._nut["remain-time"] <= 0:
                    if self._nut["area"] == self._cmd["stop-area"]:
                        self._nut["status"] = 403
                        self._nut["remain-time"] = 0
                        self._mqlog.info ("Finishing the command : " + str(self._cmd) + " " + str(self._nut))
                    else:
                        self._nut["area"] = self._nut["area"] + 1
                        self._nut["remain-time"] = self._cmd["on-sec"]
                        self._mqlog.info ("Next area : " + str(self._cmd) + " " + str(self._nut))

            elif self._nut["status"] == 403:
                self._nut["status"] = 0
                self._nut["area"] = 0
                self._mqlog.info ("Finished the command : " + str(self._cmd) + " " + str(self._nut))

        else: # self._cmd["operation"] == 0
            self._nut["status"] = 0
            self._nut["area"] = 0

        #self._mqlog.info ("Updating : " + str(self._nut))

    def execute(self):
        nsec = self.getnsec()
        gap = nsec - self._nsec
        if gap < 0: # reset - 1 day passed
            self._mqlog.info ("One day passed.")
            self._flow = [0] * (self._maxarea + 1)

        if gap < 1: #skip
            return False

        self.updatesensors(gap, nsec)
        self.updatenut(gap, nsec)

        self._nsec = nsec
        self.savestatus()
        return True

    def getregmap(self):
        defmap = nss.get_default_register_map()
        defmap.remove_sensor(2)     # not use EC 3 sensor
        defmap.remove_sensor(5)     # not use pH 3 sensor
        for idx in range(8 + self._maxarea, 20):
            defmap.remove_sensor(idx)   # 5구역 까지만 있는 양액기
        defmap.change_nutrient_supply(3)    # use nutrient-supply / level3
        return defmap

    def getobservations(self):
        obs = [self._pec + random.randrange(-10, 10) / 100, self._pec + random.randrange(-10, 10) / 100, 0,
                self._pph + random.randrange(-10, 10) / 100, self._pph + random.randrange(-10, 10) / 100, 0, 
                self._rad + random.randrange(0, 100) / 10]
        obs.extend (self._flow)
        return obs

    def getnd(self):
        return self._nd

    def getnut(self):
        self._nut["remain-time"] = int(self._nut["remain-time"])
        return self._nut

class NS2023(Runner):
    def __init__(self, conf, mode):
        fp = open(conf, 'r')
        self._option = json.loads(fp.read())
        fp.close()

        self._mode = mode
        self._mqlog = MQTTLogger()
        self._sim = NutSim(self._mqlog)
        self._comm = nss.start_ns_communicator(self._option[mode], self._sim.getregmap(), True)
        self._isrunning = False

    def getdname(self):
        return "ns2023-" + self._mode

    def stop(self):
        self._logger.info("Try to stop")
        self._isrunning = False

    def finalize(self):
        nss.stop_ns_communicator(self._comm)

    def update(self):
        for idx, obs in enumerate(self._sim.getobservations()):
            nss.update_sensor_status(self._comm, idx, {"status":0, "value":obs})

        nss.update_node_status(self._comm, self._sim.getnd())
        nss.update_nutrient_status(self._comm, self._sim.getnut())

    def run(self, debug = False):
        n = 0
        self._isrunning = True

        while self._isrunning:
            ndcmd = nss.get_node_control_info(self._comm)
            if ndcmd:
                self._logger.info("Get Node Command : " + str(ndcmd))
                self._sim.setcontrol(ndcmd)

            nutcmd = nss.get_nutrient_control_info(self._comm)
            if nutcmd:
                self._logger.info("Get NS Command : " + str(nutcmd))
                self._sim.setcommand(nutcmd)

            if self._sim.execute():
                n = n + 1
                if n % 10 == 0:
                    self._logger.info("Update register~" + str(self._sim.getstatus()))
                self.update()

            time.sleep(0.1)

if __name__ == '__main__':
    import sys

    if len(sys.argv) != 2:
        print("Usage : python ns2023.py [start|stop|run|debug]")
        sys.exit(2)

    fp = open("../../mode/ui.mode", "r")
    mode = int(fp.readline())
    fp.close()
    if mode in (1, 3):
        runtype = "sim"
    elif mode == 2:
        sys.exit(0)
    else:
        runtype = "real"

    runner = NS2023('conf/ns2023.json', runtype)
    adaemon = Daemon(runner.getdname(), runner)
    if 'start' == runtype:
        adaemon.start()
    elif 'stop' == runtype:
        adaemon.dstop()
    elif 'run' == runtype:
        adaemon.run()
    elif 'debug' == runtype:
        adaemon.run(True)
    else:
        print("Unknown command")
        sys.exit(2)
    sys.exit(0)

