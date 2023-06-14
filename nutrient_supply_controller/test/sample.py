#!/usr/bin/env python3
#
# -*- coding: utf-8 -*-
#
# Copyright (c) 2021 FarmOS, Inc.
# All right reserved.
#
# User Sample
# 아래의 코드는 적당히 양액기처럼 동작하기 위한 샘플로 실제 구동과는 차이가 있습니다.
#

import time
import nscomm.communicator as nss
from nscomm.log import log

def get_kist_register_map():
    defmap = nss.get_default_register_map()
    defmap.remove_sensor(2)     # not use EC 3 sensor
    defmap.remove_sensor(5)     # not use pH 3 sensor
    defmap.change_nutrient_supply(3)    # use nutrient-supply / level3
    return defmap

option = {"method":"tcp", "host":"192.168.1.76", "port":2222}
defmap = get_kist_register_map()

sencnt = 0
control = 1
opid = 0
supplyingstatus = 0    # 0 ready  401 preparing  402 supplying  403 stopping

communicator = nss.start_ns_communicator(option, defmap)

# 초기화
nss.update_node_status(communicator, {"status" : 0, "opid" : 0, "control" : control})

while True:
    log.info("loop" + str(control) + str(supplyingstatus))
    # 센서 정보 획득

    # 센서 데이터 업데이트
    if sencnt % 60 == 0:
        for idx in range(2):
            nss.update_sensor_status(communicator, idx, {"status":0, "value":2.3})
    sencnt = sencnt + 1

    ctrlinfo = nss.get_node_control_info(communicator)
    if ctrlinfo:
        # 노드 명령 처리
        print ("node control info", ctrlinfo)
        # 노드 상태 업데이트
        control = ctrlinfo["control"]
        nss.update_node_status(communicator, {"status": 0, "opid" : ctrlinfo["opid"], "control": control})
        time.sleep(1)
    
    if nss.should_stop(communicator) > 0:  # 중지명령이 있다면

        ctrlinfo = nss.get_nutrient_control_info(communicator)
        if control == 2 and ctrlinfo:   # 원격제어 상태에서 명령을 받았다면 처리함. 그렇지 않으면 무시함.
            print ("nutrient supply stop control info", ctrlinfo)
            # 양액기 상태 업데이트
            supplyingstatus = 0
            opid = ctrlinfo["opid"]
            nss.update_nutrient_status(communicator, {"status":supplyingstatus, "opid":opid, "area" : 0, "alert" : 0})

    elif supplyingstatus == 0:  # 공급중이 아니라면
        ctrlinfo = nss.get_nutrient_control_info(communicator)
        if control == 2 and ctrlinfo :  # 원격제어 상태에서 명령을 받았다면 처리함.
            supplyingstatus = 401
            print ("nutrient supply control info", ctrlinfo)
            # 양액기 상태 업데이트 - 실제로 이렇게 구현하면 안됨.
            nss.update_nutrient_status(communicator, {"status":supplyingstatus, "opid":opid, "area" : 0, "alert" : 0})
            time.sleep(3)

    else:   
        # 중지명령도 없고, 양액기가 동작중이라면, 할일을 계속함.
        print("nutrient supply is working")
        if supplyingstatus == 401:
            supplyingstatus = 402
            nss.update_nutrient_status(communicator, {"status":supplyingstatus, "opid":opid, "area" : 1, "alert" : 0})
            time.sleep(5)

        elif supplyingstatus == 402:
            supplyingstatus = 403
            nss.update_nutrient_status(communicator, {"status":supplyingstatus, "opid":opid, "area" : 0, "alert" : 0})
            time.sleep(3)

        elif supplyingstatus == 403:
            supplyingstatus = 0
            nss.update_nutrient_status(communicator, {"status":supplyingstatus, "opid":opid, "area" : 0, "alert" : 0})
    
    time.sleep(1)

nss.stop_ns_communicator(communicator)
