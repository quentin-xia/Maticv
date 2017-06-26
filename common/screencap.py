#!/usr/bin/env python
#-*- coding: utf-8 -*-

import socket,os,time,struct
from maticv.common.adb import Adb

class MinicapStream:
    def __init__(self):
        self.IP = "127.0.0.1" #定义IP
        self.PORT = 1717 #监听的端口
        self.minicapSocket = None
        self.ReadImageStreamTask = None
        self.adb = Adb()


    #读取图片流并保存图片
    def ReadImageStream(self,filepath):
        #本地端口转发
        #os.system("adb forward tcp:%s localabstract:minicap" % self.PORT)
        cmd = "forward tcp:%s localabstract:minicap" % self.PORT
        self.adb.adb(cmd)
        #启动socket连接
        self.minicapSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM) #定义socket类型，网络通信，TCP
        self.minicapSocket.connect((self.IP,self.PORT))
        readBannerBytes = 0
        bannerLength = 2
        readFrameBytes = 0
        frameBodylength = 0
        dataBody = ""

        #banner信息
        """
        version = 0 #版本信息
        blength = 0 #banner长度
        pid = 0 #进程ID
        realWidth = 0 #设备真实宽度
        realHeight = 0 #设备真实高度
        virtualWidth = 0 #设备虚拟宽度
        virtualHeight = 0 #设备虚拟高度
        orientation = 0 #设备方向
        quirks = 0 #设备信息获取策略
        """

        t = time.time() + 5
        while t > time.time():
            reallen = self.minicapSocket.recv(4096)
            length = len(reallen)
            if not length:
                continue
            cursor = 0
            while cursor < length:
                if readBannerBytes < bannerLength:
                    #打印banner信息
                    """
                    if readBannerBytes == 0:
                        version = self.bytes_to_int(reallen[cursor])
                    elif readBannerBytes == 1:
                        bannerLength = self.bytes_to_int(reallen[cursor])
                        blength = bannerLength
                    elif readBannerBytes in [2,3,4,5]:
                        pid += self.bytes_to_int(reallen[cursor],readBannerBytes - 2) 
                    elif readBannerBytes in [6,7,8,9]:
                        realWidth += self.bytes_to_int(reallen[cursor],readBannerBytes - 6)
                    elif readBannerBytes in [10,11,12,13]:
                        realHeight += self.bytes_to_int(reallen[cursor],readBannerBytes - 10)
                    elif readBannerBytes in [14,15,16,17]:
                        virtualWidth += self.bytes_to_int(reallen[cursor],readBannerBytes - 14)
                    elif readBannerBytes in [18,19,20,21]:
                        virtualHeight += self.bytes_to_int(reallen[cursor],readBannerBytes - 18)
                    elif readBannerBytes == 22:
                        orientation = self.bytes_to_int(reallen[cursor]) * 90
                    elif readBannerBytes == 23:
                        quirks = self.bytes_to_int(reallen[cursor])
                    cursor += 1
                    readBannerBytes += 1
                    if readBannerBytes == bannerLength:
                        print "Banner [Version=%s, length=%s, Pid=%s, realWidth=%s, realHeight=%s, virtualWidth=%s, virtualHeight=%s, orientation=%s, quirks=%s]" % (version,blength,pid,realWidth,realHeight,virtualWidth,virtualHeight,orientation,quirks)
                    """
                    if readBannerBytes == 1:
                        bannerLength = self.bytes_to_int(reallen[cursor])
                    cursor += 1
                    readBannerBytes += 1

                elif readFrameBytes < 4:
                    frameBodylength += self.bytes_to_int(reallen[cursor],readFrameBytes)
                    cursor += 1
                    readFrameBytes += 1
                else:
                    if length - cursor >= frameBodylength: 
                        dataBody += reallen[cursor:(cursor+frameBodylength)]
                        if self.bytes_to_int(dataBody[0])!=0xFF or self.bytes_to_int(dataBody[1])!=0xD8:
                            return False
                        self.save_file(filepath, dataBody)
                        #print "Image saved!"
                        self.minicapSocket.close()
                        return True
                    else:
                        dataBody += reallen[cursor:length] 
                        frameBodylength -= length - cursor;
                        readFrameBytes += length - cursor;
                        cursor = length;
        raise Exception("Server did not start!!!")

    def save_file(self,file_name, data):
        file=open(file_name, "wb")
        file.write(data)
        file.flush()
        file.close()

    def bytes_to_int(self,byte,choice = 0):
        return struct.unpack("<B",byte)[0] << (choice * 8)


