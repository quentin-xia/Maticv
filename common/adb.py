#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os,sys,time,re
import platform
import subprocess
import gl



class Adb(object):
    def __init__(self):
        gl.ADB_CMD = self._get_sdk_binary_present("adb")
        gl.AAPT_CMD = self._get_sdk_binary_present("aapt")

    def adb(self,cmd):
        cmd = cmd.strip()
        if not cmd:
            msg = "You need to pass in a command to adb()"
            raise Exception(msg)
        cmd = "%s %s" % (gl.ADB_CMD,cmd)
        #print cmd
        pipe = subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
        out = pipe.stdout.read()
        err = pipe.stderr.read()
        if err and err.find(" bytes in ") == -1:
            msg = err
            raise Exception(msg)
        else:
            if out.lower().find("error:") == -1:
                return out
            else:
                msg = out
                raise Exception(msg)

    def shell(self,cmd):
        cmd = "shell %s" % cmd
        return self.adb(cmd)

    def wait_for_device(self,deviceId = None,waitSec = 10):
        #self._restart_adb()
        sec = 0.75
        endAt = time.time() + waitSec

        def do_wait():
            if time.time() > endAt:
                msg = "Device did not become ready in %s secs; are sure it's powered on?" % waitSec
                raise Exception(msg)
            devices = self._get_connected_devices()
            if devices == []:
                time.sleep(sec)
                return do_wait()
            else:
                if not deviceId:
                    device = devices[0]["udid"]
                    self._set_device_id(device)
                    return device
                else:
                    for i in range(len(devices)):
                        if devices[i]["udid"] == deviceId:
                            self._set_device_id(deviceId)
                            return deviceId
                time.sleep(sec)
                return do_wait()
                
        dev = do_wait()
        return self._check_adb_connection_is_up(),dev

    
    def pull(self,remotePath,localPath):
        cmd = "pull %s %s" % (remotePath,localPath)
        self.adb(cmd)

    def push(self,localPath,remotePath):
        cmd = "push %s %s" % (localPath,remotePath)
        self.adb(cmd)

    #获取屏幕尺寸
    def get_screen_resolution(self):
        display = []
        pattern = re.compile(r"\d+")
        if platform.system() is "Windows":
            cmd = "dumpsys display | findstr PhysicalDisplayInfo"
            cmd1 = "dumpsys window | findstr Display: | findstr init="
            cmd2 = "dumpsys display | findstr DisplayDeviceInfo"
        else:
            cmd = "dumpsys display | grep PhysicalDisplayInfo"
            cmd1 = "dumpsys window | grep Display: | grep init="
            cmd2 = "dumpsys display | grep DisplayDeviceInfo"
        stdout = self.shell(cmd)
        display = pattern.findall(stdout)
        if display == []:
            stdout = self.shell(cmd1)
            display = pattern.findall(stdout)
        if display == []:
            stdout = self.shell(cmd2)
            display = pattern.findall(stdout)
            if display: 
                display = display[1:]
        if display == []:
            msg = "Can't get screen resolution"
            raise Exception(msg)
        return (int(display[0]),int(display[1]))

    #启动APP
    def start_app(self,pkg,act,retry=True):
        if not pkg or not act:
            msg = "Parameter 'appPackage' and 'appActivity' is required for lunching application"
            raise Exception(msg)
        cmd = "am start -n %s/%s" % (pkg,act)

        try:
            stdout = self.shell(cmd)
        except Exception,ex:
            if retry:
                self.start_app(pkg,act,False)
            else:
                msg = ex
                raise Exception(msg)
        return True
            

    def check_api_level(self):
        apiLv = self._get_api_level()
        if apiLv < 16:
            msg = "Api Level should >= 16"
            raise Exception(msg)
        return True

    #获取package和activity
    def package_and_launch_activity_from_manifest(self,app):
        badging = " ".join([gl.AAPT_CMD,"dump","badging",app])
        pipe = subprocess.Popen(badging,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
        out = pipe.stdout.read()
        err = pipe.stderr.read()
        if err:
            msg = err
            raise Exception(msg)
        package = re.search(r"(package: name=(\S)+)",out)
        if package:
            package = package.group()
        else:
            msg = "Get package failed"
            raise Exception(msg)

        if len(package) > 16:
            package = package[15:-1]
        else:
            package = None

        activity = re.search(r"(launchable-activity: name=(\S)+)",out)
        if activity:
            activity = activity.group()
        else:
            msg = "Get activity failed"
            raise Exception(msg)

        if len(activity) > 28:
            activity = activity[27:-1]
        else:
            activity = None

        return package,activity


    #安装apk
    def install_apk(self,apk,replace=True):
        cmd = "install "
        if replace:
            cmd += "-r "
        cmd += apk
        stdout = self.adb(cmd)
        stdout = stdout.strip()
        if stdout.find("Success") != -1:
            return True
        else:
            msg = "App was not installed"
            raise Exception(msg)

    #解锁屏幕
    def unlock_screen(self):
        if self._is_screen_locked():
            self._push_unlock()
            timeout = 10
            endAt = time.time() + timeout
            sec = 0.75
            def unlock_and_check():
                pkg = "io.matip.unlock"
                activity = ".Unlock"
                self.start_app(pkg,activity)
                if not self._is_screen_locked():
                    return True
                if time.time() > endAt:
                    msg = "Screen did not unlock"
                    raise Exception(msg)
                else:
                    time.sleep(sec)
                    unlock_and_check()
            unlock_and_check()

    #设置输入法
    def set_ime(self):
        self._push_ime()
        cmd = "ime set com.android.maticvkeyboard/.MaticvIME"
        self.shell(cmd)

    #app是否已安装
    def is_app_installed(self,pkg):
        installed = False
        #cmd = "pm list packages -3 %s" % pkg
        cmd = "pm list packages"
        stdout = self.shell(cmd)
        for package in stdout.splitlines():
            apk_install_re = re.compile(r"^package:%s$" % pkg)
            if apk_install_re.findall(package):
                installed = True
                break
        return installed

    #停止app并清除数据
    def stop_and_clear(self,pkg):
        self.force_stop(pkg)
        self.clear(pkg)

    #停止app
    def force_stop(self,pkg):
        cmd = "am force-stop %s" % pkg
        self.shell(cmd)

    #清除数据
    def clear(self,pkg):
        cmd = "pm clear %s" % pkg
        self.shell(cmd)

    #创建目录
    def mkdir(self,path):
        cmd = "mkdir -p %s" % path
        self.shell(cmd)

    #删除文件
    def rimraf(self,path):
        cmd = "rm %s" % path
        self.shell(cmd)

    #卸载app
    def uninstall_app(self,pkg):
        self.force_stop(pkg)
        cmd = "uninstall %s" % pkg
        stdout = self.adb(cmd)
        stdout = stdout.strip()
        if stdout.find("Success") != -1:
            return True
        else:
            msg = "App was not uninstalled,maybe it wasn't on device?'"
            raise Exception(msg)

    #安装app
    def install_remote(self,remoteApk):
        cmd = "pm install -r %s" % remoteApk
        stdout = self.shell(cmd)
        if stdout.find("Success") != -1:
            return True
        else:
            msg = "Remote install failed: %s" % stdout
            raise Exception(msg)

    #启动app
    def start_app(self,pkg,act,retry=True):
        if not pkg or not act:
            msg = "Parameter 'appPackage' and 'appActivity' is required for lunching application"
            raise Exception(msg)

        cmd = "am start -n %s/%s" % (pkg,act)

        try:
            stdout = self.shell(cmd)
        except Exception,ex:
            if retry:
                self.start_app(pkg,act,False)
            else:
                msg = ex
                raise Exception(msg)
        return True

    #等待Activity启动
    def wait_for_activity(self,pkg,act,waitSec=20):
        if self.wait_for_activity_or_not(pkg,act,False,waitSec):
            return True

    #等待Activity停止
    def wait_for_not_activity(self,pkg,act,waitSec=20):
        if self.wait_for_activity_or_not(pkg,act,True,waitSec):
            return True

    #等待app打开或关闭
    def wait_for_activity_or_not(self,pkg,act,flag,waitSec=20):
        if not pkg:
            msg = "Package must not be null"
            raise Exception(msg)
        sec = 0.75
        end_at = time.time() + waitSec

        def check_for_activity(foundPkg,foundAct):
            foundActivity = False
            if foundPkg == pkg:
                for activity in act.split(","):
                    activity = activity.strip()
                    if activity == foundAct or foundAct.find(activity) != -1:
                        foundActivity = True
            return foundActivity

        def wait():
            foundPkg,foundAct = self.get_focused_package_and_activity() 
            foundActivity = check_for_activity(foundPkg,foundAct)
            if (not flag and foundAct) or (flag and not foundAct):
                return True
            elif time.time() < end_at:
                time.sleep(sec)
                return wait()
            else:
                if flag:
                    verb = "stoped"
                else:
                    verb = "started"
                msg = "%s/%s never %s.Current: %s/%s" % (pkg,activity,verb,foundPkg,foundAct)
                raise Exception(msg)
        return wait()

    #获取当前界面应用的package和activity
    def get_focused_package_and_activity(self):
        package = ""
        activity = ""
        if platform.system() is "Windows":
            cmd = "dumpsys window windows | findstr name="
        else:
            cmd = "dumpsys window windows | grep name="
        searchRe = re.compile(r"[a-zA-Z0-9\.]+/.[a-zA-Z0-9\.]+")
        stdout = self.shell(cmd)
        foundMatch = searchRe.findall(stdout)
        if len(foundMatch) > 0:
            foundMatch = foundMatch[0].split("/")
            package = foundMatch[0]
            activity = foundMatch[1]
        return package,activity

    #是否打开wifi
    def wifi_on(self):
        cmd = "settings get global wifi_on"
        stdout = self.shell(cmd)
        if int(stdout) == 0:
            return False
        else:
            return True

    #是否打开飞行模式
    def airplane_mode_on(self):
        cmd = "settings get global airplane_mode_on"
        stdout = self.shell(cmd)
        if int(stdout) == 0:
            return False
        else:
            return True

    #打开/关闭飞行模式并广播
    # flag: 1 (to turn on) or 0 (to turn off)
    def set_airplane_mode_on_or_off(self,flag):
        if int(flag) > 1 or int(flag) < 0:
            msg = "Parameter out range"
            raise Exception(msg)
        cmd = "settings put global airplane_mode_on %s" % int(flag)
        self.shell(cmd)
        self._broadcast_airplane_mode(flag)

    #是否打开软键盘
    def soft_keyboard_present(self):
        cmd = "dumpsys input_method"
        stdout = self.shell(cmd)
        keyboardShownRe = re.compile(r"mInputShown=\w+")
        keyboardShown = keyboardShownRe.findall(stdout)
        if keyboardShown:
            if keyboardShown[0].split("=")[1] == "true":
                return True
            else:
                return False
        else:
            return False

    #点亮屏幕
    def set_screen_on(self):
        if not self._is_screen_on_fully():
            cmd = "input keyevent 26" 
            self.shell(cmd)




    #private

    #是否点亮屏幕
    def _is_screen_on_fully(self):
        cmd = "dumpsys window"
        stdout = self.shell(cmd)
        screenOnFullyRe = re.compile(r"mScreenOnFully=\w+")
        screenOnFully = screenOnFullyRe.findall(stdout)
        if screenOnFully:
            if screenOnFully[0].split("=")[1] == "true":
                return True
            else:
                return False
        else:
            return False

    #广播飞行模式
    # flag: 1 (to turn on) or 0 (to turn off)
    def _broadcast_airplane_mode(self,flag):
        if int(flag) > 1 or int(flag) < 0:
            msg = "Parameter out range"
            raise Exception(msg)
        else:
            if int(flag) == 1:
                on = "true"
            else:
                on = "false"
        cmd = "am broadcast -a android.intent.action.AIRPLANE_HOME --ez state %s" % on
        self.shell(cmd)

    def _get_api_level(self):
        return self.shell("getprop ro.build.version.sdk")

    #安装解锁应用
    def _push_unlock(self):
        path = os.path.abspath(os.path.join(os.path.dirname(__file__),os.path.pardir,"build","unlock_apk","unlock.apk"))
        #unlockPath = os.path.join(os.getcwd(),"build","unlock_apk","unlock.apk")
        unlockPath = os.path.join(path)
        self.install_apk(unlockPath)

    #安装输入法
    def _push_ime(self):
        path = os.path.abspath(os.path.join(os.path.dirname(__file__),os.path.pardir,"build","ime_apk","MaticvKeyBoard.apk"))
        imePath = os.path.join(path)
        self.install_apk(imePath)
        
    #是否锁屏
    def _is_screen_locked(self):
        screenLocked = None
        samsungNoteUnlocked = None
        gbScreenLocked = None
        cmd = "dumpsys window"
        stdout = self.shell(cmd)
        screenLockedRe = re.compile(r"mShowingLockscreen=\w+")
        screenLocked = screenLockedRe.findall(stdout)
        samsungNoteUnlockedRe = re.compile(r"mScreenOnFully=\w+")
        samsungNoteUnlocked = samsungNoteUnlockedRe.findall(stdout)
        gbScreenLockedRe = re.compile(r"mCurrentFocus.+Keyguard")
        gbScreenLocked = gbScreenLockedRe.findall(stdout)
        if screenLocked:
            if screenLocked[0].split("=")[1] == "false":
                return False
            else:
                return True
        elif gbScreenLocked:
            return True
        elif samsungNoteUnlocked:
            if samsungNoteUnlocked[0].split("=")[1] == "true":
                return False
            else:
                return True
        else:
            return False

    def _check_adb_connection_is_up(self):
        stdout = self.shell("echo 'ready'")
        if stdout.find("ready") == 0:
            return True
        else:
            msg = "ADB ping failed,return: %s" % stdout
            raise Exception(msg)

    def _set_device_id(self,deviceId):
        gl.ADB_CMD += " -s %s" % deviceId

    #重启adb
    def _restart_adb(self):
        def restart():
            self.adb("kill-server")
            self.adb("start-server")
        for i in range(3):
            try:
                restart()
                break
            except Exception,ex:
                if i < 3:
                    continue
                else:
                    msg = ex
                    raise Exception(msg)

    def _get_sdk_binary_present(self,binary):
        if platform.system() is "Windows":
            if binary[-4:].find(".exe") == -1:
                binary += ".exe"
        #print os.path.abspath(os.path.join(os.path.dirname(__file__),os.path.pardir))
        path = os.path.abspath(os.path.join(os.path.dirname(__file__),os.path.pardir,"build","platform-tools",binary))
        #return os.path.join(os.getcwd(),"build","platform-tools",binary)
        return path

    def _is_device_connected(self):
        devices = self._get_connected_devices()
        if devices == []:
            msg = "0 device(s) connected"
            raise Exception(msg)
        return devices

    def _get_connected_devices(self):
        stdout = self.adb("devices")
        devices = []
        stdout = stdout.split("\n")
        for line in stdout:
            if line.strip() and line.find("List of devices") == -1 and line.find("* daemon") == -1 and line.find("offline") == -1:
                lineinfo = line.split("\t")
                devices.append({"udid":lineinfo[0],"state":lineinfo[1]})
        return devices


