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

import math
import time
import datetime
# from demo_opts import get_device
from luma.core.render import canvas
from luma.core.interface.serial import spi
from luma.oled.device import ssd1309
from PIL import ImageFont

def posn(angle, arm_length):
    dx = int(math.cos(math.radians(angle)) * arm_length)
    dy = int(math.sin(math.radians(angle)) * arm_length)
    return (dx, dy)

WEEK = {'1': u"一", '2': u"二", '3': u"三", '4': u"四", '5': u"五", '6': u"六", '0': u"日"}


def main():
    today_last_time = "Unknown"
    timeSize = 52
    ehsmbFont = ImageFont.truetype("./EHSMB.TTF", timeSize)
    dateSize = 18
    myFont = ImageFont.truetype("./Font.ttc", dateSize)
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

                draw.text((0, 0), hourStr, font=ehsmbFont, fill="white")
                draw.text((0, timeSize), minStr, font=ehsmbFont, fill="white")
                draw.text((0, 2 * timeSize), today_date, font=myFont, fill="white")
                draw.text((64 - dateSize, 2 * timeSize), WEEK[today_week], font=myFont, fill="white")


if __name__ == "__main__":
    try:
        # device = get_device()
        serial = spi(device=0, port=0)
        device = ssd1309(serial, rotate=1)
        main()
    except KeyboardInterrupt:
        pass
