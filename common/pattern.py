#/usr/bin/env python
#-*- coding:utf-8 -*-
import os,time
from utils import Utils
from match import Match
#from action import Action
import gl
import platform
if platform.system() is "Windows":
    try:
        import maticv.common.opencv.x32.cv2 as cv2
    except:
        import maticv.common.opencv.x64.cv2 as cv2
else:
    import maticv.common.opencv.linux.cv2 as cv2

class Pattern(Utils):
    def __init__(self,pattern=None,timeout=5):
        super(Pattern,self).__init__()
        if pattern:
            if os.path.exists(pattern):
                self.pattern = pattern
            else:
                msg = "Image not found"
                raise Exception(msg)
        else:
            msg = "Pattern can be none"
            raise Exception(msg)
        if float(timeout) <= 0: 
            self.timeout = 5
        else:
            self.timeout = timeout
        self.screenshot()
        self.centerX,self.centerY = self._find()


    """
    相似度
    
    Args:
        - similar: 相似度（0-1）
    """
    def similar(self,similar):
        if similar:
            if 0 < float(similar) <= 1:
                self.centerX,self.centerY = self._find(similar)
            else:
                msg = "Similar out of range"
                raise Exception(msg)
        else:
            msg = "Similar can not be none"
            raise Exception(msg)
        return self


    """
    偏移值

    Args:
        - x: x轴偏移值(中心点开始)
        - y: y轴偏移值(中心点开始)
    """
    def target_offset(self,x,y):
        if self.centerX and self.centerY:
            if x and y:
                self.centerX += int(x)
                self.centerY += int(y)
            else:
                msg = "Target offset x,y can not be none"
                raise Exception(msg)
        return self
            
    #获取坐标
    def get_coordinate(self):
        """
        if not self.centerX or not self.centerY:
            msg = "Can not find image on the screen"
            raise Exception(msg)
        """
        return self.centerX,self.centerY

    #判断是否匹配到
    def exists(self):
        if not self.centerX or not self.centerY:
            return False
        else:
            return True

    #private
    #图像匹配
    def _find(self,similar=0.7):
        match = Match()
        pattern = cv2.imread(self.pattern,0)
        endTime = time.time() + self.timeout
        while True:
            try:
                screen = cv2.imread(gl.TEMP_IMAGE_PATH,0)
                res = match.find(pattern,screen,similar)
            except:
                if time.time() < endTime:
                    self.screenshot()
                    continue
                else:
                    self.centerX = None
                    self.centerY = None
                    return self.centerX,self.centerY
            if res:
                return self._get_center_point(res)
            else:
                if time.time() < endTime:
                    self.screenshot()
                else:
                    self.centerX = None
                    self.centerY = None
                    return self.centerX,self.centerY
                    #msg = "can not find image on the screen"
                    #raise Exception(msg)

    #获取中心点
    def _get_center_point(self,rectangle):
        centerX = int((rectangle[2] - rectangle[0]) / 2) + rectangle[0]
        centerY = int((rectangle[3] - rectangle[1]) / 2) + rectangle[1]
        if gl.WINDOW:
            tmpX = centerX
            tmpY = centerY
            if gl.WINDOW == 1:
                centerX = tmpY
                centerY = gl.MOBILE_WIDTH - tmpX
            elif gl.WINDOW == 2:
                centerX = gl.MOBILE_WIDTH - tmpX
                centerY = gl.MOBILE_HEIGHT - tmpY
                #print gl.MOBILE_WIDTH
                #print gl.MOBILE_HEIGHT
                #print centerX
                #print centerY
            elif gl.WINDOW == 3:
                centerX = gl.MOBILE_HEIGHT - tmpY
                centerY = tmpX
        return centerX,centerY
     
