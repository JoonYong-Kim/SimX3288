#!/usr/bin/env python3
#
# -*- coding: utf-8 -*-
#
# Copyright (c) 2023 tombraid@snu.ac.kr
# All right reserved.
#

import sys
import os
import traceback
from http.server import HTTPServer, CGIHTTPRequestHandler
from daemon import Runner, Daemon

class SimServer(Runner):
    def initialize(self):
        os.chdir('../ui')

    def run(self, debug=False):
        server_object = HTTPServer(server_address=('', 80), RequestHandlerClass=CGIHTTPRequestHandler)
        server_object.serve_forever()

    def stop(self):
        pass

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage : python simserver.py [start|stop|restart|run]")
        sys.exit(2)

    mode = sys.argv[1]
    simsvr = SimServer()
    daemon = Daemon("simsvr", simsvr)

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

