import xml.etree.ElementTree as ET
import config
from WXBizMsgCrypt import WXBizMsgCrypt
import models


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


def model2reply(from_model, reply_content):
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
    msg_type = xml_data.find('MsgType').text.lower()
    if msg_type != 'event':
        return parse_message_xml(msg_type, xml_data)
    else:
        pass


def parse_message_xml(msg_type, xml_data):
    """parse wechat xml data to models"""
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


