#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014-18 Richard Hull and contributors
# See LICENSE.rst for details.
# PYTHON_ARGCOMPLETE_OK

"""
An analog clockface with date & time.

Ported from:
https://gist.github.com/TheRayTracer/dd12c498e3ecb9b8b47f#file-clock-py
"""

import os
import math
import time
import datetime
# from demo_opts import get_device
from luma.core.render import canvas
from luma.core.interface.serial import spi
from luma.oled.device import ssd1309
from PIL import Image, ImageFont, ImageOps, ImageChops
from service import GetWeatherInfo

def posn(angle, arm_length):
    dx = int(math.cos(math.radians(angle)) * arm_length)
    dy = int(math.sin(math.radians(angle)) * arm_length)
    return (dx, dy)

path = os.path.dirname(os.path.realpath(__file__))

WEATHER = {u"小雨": "WXYU.BMP", u"中雨": "WZYU.BMP", u"大雨": "WDYU.BMP", u"暴雨": "WWET.BMP",
           u"晴": "WQING.BMP", u"多云": "WDYZQ.BMP", u"阴": "WYIN.BMP", u"雷阵雨": "WLZYU.BMP",
           u"阵雨": "WYGTQ.BMP", u"霾": "WFOG.BMP", u"雾": "WWU.BMP", u"雪": "WXUE.BMP",
           u"雨夹雪": "WYJX.BMP", u"冰雹": "WBBAO.BMP", u"月亮": "WMOON.BMP", u"深夜": "WSLEEP.BMP",
           u"日落": "SUMSET.BMP", u"日出": "SUNRISE.BMP", u"雨": "WZYU.BMP"}
WEEK = {'1': u"一", '2': u"二", '3': u"三", '4': u"四", '5': u"五", '6': u"六", '0': u"日"}


def main():
    weatherOK = False
    today_last_time = "Unknown"
    timeSize = 48
    ehsmbFont = ImageFont.truetype(path + "/EHSMB.TTF", int(timeSize / 8 * 9))
    dateSize = 16
    Font16 = ImageFont.truetype(path + "/Font.ttc", int(dateSize / 8 * 9))
    Font7 = ImageFont.truetype(path + "/guanzhi.ttf", 7)
    bmp = Image.new("1", (16, 16))
    topOffset = -3

    while True:
        now = datetime.datetime.now()
        # today_date = now.strftime("%d %b %y")
        today_time = now.strftime("%H:%M:%S")
        if today_time != today_last_time:
            today_last_time = today_time
            with canvas(device) as draw:
                now = datetime.datetime.now()
                today_date = now.strftime("%m/%d")
                today_week = now.strftime("%w")
                hourStr = now.strftime("%H")
                minStr = now.strftime("%M")
                hour = int(hourStr)
                min = int(minStr)
                sec = int(now.strftime("%S"))

                if (hour % 6 == 0 and min < 1 and sec < 39) or (not weatherOK):
                    fore, now, weatherText = GetWeatherInfo()
                    if weatherText == "":
                        weatherOK = True
                        weather = now["lives"][0]["weather"]
                        if abs(hour - 12) < 6:  # 白天
                            cast1 = fore['forecasts'][0]['casts'][0]['nightweather']
                            name1 = '今晚'
                            cast2 = fore['forecasts'][0]['casts'][1]['dayweather']
                            name2 = '明天'
                        elif hour <= 6:
                            cast1 = fore['forecasts'][0]['casts'][0]['dayweather']
                            name1 = '今早'
                            cast2 = fore['forecasts'][0]['casts'][0]['nightweather']
                            name2 = '今晚'
                        else:  # 晚上
                            cast1 = fore['forecasts'][0]['casts'][1]['dayweather']
                            name1 = '明天'
                            cast2 = fore['forecasts'][0]['casts'][2]['dayweather']
                            name2 = '后天'

                        print("Display weather...")
                        #try:  # 加载天气图片
                        if True:
                            bmp0 = Image.open(os.path.join(path + '/bmp', WEATHER[weather])).convert(device.mode)
                            bmp0.thumbnail((24, 24))
                            bmp0 = ImageChops.invert(bmp0)

                            bmp1 = Image.open(os.path.join(path + '/bmp', WEATHER[cast1])).convert(device.mode)
                            bmp1.thumbnail((16, 16))
                            bmp1 = ImageChops.invert(bmp1)

                            bmp2 = Image.open(os.path.join(path + '/bmp', WEATHER[cast2])).convert(device.mode)
                            bmp2.thumbnail((16, 16))
                            bmp2 = ImageChops.invert(bmp2)

#                            bmp = Image.open(os.path.join(path + '/bmp', WEATHER[cast1]))
#                            bmp.thumbnail((36, 36))
#                            image.paste(bmp, (218, 80))
#                            draw.text((224, 116), name1, font = font12, fill = 0)

#                            bmp = Image.open(os.path.join(path + '/bmp', WEATHER[cast2]))
#                            bmp.thumbnail((36, 36))
#                            image.paste(bmp, (258, 80))
#                            draw.text((264, 116), name2, font = font12, fill = 0)
#                        except Exception as error:
#                            text += '%s ' % error
#                             print("%s" % error)

#                        if text == '':  # 输出其它天气信息
#                            draw.rectangle((0, 96, 214, 127), fill = 255, outline = 0)
#                            info = '%2s°C %2s%% ' % (now['lives'][0]['temperature'], now['lives'][0]['humidity'])
#                            #info = '%2d°C %2d%% ' % (temperature, humidity)
#                            info += time.strftime('%m/%d ')
#                            info += '%s' % WEEK[time.strftime('%w')]
#                            draw.text((4, 98), info, font = font24, fill = 0)
                    else:
                        weatherOK = False

                if hour > 6 or hour < 1:
                    draw.text((0, topOffset), hourStr, font=ehsmbFont, fill="white")
                    draw.text((0, timeSize + topOffset * 2 - 1), minStr, font=ehsmbFont, fill="white")
                    draw.text((0, 2 * timeSize + topOffset * 3 - 2), today_date, font=Font16, fill="white")
                    draw.text((64 - dateSize, 2 * timeSize + topOffset * 3 - 3), WEEK[today_week], font=Font16, fill="white")
                    if weatherOK:
                        draw.bitmap((0, 2 * timeSize + dateSize + topOffset * 2 - 2), bmp0, fill="white")
                        draw.bitmap((26, 2 * timeSize + dateSize + topOffset * 2 - 2), bmp1, fill="white")
                        draw.bitmap((44, 2 * timeSize + dateSize + topOffset * 2 - 2), bmp2, fill="white")
                        draw.text((26 + 1, device.height - 9), name1, font=Font7, fill="white")
                        draw.text((44 + 1, device.height - 9), name2, font=Font7, fill="white")
                        draw.line((0, device.height - 1, device.width - 1, device.height - 1), fill="white")
                    # draw.text((24
        time.sleep(20)


if __name__ == "__main__":
    try:
        # device = get_device()
        serial = spi(device=0, port=0)
        device = ssd1309(serial, rotate=1)
        main()
    except KeyboardInterrupt:
        pass
