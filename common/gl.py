#!/usr/bin/evn python
#-*- coding:utf-8 -*-
import tempfile

color = [
    [(0,0,255),0.7,0.5],
    [(214,112,218),0.8,0.4],
    [(238,104,123),0.8,0.3]
]

ADB_CMD = ""
AAPT_CMD = ""
MOBILE_WIDTH = 0
MOBILE_HEIGHT = 0
WINDOW = 0

TEMP_IMAGE_PATH = "%s/screenshot.png" % tempfile.gettempdir()
