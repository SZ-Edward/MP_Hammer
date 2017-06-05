#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'Aurora Wu (wuxy91@gmail.com)'
__copyright__ = "Copyright (c) 2013- aurorawu.com"

import config
import json
import requests
from flask import Flask, jsonify, request as req
import hashlib

app = Flask(__name__)


@app.route("/")
def index():
    return "This is an index page!"


@app.route("/wx", methods=["GET"])
def validate_wx_dev_config():
    sign = req.args.get('signature')
    timestamp = req.args.get('timestamp')
    nonce = req.args.get('nonce')
    echostr = req.args.get('echostr')
    to_sort_list = [config.wx_my_token, timestamp, nonce]
    sha1 = hashlib.sha1()
    to_sort_list.sort()
    map(sha1.update, to_sort_list)
    hashcode = sha1.hexdigest()
    if sign == hashcode:
        return echostr
    else:
        return ''


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=config.port, debug=config.debug)
