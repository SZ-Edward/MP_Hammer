#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'Aurora Wu (wuxy91@gmail.com)'
__copyright__ = "Copyright (c) 2013- aurorawu.com"

import config
import json
import requests
from flask import Flask, jsonify, request as req
import hashlib
import tools
import message_templates as msgt

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


@app.route("/wx", methods=["POST"])
def receive_wx_posted_xml():
    sign = req.args.get('signature')
    timestamp = req.args.get('timestamp')
    nonce = req.args.get('nonce')
    openid = req.args.get('openid')
    encrypt_type = req.args.get('encrypt_type')
    msg_signature = req.args.get('msg_signature')
    xml = req.get_data()
    print xml
    if encrypt_type == 'aes':
        xml = tools.decrypt_wx_xml_data(xml, msg_signature, timestamp, nonce)
    #return 'success'
    msg_model, reply = tools.parse_xml(xml), ''
    if not msg_model:
        print 'Something goes wrong'
        return ''
    if msg_model.msg_type in ['text', 'image', 'voice', 'link', 'video', 'shortvideo', 'location']:
        if msg_model.msg_type == 'text' and msg_model.content and config.auto_reply:
            print msg_model.content
            if "读诗" in msg_model.content:
                import random
                idx = random.randint(0, len(msgt.poems))
                reply = msgt.poems[idx]
                reply = reply.encode('utf-8')
            elif "股 " in msg_model.content:
                stock, stock_name = msg_model.content.split(' ', 1)
                if stock not in ['A股', '美股', '港股']:
                    reply = "当前系统仅支持查询A股、美股和港股的信息，请确认您的输入是否符合查询规则"
                else:
                    market_code = ''
                    if stock == 'A股':
                        market_code = 'A'
                    elif stock == '美股':
                        market_code = 'M'
                    elif stock == '港股':
                        market_code = 'G'
                    res, total = tools.find_brief_info_by_stock_name_or_stock_code(stock_name, market_code)
                    if res:
                        reply = '股票名称 股票代码 昨日收盘价 今日开盘价 当前价格 最高价 最低价 过去52周最高价 过去52周最低价 数据更新时间\n'
                        for each in res:
                            item = '%s %s %s %s %s %s %s %s %s %s' % (each['stock_name'].encode('utf-8'), each['stock_code'].encode('utf-8'), each['yesterday_close_price'].encode('utf-8'), each['today_open_price'].encode('utf-8'), each['current_price'].encode('utf-8'), each['highest_price_in_today'].encode('utf-8'), each['lowest_price_in_today'].encode('utf-8'), each['highest_price_in_52_weeks'].encode('utf-8') if each['highest_price_in_52_weeks'] else '无', each['lowest_price_in_52_weeks'].encode('utf-8') if  each['lowest_price_in_52_weeks'] else '无', each['real_time'].encode('utf-8'))
                            reply += item + '\n\n'
                        reply += '\n提示：符合查询的股票共有%d支，仅显示前五条的数据' % total
                    else:
                        reply = "抱歉，没有查到对应的股票"
            else:
                reply = msgt.no_keyword_text_message
        else:
            reply = "暂不支持此类消息"
    elif msg_model.msg_type == "event" and msg_model.event in ['subscribe', 'unsubscribe', 'scan', 'location', 'click', 'view']:
        if msg_model.followed:
            reply = msgt.welcome_text_message 
    else:
        reply = "your message type is not supported now!"
    print reply
    ret_xml = tools.msg_model2reply(msg_model, reply)
    # ret_xml = tools.model2xml(msg_model)
    # print ret_xml
    if encrypt_type == 'aes':
        tools.encrypt_wx_xml_data(ret_xml, nonce)
    return ret_xml


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=config.port, debug=config.debug)
