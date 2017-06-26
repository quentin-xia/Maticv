#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os,socket,tempfile,time

try:
    import http.client as httplib
    from urllib import request as url_request
except ImportError: #above is available in py3+,below is py2.7
    import httplib as httplib
    import urllib as url_request

#配置app
def configure_app(app):
    if app[:4].lower() == "http":
        tmpDir = tmpfile.mkdtemp()
        randNum = str(time.time().replace(".",""))
        tmpPath = os.path.join(tmpDir,randNum + ".apk")
        configure_downloaded_app(app,tmpPath)
        return tmpPath
    else:
        configure_local_app(app)
        return app

#本地app
def configure_local_app(app):
    ext = app[-4:].lower()
    if ext == ".apk":
        if not os.path.exists(app):
            msg = "App is not exists: %s" % app
            raise Exception(msg)
    else:
        msg = "Using local app,but didn't end in .apk"
        raise Exception(msg)

#下载app
def configure_downloaded_app(app,path):
    ext = app[-4:].lower()
    if ext == ".apk":
        down_load_app(app,path)
        if os.path.getsize(path) < 1024:
            msg = "Failed downloading app from app URL(%s)" % app
            raise Exception(msg)
    else:
        msg = "App URL(%s) didn't sem to point to a .apk file" % app
        raise Exception(msg)

#下载
def download_app(app,path):
    try:
        #set urllib timeout
        socket.setdefaulttimeout(600)
        url_request.urlretrieve(app,path)
    except:
        msg = "Failed downloading app from app URL(%s)" % app
        raise Exception(msg)
