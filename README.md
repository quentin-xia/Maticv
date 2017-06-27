## What is matip? ##
Maticv （mobile application test in opencv） 
Maticv是一个使用“视觉图像匹配”方法来自动化图形用户界面的自动化测试框架。  
Maticv支持Android平台上的各种应用，所有手机屏幕上的元素都被视为一个图像，并存储在项目中。Maticv将基于对作为参数传递的图像进行视觉匹配出发GUI交互。  
Maticv对手游非常有用（对象不具有ID或名称），它在有一个稳定的图形用户界面（如，GUI组建不可变）的情况下是很有用的。

### Actual Use ###
- Maticv可以用来自动化手游，特别是卡牌类手游。
- 它可以运用于自动化基于窗口的应用程序，我们可以自动化我们在手机屏幕上所看到的。
- 大多数的自动化测试工具都不支持手游项目。Maticv提供了广泛的支持。
- Maticv采用强大的“视觉匹配”机制来自动化桌面对象，它通过提取图像特征进行识别，如果发现匹配，将相应的与图像进行交互。

### Supported Python Versions ###
- Python 2.6，2.7

### Supported Systems ###
- Windows XP，Windows 7
- Linux
- Macos

### Installing ###
如果你的系统中已安装 `pip <http://www.pip-installer.org>`，你可以直接安装或更新Maticv  

	pip install -U maticv  

或者，你可以从`PYPI <http://pypi.python.org/pypi/maticv>` 下载源文件，解压并执行setup.py  

	python setup.py install

注：上述两种方法安装maticv需要将python加入环境变量

** 有任何疑问或吐槽请联系: **
- QQ：873334303
- Email：873334303@qq.com
