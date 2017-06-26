#/usr/bin/env python
#-*- coding:utf-8 -*-

from adb import Adb
import gl
import keys
import platform

class Action(Adb):
    """
    send keyevent

    :Args:
        - keycode: keyevent code
          http://developer.android.com/reference/android/view/KeyEvent.html
    """
    def keyevent(self,keycode):
        cmd = "input keyevent %s" % keycode
        self.shell(cmd)


    """
    Tap at given coordinates

    :Args:
        - x: X coordinate to tap
        - y: Y coordinate to tap
    """
    def tap(self,x,y):
        cmd = "input tap %s %s" % (x,y)
        self.shell(cmd)


    """
    Tap at coordinates by ratio

    :Args:
        - ratioX: X ratio
        - ratioY: Y ratio
    """
    def tap_by_ratio(self,ratioX,ratioY):
        x,y = self._get_coord(ratioX,ratioY)
        self.tap(x,y)

    
    """
    Swipe

    :Args:
        - startX: X start coordinate
        - startY: Y start coordinate
        - endX: X end coordinate
        - endY: Y end coordinate
        - duration: android >= 4.4 can use opt duration(ms)
    """
    def swipe(self,startX,startY,endX,endY,duration=None):
        if duration:
            duration = int(duration)
        else:
            duration = ""
        cmd = "input swipe %s %s %s %s %s" % (startX,startY,endX,endY,duration)
        self.shell(cmd)


    """
    Swipe by ratio

    :Args:
        - startRatioX: start X ratio
        - startRatioY: start Y ratio
        - endRatioX: end X ratio
        - endRatioY: end Y ratio
        - duration: android >= 4.4 can use opt duration(ms)
    """
    def swipe_by_ratio(self,startRatioX,startRatioY,endRatioX,endRatioY,duration=None):
        startX,startY = self._get_coord(startRatioX,startRatioY)
        endX,endY = self._get_coord(endRatioX,endRatioY)
        self.swipe(startX,startY,endX,endY,duration)


    """
    Swipe to left
    """
    def swipe_to_left(self):
        self.swipe_by_ratio(0.9,0.5,0.1,0.5)


    """
    Swipe to right
    """
    def swipe_to_right(self):
        self.swipe_by_ratio(0.1,0.5,0.9,0.5)


    """
    Swipe to up
    """
    def swipe_to_up(self):
        self.swipe_by_ratio(0.5,0.9,0.5,0.1)


    """
    Swipe to down
    """
    def swipe_to_down(self):
        self.swipe_by_ratio(0.5,0.1,0.5,0.9)


    """
    Input text
    """
    def send_text(self,text):
        if text:
            text = self._text_encode(text)
            #cmd = "input text \"%s\"" % text
            cmd = "am broadcast -a MATICV_INPUT_TEXT --es msg '%s'" % text
            self.shell(cmd)

    """
    Send editor code

    Code 1:   actionNext    软键盘不关闭，光标跳到下一个输入焦点位置（发送EditorInfo.IME_ACTION_NEXT命令）
    Code 2:   actionGo      软键盘不关闭，光标跳到下一个输入焦点位置，发送EditorInfo.IME_ACTION_GO命令
    Code 3:   actionSearch  软键盘不关闭，发送EditorInfo.IME_ACTION_SEARCH命令
    Code 4:   actionSend    软键盘关闭，发送EditorInfo.IME_ACTION_SEND命令
    Code 5:   actionDone    软键盘关闭，光标保持在原来的输入框上，发送EditorInfo.IME_ACTION_DONE命令
    """
    def send_editor_code(self,code):
        code = int(code)
        cmd = "am broadcast -a MATICV_EDITOR_CODE --ei code %s" % code
        self.shell(cmd)


    """
    Pressing the back button
    """
    def back(self):
        self.keyevent(keys.BACK)


    """
    Pressing the home button
    """
    def home(self):
        self.keyevent(keys.HOME)


    """
    Pressing the menu button
    """
    def menu(self):
        self.keyevent(keys.MENU)


    """
    Pressing the volume up button
    """
    def volume_up(self):
        self.keyevent(keys.VOLUME_UP)


    """
    Pressing the volume down button
    """
    def volume_down(self):
        self.keyevent(keys.VOLUME_DOWN)



    #private

    #根据比例获取坐标
    def _get_coord(self,ratioX,ratioY):
        if (1 >= float(ratioX) >= 0) and (1 >= float(ratioY) >= 0):
            if gl.WINDOW == 1 or gl.WINDOW == 3:
                x = ratioX * gl.MOBILE_HEIGHT
                y = ratioY * gl.MOBILE_WIDTH
            else:
                x = ratioX * gl.MOBILE_WIDTH
                y = ratioY * gl.MOBILE_HEIGHT
            return x,y
        else:
            msg = "Ratio can not > 1 and < 0"
            raise Exception(msg)

    #编码转换
    def _text_encode(self,text):
        text = text.decode("utf-8").encode("unicode-escape")
        if not (platform.system() is "Windows"):
            text = text.replace("\\","\\\\")
        return text

