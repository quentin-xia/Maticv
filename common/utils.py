#/usr/bin/env python
#-*- coding:utf-8 -*-
import math,os
import numpy as np
from adb import Adb
from screencap import MinicapStream
import tempfile
import hashlib
import gl
import platform
if platform.system() is "Windows":
    try:
        import maticv.common.opencv.x32.cv2 as cv2
    except:
        import maticv.common.opencv.x64.cv2 as cv2
else:
    import maticv.common.opencv.linux.cv2 as cv2

class Utils(Adb):
    def __init__(self):
        pass
        #super(Utils,self).__init__()

    #旋转图片函数
    def rotate_about_center(self,src,angle=90,scale=1.0):
        w,h = src.shape[1::-1]
        rangle = np.deg2rad(angle)
        nw = (abs(np.sin(rangle)*h) + abs(np.cos(rangle)*w))*scale
        nh = (abs(np.cos(rangle)*h) + abs(np.sin(rangle)*w))*scale
        rot_mat = cv2.getRotationMatrix2D((nw*0.5, nh*0.5), angle, scale)
        rot_move = np.dot(rot_mat, np.array([(nw-w)*0.5, (nh-h)*0.5,0]))
        rot_mat[0,2] += rot_move[0]
        rot_mat[1,2] += rot_move[1]
        return cv2.warpAffine(src, rot_mat, (int(math.ceil(nw)), int(math.ceil(nh))), flags=cv2.INTER_LANCZOS4)

    #获取矩形坐标
    def get_rectangle_point(self,strX,strY,endX,endY,rate):
        if strX > endX:
            x1,x2 = endX,strX
        else:
            x1,x2 = strX,endX

        if strY > endY:
            y1,y2 = endY,strY
        else:
            y1,y2 = strY,endY

        if rate:
            x1 = self.reduction_point(x1,rate)
            x2 = self.reduction_point(x2,rate)
            y1 = self.reduction_point(y1,rate)
            y2 = self.reduction_point(y2,rate)
        return x1,y1,x2,y2

    #获取目标位置坐标
    def get_circle_point(self,strX,strY,endX,endY,width=0,window=0):
        centerX = int((endX - strX) / 2) + strX
        centerY = int((endY - strY) / 2) + strY
        if window:
            centerX = centerY
            centerY = int((endX - strX) / 2) + (width - endX)
        return centerX,centerY

    #根据比例还原坐标
    def reduction_point(self,point,rate):
        return int(round(point * (1 / float(rate))))

    #根据比例缩小图片
    def zoom(self,image,rate):
        return cv2.resize(image,None,fx=rate,fy=rate,interpolation=cv2.INTER_AREA)

    #生成文件名
    def get_img_name(self,project):
        path = tempfile.mktemp(".png","%s_" % project,"projects/%s" % project)
        path = path.replace("\\","/")
        return path


    #截屏
    def screenshot(self):
        #self.shell("screencap -p /sdcard/screenshot.png")
        #self.pull("/sdcard/screenshot.png",gl.TEMP_IMAGE_PATH)
        screencap = MinicapStream()
        screencap.ReadImageStream(gl.TEMP_IMAGE_PATH)

    #安装app
    def install_app_for_test(self,apk=None,pkg=None,clr=True):
        if apk:
            installed = self.is_app_installed(pkg)
            remoteApk = self._remote_apk_is_exists(apk)
            if installed and remoteApk:
                self._reset_app(pkg,clr)
            else:
                self._mk_remote_dir()
                remoteApk,md5 = self._get_remote_path(apk)
                #print remoteApk,md5
                self._remove_temp_apks(md5)
                self._install_remote_with_retry(remoteApk,pkg,apk)
        else:
            self._reset_app(pkg,clr)



    #private

    #安装app
    def _install_remote_with_retry(self,remoteApk,pkg,localApk):
        installed = self.is_app_installed(pkg)
        if installed:
            self.uninstall_app(pkg)
        print "Install APK should to wait for a few minutes."
        self.push(localApk,remoteApk)
        self.install_remote(remoteApk)

    #删除app安装包
    def _remove_temp_apks(self,md5):
        remoteTempPath = self._remote_temp_path()
        cmd = "ls %s*.apk" % remoteTempPath
        try:
            stdout = self.shell(cmd)
            if "No such file" in stdout:
                apks = []
            else:
                apks = stdout.split("\n")
        except:
            if len(apks) < 1:
                #print "No apks to examine"
                return False

        noMd5Matched = True
        for path in apks:
            path = path.strip()
            if path != "":
                noMd5Matched = True
                if not md5 in path:
                    noMd5Matched = False
                if noMd5Matched:
                    filePath = remoteTempPath + path
                    self.rimraf(filePath)

    #手机上创建临时目录
    def _mk_remote_dir(self):
        path = self._remote_temp_path()
        self.mkdir(path)

    #重置app
    def _reset_app(self,pkg,clr):
        if clr:
            self.stop_and_clear(pkg)
        else:
            self.force_stop(pkg)

    #手机上是否存在安装包
    def _remote_apk_is_exists(self,apk):
        remoteApk,appMd5Hash = self._get_remote_path(apk)
        cmd = "ls %s" % remoteApk
        stdout = self.shell(cmd)
        if not "No such file" in stdout:
            return stdout.strip()
        else:
            return False

    #获取apk路径和md5
    def _get_remote_path(self,apk):
        appMd5 = self._get_md5(apk)
        remoteTempPath = self._remote_temp_path()
        remoteApk = "%s%s.apk" % (remoteTempPath,appMd5)
        return remoteApk,appMd5

    #手机临时目录
    def _remote_temp_path(self):
        return "/data/local/tmp/"

    #获取md5
    def _get_md5(self,apk):
        appMd5Hash = self._get_app_md5(apk)
        appMd5 = "%s%s%s" % (appMd5Hash[0],appMd5Hash,appMd5Hash[-1])
        return appMd5
        
    #获取app md5
    def _get_app_md5(self,apk):
        app = None
        ret = False
        strMd5 = ""
        try:
            app = open(apk,"rb")
            md5 = hashlib.md5()
            strRead = ""
            while True:
                strRead = app.read(8096)
                if not strRead:
                    break
                md5.update(strRead)
            ret = True
            strMd5 = md5.hexdigest()
        except Exception,ex:
            #print ex
            ret = False
        finally:
            if app:
                app.close()
        return strMd5


