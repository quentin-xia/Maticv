#!/usr/bin/env python
# -*- coding: utf-8 -*-

from action import Action
import gl

class Region(object):
    def __init__(self):
        #super(Region,self).__init__()
        pass

    """
    判断是否匹配到
    Args:
        - patternObject: pattern object
    """
    def exists(self,patternObject):
        return patternObject.exists()

    def wait(self,patternObject):
        x,y = patternObject.get_coordinate()
        if not x or not y:
            msg = "Can not find image on the screen"
            raise Exception(msg)
        else:
            return x,y

    """
    点击
    Args:
        - patternObject: pattern object
    """
    def click(self,patternObject):
        x,y = self.wait(patternObject)
        Action().tap(x,y)

    """
    根据坐标点击
    Args:
        - x: X coordinate to tap
        - y: Y coordinate to tap
    """
    def click_by_coordinate(self,x,y):
        if x and y:
            x = int(x)
            y = int(y)
            Action().tap(x,y)
        else:
            msg = "Coordinate x,y can not be none"
            raise Exception(msg)

    """
    根据屏幕比例点击
    Args:
        - ratioX: X ratio
        - ratioY: Y ratio
    """
    def click_by_ratio(self,ratioX,ratioY):
        Action().tap_by_ratio(ratioX,ratioY)


    """
    拖放
    Args:
        - patternObjectA: pattern object (drag)
        - patternObjectB: pattern object (drop)
        - duration: android >= 4.4 can use opt duration(ms)
    """
    def swipe(self,patternObjectA,patternObjectB,duration=None):
        bx,by = self.wait(patternObjectA)
        ex,ey = self.wait(patternObjectB)
        Action().swipe(bx,by,ex,ey,duration)


    """
    拖放到坐标
    Args:
        - patternObject: pattern object (drag)
        - x: X coordinate (drop)
        - y: Y coordinate (drop)
        - duration: android >= 4.4 can use opt duration(ms)
    """
    def swipe_to_coordinate(self,patternObject,x,y,duration=None):
        bx,by = self.wait(patternObject)
        ex = int(x)
        ey = int(y)
        if not ex or not ey:
            msg = "x,y can not be none"
            raise Exception(msg)
        Action().swipe(bx,by,ex,ey,duration)

    """
    从坐标拖放到指定位置
    Args:
        - x: X coordinate (drag)
        - y: Y coordinate (drag)
        - patternObject: pattern object (drop)
        - duration: android >= 4.4 can use opt duration(ms)
    """
    def swipe_to_pattern(self,x,y,patternObject,duration=None):
        bx = int(x)
        by = int(y)
        ex,ey = self.wait(patternObject)
        if not bx or not by:
            msg = "x,y can not be none"
            raise Exception(msg)
        Action().swipe(bx,by,ex,ey,duration)

    """
    按比例拖放
    Args:
        - startRatioX: start X ratio
        - startRatioY: start Y ratio
        - endRatioX: end X ratio
        - endRatioY: end Y ratio
        - duration: android >= 4.4 can use opt duration(ms)
    """
    def swipe_by_ratio(self,startRatioX,startRatioY,endRatioX,endRatioY,duration=None):
        Action().swipe_by_ratio(startRatioX,startRatioY,endRatioX,endRatioY,duration)


    """
    向左拖放
    """
    def swipe_to_left(self):
        Action().swipe_to_left()

    """
    向右拖放
    """
    def swipe_to_right(self):
        Action().swipe_to_right()

    """
    向上拖放
    """
    def swipe_to_up(self):
        Action().swipe_to_up()

    """
    向下拖放
    """
    def swipe_to_down(self):
        Action().swipe_to_down()


    """
    输入
    Args:
        - patternObject: pattern object
        - text: input text
    """
    def input_text(self,text=None,patternObject=None):
        if patternObject != None:
            self.click(patternObject)
        Action().send_text(str(text))

    """
    Send editor code

    Code 1:  actionNext    软键盘不关闭，光标跳到下一个输入焦点位置（发送EditorInfo.IME_ACTION_NEXT命令）
    Code 2:  actionGo      软键盘不关闭，光标跳到下一个输入焦点位置，发送EditorInfo.IME_ACTION_GO命令
    Code 3:  actionSearch  软键盘不关闭，发送EditorInfo.IME_ACTION_SEARCH命令
    Code 4:  actionSend    软键盘关闭，发送EditorInfo.IME_ACTION_SEND命令
    Code 5:  actionDone    软键盘关闭，光标保持在原来的输入框上，发送EditorInfo.IME_ACTION_DONE命令
    """
    def send_editor_action(self,code):
        code = int(code)
        Action().send_editor_code(code)


    """
    send keyevent
    Args:
        - keycode: keyevent code
        http://developer.android.com/reference/android/view/KeyEvent.html
    """
    def keyevent(self,keycode):
        Action().keyevent(keycode)


    """
    Pressing the back button
    """
    def back(self):
        Action().back()

    """
    Pressing the home button
    """
    def home(self):
        Action().home()

    """
    Pressing the menu button
    """
    def menu(self):
        Action().menu()

    """
    Pressing the volume up button
    """
    def volume_up(self):
        Action().volume_up()

    """
    Pressing the volume down button
    """
    def volume_down(self):
        Action().volume_down()
