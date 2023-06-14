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
from flask import Flask, request, json, render_template

app = Flask(__name__, static_url_path='', static_folder='../ui/')

@app.route("/mode", methods=['GET'])
def getmode():
    fp = open("../mode/real.mode", "r")
    mode = fp.readline()
    fp.close()

    fp = open("../mode/ui.mode", "r")
    mode = fp.readline()
    fp.close()

    return json.dumps({"real": mode.strip(), "ui": mode.strip()})

@app.route("/modechange", methods=['POST'])
def modechange():
    print (request.method, request.form.get('mode'))
    if 0 < int(request.form.get('mode')) < 5:
        fp = open("../mode/ui.mode", "w")
        fp.write(request.form.get('mode'))
        fp.close()

        response = {
            "status": "success"
        }
    else:
        response = {
            "status": "failure"
        }

    return json.dumps(response)

@app.route("/")
def index():
    return app.send_static_file('index.html')

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=80)
