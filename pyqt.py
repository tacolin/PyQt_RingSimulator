#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.QtWebKit import *

class MyWidget(QWidget):
    def __init__(self, parent = None):
        super(MyWidget, self).__init__(parent)
        
        self.webview = QWebView()
        verticalLayout = QVBoxLayout()
        verticalLayout.addWidget(self.webview)
        self.setLayout(verticalLayout)
        
        self.frame = self.webview.page().mainFrame()
        self.myComm = MyCommunicator()
        self.frame.addToJavaScriptWindowObject('py_obj', self.myComm)
        
        self.webview.load( QUrl("index.html") )

        
class MyCommunicator(QObject):
    someSignal = pyqtSignal(str)    

    def __init__(self, parent = None):
        super(MyCommunicator, self).__init__(parent)
        
    @pyqtSlot(str)
    def printText(self, text):
        print text
        
    @pyqtSlot()
    def triggerSomething(self):
        self.someSignal.emit("hello from pyqt")
        
        
if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    widget = MyWidget()
    widget.show()
    sys.exit( app.exec_() )