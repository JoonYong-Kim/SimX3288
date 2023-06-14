#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (c) 2021 FarmOS, Inc.
# All right reserved.
#
# Code Table
#

from enum import Enum

class ProductType(Enum):
    COMPLEX = 3

class Product(Enum):
    LV0 = 1
    LV1 = 2
    LV2 = 3
    LV3 = 4

class StatCode(Enum):
    READY = 0
    ERROR = 1
    BUSY = 2
    VOLTAGE_ERROR = 3
    CURRENT_ERROR = 4
    TEMPERATURE_ERROR = 5
    FUSE_ERROR = 6

    NEED_REPLACE = 101
    NEED_CALIBRATION = 102
    NEED_CHECK = 103
    
    PREPARING = 401
    SUPPLYING = 402
    STOPPING = 403

class ControlCode(Enum):
    LOCAL_CONTROL = 1
    REMOTE_CONTROL = 2
    MANUAL_CONTROL = 3
    
class OperationCode(Enum):
    CONTROL = 2
    ON = 401
    AREA_ON = 402
    PARAM_ON = 403

class NutrientSupplyLevel(Enum):
    LV0 = 201
    LV1 = 202
    LV2 = 203
    LV3 = 204
    
class AlertCode(Enum):
    NORMAL = 0
    HIGH_CONCENTRATION_EC=1
    LOW_CONCENTRATION_EC=2
    HIGH_CONCENTRATION_pH=3
    LOW_CONCENTRATION_pH=4
    LOW_FLOW_ALARM=5
    HIGH_TEMPERATURE_ALARM=6
    LOW_TEMPERATURE_ALARM=7
    ABNORMAL=8
    LOW_LEVEL = 9
    OVERLOAD = 10
    
