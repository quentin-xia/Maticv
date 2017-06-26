#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
from common.adb import Adb
import common.app as app
import common.gl as gl
from common.utils import Utils
from common.pattern import Pattern
from common.region import Region
from common.screencap import MinicapStream
import platform
if platform.system() is "Windows":
    try:
        import common.opencv.x32.cv2 as cv2
    except:
        import common.opencv.x64.cv2 as cv2
else:
    import common.opencv.linux.cv2 as cv2


class MobileDriver(Adb,Region):
    """
    Attributes:
    ####- platformName eg:Android
    - app（安装包）
    - device（设备id)
    - appPackage
    - appActivity
    - window(0-3,默认0竖屏)
    - clear(清除缓存，默认True)
    """
    def __init__(self,capabilities):
        super(MobileDriver,self).__init__()

        if capabilities is None:
            msg = "Desired capabilities can't be None"
            raise Exception(msg)

        if not isinstance(capabilities,dict):
            msg = "Desired capabilities must be a dectionary"
            raise Exception(msg)

        deviceName = capabilities.get("device")
        if deviceName:
            self.wait_for_device(deviceName)
        else:
            self.wait_for_device()
            #deviceName = self.wait_for_device()[1]
            #capabilities["device"] = deviceName


        self.screencap = MinicapStream()
        self.screencap.ReadImageStream(gl.TEMP_IMAGE_PATH)
        image = cv2.imread(gl.TEMP_IMAGE_PATH,1)
        #设置手机分辨率
        gl.MOBILE_WIDTH = len(image[0])
        gl.MOBILE_HEIGHT = len(image)
        #print gl.MOBILE_WIDTH,gl.MOBILE_HEIGHT
        
        """
        w = capabilities.get("width")
        h = capabilities.get("height")
        if w and h:
            width = w
            height = h
        else:
            width,height = self.get_screen_resolution()
        gl.MOBILE_WIDTH = width
        gl.MOBILE_HEIGHT = height
        """

        self.check_api_level()
        apk = capabilities.get("app")
        pkg = capabilities.get("appPackage")
        act = capabilities.get("appActivity")
        try:
            window = int(capabilities.get("window"))
        except TypeError:
            window = 0
        clr = capabilities.get("clear")
        if clr == None or clr == True:
            clr = True
        else:
            if isinstance(clr,str):
                if clr.lower() == "true":
                    clr = True
                else:
                    clr = False
            else:
                clr = False
        utils = Utils()
        if apk:
            capabilities["app"] = app.configure_app(apk)
            pkg,act = self.package_and_launch_activity_from_manifest(capabilities["app"])
            utils.install_app_for_test(apk=apk,pkg=pkg)
        elif pkg and act:
            installed = self.is_app_installed(pkg)
            if not installed:
                msg = "App is not installed,app can't be none"
                raise Exception(msg)
            else:
                utils.install_app_for_test(pkg=pkg,clr=clr)
        else:
            msg = "app or appPackage、appActivity can't be none"
            raise Exception(msg)
        if window:
            if 0 <= window <=3:
                gl.WINDOW = window
        self.unlock_screen()
        self.set_ime()
        self.set_screen_on()
        self.wait_for_server(pkg,act)
        self.pkg = pkg
        self.act = act

    #def pattern(self,pattern=None,timeout=5):
    #    return Pattern(pattern,timeout)



    #等待应用启动
    def wait_for_server(self,pkg,act):
        self.start_app(pkg,act)
        self.wait_for_activity(pkg,act)

    #屏幕分辨率
    def size(self):
        return self.get_screen_resolution()

    #wifi是否打开
    def is_wifi_on(self):
        return self.wifi_on()

    #是否打开飞行模式
    def is_airplane_mode_on(self):
        return self.airplane_mode_on()

    #打开/关闭飞行模式并广播
    # flag: 1 (to turn on) or 0 (to turn off)
    def set_airplane_mode(self,flag):
        self.set_airplane_mode_on_or_off(flag)

    #是否打开软键盘
    def is_soft_keyboard_present(self):
        return self.soft_keyboard_present()

    #获取package
    def get_package(self):
        return self.pkg

    #获取activity
    def get_activity(self):
        return self.act

    #等待
    def sleep(self,seconds):
        time.sleep(seconds)

    #关闭应用
    def close(self):
        self.force_stop(self.pkg)

    #截屏
    def screenshot(self,filename):
        #temp_png = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
        #self.shell("screencap -p /sdcard/screenshot.png")
        #self.pull("/sdcard/screenshot.png",filename)
        self.screencap.ReadImageStream(filename)
