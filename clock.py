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
import smbus

from luma.core.render import canvas
from luma.core.interface.serial import spi
from luma.oled.device import ssd1309
from PIL import Image, ImageFont, ImageOps, ImageChops
from service import GetWeatherInfo

path = os.path.dirname(os.path.realpath(__file__))

WEEK = {'1': u"一", '2': u"二", '3': u"三", '4': u"四", '5': u"五", '6': u"六", '0': u"日"}

# pi sugar
## i2c address
SUGAR_ADDR = 0x57
BATT_CAP_BANK = 0x2A

#i2c address
PAJ7620U2_I2C_ADDRESS   = 0x73
#Register Bank select
PAJ_BANK_SELECT			= 0xEF			#Bank0== 0x00,Bank1== 0x01
#Register Bank 0
PAJ_SUSPEND				= 0x03		#I2C suspend command (Write = 0x01 to enter suspend state). I2C wake-up command is slave ID wake-up. Refer to topic “I2C Bus Timing Characteristics and Protocol”
PAJ_INT_FLAG1_MASK		= 0x41		#Gesture detection interrupt flag mask
PAJ_INT_FLAG2_MASK		= 0x42		#Gesture/PS detection interrupt flag mask
PAJ_INT_FLAG1		    = 0x43		#Gesture detection interrupt flag
PAJ_INT_FLAG2			= 0x44		#Gesture/PS detection interrupt flag
PAJ_STATE				= 0x45		#State indicator for gesture detection (Only functional at gesture detection mode)
PAJ_PS_HIGH_THRESHOLD	= 0x69		#PS hysteresis high threshold (Only functional at proximity detection mode)		
PAJ_PS_LOW_THRESHOLD	= 0x6A		#PS hysteresis low threshold (Only functional at proximity detection mode)
PAJ_PS_APPROACH_STATE	= 0x6B		#PS approach state,  Approach = 1 , (8 bits PS data >= PS high threshold),  Not Approach = 0 , (8 bits PS data <= PS low threshold)(Only functional at proximity detection mode)
PAJ_PS_DATA				= 0x6C		#PS 8 bit data(Only functional at gesture detection mode)
PAJ_OBJ_BRIGHTNESS		= 0xB0		#Object Brightness (Max. 255)
PAJ_OBJ_SIZE_L			= 0xB1		#Object Size(Low 8 bit)		
PAJ_OBJ_SIZE_H			= 0xB2		#Object Size(High 8 bit)	
#Register Bank 1
PAJ_PS_GAIN				= 0x44	    #PS gain setting (Only functional at proximity detection mode)
PAJ_IDLE_S1_STEP_L		= 0x67		#IDLE S1 Step, for setting the S1, Response Factor(Low 8 bit)
PAJ_IDLE_S1_STEP_H		= 0x68		#IDLE S1 Step, for setting the S1, Response Factor(High 8 bit)	
PAJ_IDLE_S2_STEP_L		= 0x69		#IDLE S2 Step, for setting the S2, Response Factor(Low 8 bit)
PAJ_IDLE_S2_STEP_H		= 0x6A		#IDLE S2 Step, for setting the S2, Response Factor(High 8 bit)
PAJ_OPTOS1_TIME_L		= 0x6B		#OPtoS1 Step, for setting the OPtoS1 time of operation state to standby 1 state(Low 8 bit)	
PAJ_OPTOS2_TIME_H		= 0x6C		#OPtoS1 Step, for setting the OPtoS1 time of operation state to standby 1 stateHigh 8 bit)	
PAJ_S1TOS2_TIME_L		= 0x6D		#S1toS2 Step, for setting the S1toS2 time of standby 1 state to standby 2 state(Low 8 bit)	
PAJ_S1TOS2_TIME_H		= 0x6E		#S1toS2 Step, for setting the S1toS2 time of standby 1 state to standby 2 stateHigh 8 bit)	
PAJ_EN					= 0x72		#Enable/Disable PAJ7620U2
#Gesture detection interrupt flag
PAJ_UP				    = 0x01
PAJ_DOWN			    = 0x02
PAJ_LEFT			    = 0x04
PAJ_RIGHT			    = 0x08
PAJ_FORWARD		    	= 0x10
PAJ_BACKWARD		    = 0x20
PAJ_CLOCKWISE			= 0x40
PAJ_COUNT_CLOCKWISE		= 0x80
PAJ_WAVE				= 0x100
#Power up initialize array
Init_Register_Array = (
	(0xEF,0x00),
	(0x37,0x07),
	(0x38,0x17),
	(0x39,0x06),
	(0x41,0x00),
	(0x42,0x00),
	(0x46,0x2D),
	(0x47,0x0F),
	(0x48,0x3C),
	(0x49,0x00),
	(0x4A,0x1E),
	(0x4C,0x20),
	(0x51,0x10),
	(0x5E,0x10),
	(0x60,0x27),
	(0x80,0x42),
	(0x81,0x44),
	(0x82,0x04),
	(0x8B,0x01),
	(0x90,0x06),
	(0x95,0x0A),
	(0x96,0x0C),
	(0x97,0x05),
	(0x9A,0x14),
	(0x9C,0x3F),
	(0xA5,0x19),
	(0xCC,0x19),
	(0xCD,0x0B),
	(0xCE,0x13),
	(0xCF,0x64),
	(0xD0,0x21),
	(0xEF,0x01),
	(0x02,0x0F),
	(0x03,0x10),
	(0x04,0x02),
	(0x25,0x01),
	(0x27,0x39),
	(0x28,0x7F),
	(0x29,0x08),
	(0x3E,0xFF),
	(0x5E,0x3D),
	(0x65,0x96),
	(0x67,0x97),
	(0x69,0xCD),
	(0x6A,0x01),
	(0x6D,0x2C),
	(0x6E,0x01),
	(0x72,0x01),
	(0x73,0x35),
	(0x74,0x00),
	(0x77,0x01),
)
#Approaches register initialization array
Init_PS_Array = (
	(0xEF,0x00),
	(0x41,0x00),
	(0x42,0x00),
	(0x48,0x3C),
	(0x49,0x00),
	(0x51,0x13),
	(0x83,0x20),
	(0x84,0x20),
	(0x85,0x00),
	(0x86,0x10),
	(0x87,0x00),
	(0x88,0x05),
	(0x89,0x18),
	(0x8A,0x10),
	(0x9f,0xf8),
	(0x69,0x96),
	(0x6A,0x02),
	(0xEF,0x01),
	(0x01,0x1E),
	(0x02,0x0F),
	(0x03,0x10),
	(0x04,0x02),
	(0x41,0x50),
	(0x43,0x34),
	(0x65,0xCE),
	(0x66,0x0B),
	(0x67,0xCE),
	(0x68,0x0B),
	(0x69,0xE9),
	(0x6A,0x05),
	(0x6B,0x50),
	(0x6C,0xC3),
	(0x6D,0x50),
	(0x6E,0xC3),
	(0x74,0x05),
)
#Gesture register initializes array
Init_Gesture_Array = (
	(0xEF,0x00),
	(0x41,0x00),
	(0x42,0x00),
	(0xEF,0x00),
	(0x48,0x3C),
	(0x49,0x00),
	(0x51,0x10),
	(0x83,0x20),
	(0x9F,0xF9),
	(0xEF,0x01),
	(0x01,0x1E),
	(0x02,0x0F),
	(0x03,0x10),
	(0x04,0x02),
	(0x41,0x40),
	(0x43,0x30),
	(0x65,0x96),
	(0x66,0x00),
	(0x67,0x97),
	(0x68,0x01),
	(0x69,0xCD),
	(0x6A,0x01),
	(0x6B,0xB0),
	(0x6C,0x04),
	(0x6D,0x2C),
	(0x6E,0x01),
	(0x74,0x00),
	(0xEF,0x00),
	(0x41,0xFF),
	(0x42,0x01),
)

class PAJ7620U2(object):
	def __init__(self,address=PAJ7620U2_I2C_ADDRESS):
		self._address = address
		self._bus = smbus.SMBus(0) # we connect to i2c-0
		time.sleep(0.5)
		if self._read_byte(0x00) == 0x20:
			print("\nGesture Sensor OK\n")
			for num in range(len(Init_Register_Array)):
				self._write_byte(Init_Register_Array[num][0],Init_Register_Array[num][1])
		else:
			print("\nGesture Sensor Error\n")
		self._write_byte(PAJ_BANK_SELECT, 0)
		for num in range(len(Init_Gesture_Array)):
				self._write_byte(Init_Gesture_Array[num][0],Init_Gesture_Array[num][1])
	def _read_byte(self,cmd):
		return self._bus.read_byte_data(self._address,cmd)

	def _read_u16(self,cmd):
		LSB = self._bus.read_byte_data(self._address,cmd)
		MSB = self._bus.read_byte_data(self._address,cmd+1)
		return (MSB	<< 8) + LSB
	def _write_byte(self,cmd,val):
		self._bus.write_byte_data(self._address,cmd,val)
	def check_gesture(self):
		Gesture_Data=self._read_u16(PAJ_INT_FLAG1)
		if Gesture_Data == PAJ_UP:
			print("Up\r\n")
		elif Gesture_Data == PAJ_DOWN:
			print("Down\r\n")
		elif Gesture_Data == PAJ_LEFT:
			print("Left\r\n")
		elif Gesture_Data == PAJ_RIGHT:
			print("Right\r\n")
		elif Gesture_Data == PAJ_FORWARD:
			print("Forward\r\n")
		elif Gesture_Data == PAJ_BACKWARD:
			print("Backward\r\n")
		elif Gesture_Data == PAJ_CLOCKWISE:
			print("Clockwise\r\n")
		elif Gesture_Data == PAJ_COUNT_CLOCKWISE:
			print("AntiClockwise\r\n")
		elif Gesture_Data == PAJ_WAVE:
			print("Wave\r\n")
		return Gesture_Data


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

    sugarBus = smbus.SMBus(1) # sugar is on i2c-1
    time.sleep(0.5)
    if sugarBus.read_byte_data(SUGAR_ADDR, 0x50) == 0xD7:
        print("\nPiSugar is OK\n")
    else:
        print("Fail to read PiSugar")

    paj7620u2 = PAJ7620U2()
    interval = 0.5
    isDisp = 0
    count = 0
    hour = -1

    while True:
        gest = paj7620u2.check_gesture()
        if count % 20 == 0 or hour == -1:
            now = datetime.datetime.now()
            # today_date = now.strftime("%d %b %y")
            today_time = now.strftime("%H:%M:%S")
            if today_time != today_last_time:
                today_last_time = today_time
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
                        weather = now["now"]["icon"]
                        if abs(hour - 12) < 6:  # 白天
                            cast1 = fore["daily"][0]["iconNight"]
                            name1 = '今晚'
                            cast2 = fore["daily"][1]["iconDay"]
                            name2 = '明天'
                        elif hour <= 6:
                            cast1 = fore["daily"][0]["iconDay"]
                            name1 = '今早'
                            cast2 = fore["daily"][0]["iconNight"]
                            name2 = '今晚'
                        else:  # 晚上
                            cast1 = fore["daily"][1]["iconDay"]
                            name1 = '明天'
                            cast2 = fore["daily"][2]["iconDay"]
                            name2 = '后天'

                        print("Display weather...")
                        #try:  # 加载天气图片
                        if True:
                            bmp0 = Image.open(os.path.join(path + "/jpg/", weather + ".jpg")).convert(device.mode)
                            bmp0.thumbnail((24, 24))
                            bmp0 = ImageChops.invert(bmp0)

                            bmp1 = Image.open(os.path.join(path + "/jpg/", cast1 + ".jpg")).convert(device.mode)
                            bmp1.thumbnail((16, 16))
                            bmp1 = ImageChops.invert(bmp1)

                            bmp2 = Image.open(os.path.join(path + "/jpg/", cast2 + ".jpg")).convert(device.mode)
                            bmp2.thumbnail((16, 16))
                            bmp2 = ImageChops.invert(bmp2)

                    else:
                        weatherOK = False

        if (hour > 6 and isDisp <=0) or gest != 0 :
            isDisp = 5
            battery = sugarBus.read_byte_data(SUGAR_ADDR, BATT_CAP_BANK)
            print(battery)
            with canvas(device) as draw:
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
                    draw.line((0, device.height - 1, (device.width - 1) * (battery / 100), device.height - 1), fill="white")

        if hour <= 6 and isDisp > 0 and isDisp - interval <= 0:
            device.clear()

        if isDisp > 0:
            isDisp -= interval
        count += interval
        count %= 100
        time.sleep(interval)


if __name__ == "__main__":
    try:
        serial = spi(device=0, port=0)
        device = ssd1309(serial, rotate=1)
        main()
    except KeyboardInterrupt:
        pass
