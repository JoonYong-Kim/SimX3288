#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (c) 2021 FarmOS, Inc.
# All right reserved.
#
# Nutrient Supply Logger
#

import logging

FORMAT = ('%(asctime)-15s'
          ' %(levelname)-8s %(module)-15s:%(lineno)-8s %(message)s')
logging.basicConfig(format=FORMAT)
log = logging.getLogger()
log.setLevel(logging.INFO)
