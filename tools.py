#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'Aurora Wu (wuxy91@gmail.com)'
__copyright__ = "Copyright (c) 2013- aurorawu.com"


import xml.etree.ElementTree as ET
import config
from WXBizMsgCrypt import WXBizMsgCrypt
import models
import requests
from bs4 import BeautifulSoup


def encrypt_wx_xml_data(xml, nonce):
    crypt_obj = WXBizMsgCrypt(config.wx_my_token, config.wx_encoding_AES_key, config.wx_app_id)
    ret, encrypted_xml = crypt_obj.EncryptMsg(xml, nonce)
    return encrypted_xml


def decrypt_wx_xml_data(xml, sign, timestamp, nonce):
    crypt_obj = WXBizMsgCrypt(config.wx_my_token, config.wx_encoding_AES_key, config.wx_app_id)
    ret, decrypted_xml = crypt_obj.DecryptMsg(xml, sign, timestamp, nonce)
    return decrypted_xml


def model2xml(model_obj):
    model_dict = model_obj.__dict__
    xml_string = "\n"
    for key, value in model_dict.items():
        if not isinstance(key, str):
            continue
        ks = key.split('_')
        new_key = "".join([each.capitalize() for each in ks])
        key_string = "<%s>%s</%s>\n" % (new_key, value, new_key)
        xml_string += key_string
    return """<xml>%s</xml>""" % xml_string


def msg_model2reply(from_model, reply_content):
    import time
    return """<xml>
<ToUserName><![CDATA[%s]]></ToUserName>
<MsgType><![CDATA[text]]></MsgType>
<FromUserName><![CDATA[%s]]></FromUserName>
<Content><![CDATA[%s]]></Content>
<CreateTime><![CDATA[%s]]></CreateTime>
</xml>""" % (from_model.from_user_name, from_model.to_user_name, reply_content, str(time.time()).replace('.', ''))


def parse_xml(xml):
    if len(xml) == 0:
        return None
    xml_data = ET.fromstring(xml)
    msg_type, event_type = xml_data.find('MsgType').text.lower(), 'event'
    if xml_data.find('Event') is not None:
        event_type = xml_data.find('Event').text.lower()
    if msg_type in ['text', 'image', 'voice', 'link', 'video', 'shortvideo', 'location']:
        return parse_message_xml(msg_type, xml_data)
    elif msg_type == 'event' and event_type in ['subscribe', 'unsubscribe', 'scan', 'location', 'click', 'view']:
        return parse_event_xml(event_type, xml_data)
    else:
        pass


def parse_message_xml(msg_type, xml_data):
    if msg_type == 'text':
        return models.TextMsg(xml_data)
    elif msg_type == 'image':
        return models.ImageMsg(xml_data)
    elif msg_type == 'voice':
        return models.VoiceMsg(xml_data)
    elif msg_type == 'link':
        return models.LinkMsg(xml_data)
    elif msg_type in ['video', 'shortvideo']:
        return models.VideoMsg(xml_data)
    elif msg_type == 'location':
        return models.GeoMsg(xml_data)


def parse_event_xml(msg_type, xml_data):
    if msg_type in ['subscribe', 'unsubscribe']:
        return models.SubscribeEvent(xml_data)
    elif msg_type == 'scan':
        return models.ScanQrCodeEvent(xml_data)
    elif msg_type == 'location':
        pass
    elif msg_type == 'click':
        pass
    elif msg_type == 'view':
        pass


def find_stock_code_by_stock_name(stock_name, market_code='A'):
    result = []
    url = "http://biz.finance.sina.com.cn/suggest/lookup_n.php?q=%s&t=keyword&c=all"
    target_ids = {'A': 'stock_stock', 'M': 'us_stock', 'G': 'hk_stock'}
    target_id = target_ids[market_code]
    url = url % stock_name
    resp = requests.get(url)
    if not resp or resp.status_code > 400:
        return result
    soup = BeautifulSoup(resp.content, 'lxml', from_encoding='utf-8')
    target = soup.find(id=target_id)
    if target is None:
        import re
        target = soup.find(id='stockName')
        stock = target.get_text()
        name, code = stock.split('(')
        code = re.findall(r'\d+', code)[0]
        name = code +  ' ' + name
        result.append(name)
    else:
        hrefs = target.find_next_sibling('div')
        if hrefs is None:
            return result
        for a in hrefs.find_all('a'):
            if not a.get_text():
                continue
            result.append(a.get_text())
    return result


def find_brief_info_by_stock_code(stock_code, market_code='G'):
    prefix = 'hk'
    url = "http://hq.sinajs.cn/list="
    result = {}
    if market_code == 'M' and stock_code.isalpha():
        prefix = 'gb'
        url += prefix + '_' + stock_code.lower()
    elif market_code == 'A':
        if stock_code.startswith('sh') or stock_code.startswith('sz'):
            url += stock_code
        else:
            prefix = {'6': 'sh', '0': 'sz'}[stock_code[0]]
            url += prefix + stock_code
    elif market_code == 'G' and stock_code.isdigit():
        url += prefix + stock_code
   
    resp = requests.get(url)
    if not resp or resp.status_code > 400 or '""' in resp.content:
        return result
    info = resp.content.decode(encoding=resp.encoding)
    info = info.split('="')
    if len(info[1]) < 3:
        return result
    info = info[1].split(',')
    #print info
    if market_code == 'G':
        info = info[1:]
        result['stock_name'], result['today_open_price'], result['yesterday_close_price'], result['current_price'], result['highest_price_in_today'], result['lowest_price_in_today'], result['highest_price_in_52_weeks'], result['lowest_price_in_52_weeks'], result['real_time'] = info[0], info[1], info[2], info[3], info[4], info[5], info[-4], info[-3], info[-2]+' '+info[-1][:-3]
    elif market_code == 'M':
        result['stock_name'], result['today_open_price'], result['yesterday_close_price'], result['current_price'], result['highest_price_in_today'], result['lowest_price_in_today'], result['highest_price_in_52_weeks'], result['lowest_price_in_52_weeks'], result['real_time'] = info[0], info[5], info[-2], info[1], info[6], info[7], info[8], info[9], info[3]
    elif market_code == 'A':
        result['stock_name'], result['today_open_price'], result['yesterday_close_price'], result['current_price'], result['highest_price_in_today'], result['lowest_price_in_today'], result['highest_price_in_52_weeks'], result['lowest_price_in_52_weeks'], result['real_time'] = info[0], info[1], info[2], info[3], info[4], info[5], '', '', info[-3]+' '+info[-2]
    return result


def find_brief_info_by_stock_name_or_stock_code(stock, market_code):
    result = []
    if not stock.isalpha() and not stock.isdigit():
        stock_info_list = find_stock_code_by_stock_name(stock, market_code)
        total = len(stock_info_list)
        #print stock_info_list
        for item in stock_info_list[:5]: #前五条
            stock_code, stock_name = item.split(' ', 1)
            res = find_brief_info_by_stock_code(stock_code, market_code)
            #print res
            if not res:
                continue
            res['market_code'], res['stock_code'] = market_code, stock_code
            result.append(res)
    else:
        res = find_brief_info_by_stock_code(stock, market_code)
        if res:
            res['market_code'], res['stock_code'] = market_code, stock
            result.append(res)
    return result, total


def upload_image(img_path, access_token):
    import os
    if os.path.isfile(img_path):
        files = {'media': open(img_path, 'rb')}
        resp = requests.post(config.wx_upload_image_url % access_token, files=files)
        if not resp or resp.status_code > 400:
            return None
        return resp.content

 
