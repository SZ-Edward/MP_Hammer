#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'Aurora Wu (wuxy91@gmail.com)'
__copyright__ = "Copyright (c) 2013- aurorawu.com"


class Message(object):
    """
    微信普通消息Model
    文本消息(TextMsg)     msg_type=text
    图片消息(ImageMsg)    msg_type=image
    语音消息(VoiceMsg)    msg_type=voice
    链接消息(LinkMsg)     msg_type=link
    视频消息(VideoMsg)    msg_type=video
    小视频消息(VideoMsg)  msg_type=shortvideo
    地理位置消息(GeoMsg)  msg_type=location
    """
    def __init__(self, xml_data):
        self.to_user_name = xml_data.find('ToUserName').text.encode("utf-8")
        self.from_user_name = xml_data.find('FromUserName').text
        self.create_time = xml_data.find('CreateTime').text
        self.msg_type = xml_data.find('MsgType').text.lower()
        self.msg_id = xml_data.find('MsgId').text


class TextMsg(Message):
    def __init__(self, xml_data):
        Message.__init__(self, xml_data)
        self.content = xml_data.find('Content').text.encode("utf-8")


class ImageMsg(Message):
    def __init__(self, xml_data):
        Message.__init__(self, xml_data)
        self.media_id = xml_data.find('MediaId').text
        self.pic_url = xml_data.find('PicUrl').text


class VoiceMsg(Message):
    def __init__(self, xml_data):
        Message.__init__(self, xml_data)
        self.media_id = xml_data.find('MediaId').text
        self.format = xml_data.find('Format').text
        self.recognition = ''
        if xml_data.find('Recognition') is not None:
            self.recognition = xml_data.find('Recognition').text


class VideoMsg(Message):
    def __init__(self, xml_data):
        Message.__init__(self, xml_data)
        self.media_id = xml_data.find('MediaId').text
        self.thumb_media_id = xml_data.find('ThumbMediaId').text


class LinkMsg(Message):
    def __init__(self, xml_data):
        Message.__init__(self, xml_data)
        self.title = xml_data.find('Title').text.encode("utf-8")
        self.description = xml_data.find('Description').text.encode("utf-8")
        self.url = xml_data.find('Url').text


class GeoMsg(Message):
    def __init__(self, xml_data):
        Message.__init__(self, xml_data)
        self.geo_x = xml_data.find('Location_X').text
        self.geo_y = xml_data.find('Location_Y').text
        self.scale = xml_data.find('Scale').text
        self.label = xml_data.find('Label').text


class Event(object):
    """
    微信事件推送Model
    关注/取消关注事件(SubscribeEvent)             event=subscribe(关注)/unsubscribe(取消关注)
    TODO:
    扫描带参数二维码事件(ScanQrCodeEvent)          event=scan
    上报地理位置事件()              event=location
    自定义菜单事件()                event=click
    点击菜单拉取消息时的事件推送()  event=click
    点击菜单跳转链接时的事件推送()  event=view
    """
    def __init__(self, xml_data):
        self.to_user_name = xml_data.find('ToUserName').text
        self.from_user_name = xml_data.find('FromUserName').text
        self.create_time = xml_data.find('CreateTime').text
        self.msg_type = xml_data.find('MsgType').text
        self.event = xml_data.find('Event').text


class SubscribeEvent(Event):
    def __init__(self, xml_data):
        Event.__init__(self, xml_data)
        self.followed = True if xml_data.find('Event').text == 'subscribe' else False


class ScanQrCodeEvent(Event):
    def __init__(self, xml_data):
        Event.__init__(self, xml_data)
        self.qrscene = xml_data.find('EventKey').text
        self.ticket = xml_data.find('Ticket').text
