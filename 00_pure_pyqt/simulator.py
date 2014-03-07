#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt4.QtGui import *
from PyQt4.QtCore import *

class MyLink(QGraphicsLineItem):
    def __init__(self, startItem, endItem, parent = None, scene = None):
        super(MyLink, self).__init__(parent, scene)

        self.linkHead = QPolygonF()

        self.myStartItem = startItem
        self.myEndItem = endItem
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setPen( QPen( Qt.black, 2 ) )

    def startItem(self):
        return self.myStartItem

    def endItem(self):
        return self.myEndItem

    def boundingRect(self):
        extra = (self.pen().width() + 10) / 2.0
        p1 = self.line().p1()
        p2 = self.line().p2()
        return QRectF(p1, QSizeF(p2.x() - p1.x(), p2.y() - p1.y())).normalized().adjusted(-extra, -extra, extra, extra)

    def paint(self, painter, option, widget = None):
        if self.myStartItem.collidesWithItem(self.myEndItem):
            return

        painter.setPen( self.pen() )
        painter.setBrush( Qt.black )
        centerLine = QLineF(self.myStartItem.pos(), self.myEndItem.pos())
        
        self.setLine( centerLine )
        line = self.line()
        painter.drawLine(line)

    def updatePosition(self):
        line = QLineF( self.mapFromItem( self.myStartItem, 0, 0 ), self.mapFromItem( self.myEndItem, 0, 0) )
        self.setLine( line )
       
        

class MyItem(QGraphicsPolygonItem):
    Node, Line, Text = range(3)

    def __init__(self, itemType, parent=None, scene=None):
        super(MyItem, self).__init__(parent, scene)

        self.itemType = itemType

        self.links = []

        #path = QPainterPath()

        if (itemType == self.Node) : 
            self.myPolygon = QPolygonF( [
                QPointF(-50, -25), QPointF(50, -25), 
                QPointF(50, 25), QPointF(-50, 25), 
                QPointF(-50, -25) ] )
            self.setPolygon(self.myPolygon)
        else :
            print "itemType = {0}".format(itemType)

        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)

    def addLink(self, link):
        self.links.append(link)

    def removeLink(self, link):
        try:
            self.links.remove(link)
        except ValueError:
            print "MyItem Remove Link Value Error"
            pass

    def removeLinks(self):
        for link in self.links[:]:
            link.startItem().removeLink(link)
            link.endItem().removeLink(link)
            self.scene().removeItem(link)


class MyScene(QGraphicsScene):
    InsertNode, InsertLine, MoveItem = range(3)
    
    itemInserted = pyqtSignal(MyItem)
    itemSelected = pyqtSignal(QGraphicsItem)

    line = None

    def __init__(self, parent = None):
        super(MyScene, self).__init__(parent)
        self.myMode = self.MoveItem

    def setMode(self, mode):        
        self.myMode = mode
        print "MyScene mode = {0}".format(mode)

    def mousePressEvent(self, mouseEvent):
        if (mouseEvent.button() != Qt.LeftButton):
            return

        if (self.myMode == self.InsertNode):
            item = MyItem( MyItem.Node )
            item.setBrush( Qt.white )
            self.addItem( item )
            item.setPos( mouseEvent.scenePos() )
            self.itemInserted.emit(item)
            self.setMode( MyScene.MoveItem )
            print "Insert Item Mode"
        
        elif (self.myMode == self.InsertLine):
            self.line = QGraphicsLineItem( QLineF( mouseEvent.scenePos(), mouseEvent.scenePos() ) )
            self.line.setPen( QPen( Qt.black, 2 ) )
            self.addItem( self.line )
            print "Insert Line Mode"

        elif (self.myMode == self.MoveItem):
            print "Move Item Mode"

        super(MyScene, self).mousePressEvent(mouseEvent)

    def mouseMoveEvent(self, mouseEvent):
        if (self.myMode == MyScene.InsertLine) and self.line :
            newline = QLineF( self.line.line().p1(), mouseEvent.scenePos() )
            self.line.setLine( newline )
        else :
            super(MyScene, self).mouseMoveEvent(mouseEvent) # 要把mouseMoveEvent還給上層

    def mouseReleaseEvent(self, mouseEvent):
        if self.line and (self.myMode == MyScene.InsertLine) :
            startItems = self.items(self.line.line().p1())
            if len(startItems) and (startItems[0] == self.line) :
                startItems.pop(0)

            endItems = self.items(self.line.line().p2())
            if len(endItems) and (endItems[0] == self.line):
                endItems.pop(0)

            self.removeItem(self.line)
            self.line = None

            if len(startItems) and len(endItems) and \
                    isinstance( startItems[0], MyItem ) and \
                    isinstance( endItems[0], MyItem) and \
                    startItems[0] != endItems[0] :
                startItem = startItems[0]
                endItem = endItems[0]
                link = MyLink(startItem, endItem)
                startItem.addLink(link)
                endItem.addLink(link)
                self.addItem(link)
                link.updatePosition()
                link.setZValue(-1000.0)

        self.line = None
        self.setMode( MyScene.MoveItem )
        super(MyScene, self).mouseReleaseEvent(mouseEvent)


class MyMainWindow(QMainWindow):   
    NodeButton, LinkButton, TextButton = range(3)    

    def buttonGroupClicked(self, id):
        if ( id == self.NodeButton ):
            self.scene.setMode( MyScene.InsertNode )
        elif ( id == self.LinkButton ):
            self.scene.setMode( MyScene.InsertLine )
        else :
            self.scene.setMode( MyScene.MoveItem )

        print "Button [{0}] clicked".format(id)

    def createMenus(self):
        self.fileMenu  = self.menuBar().addMenu("&File")
        self.itemMenu  = self.menuBar().addMenu("&Item")
        self.aboutMenu = self.menuBar().addMenu("&About")    

    def createToolBox(self):
        # 設定 button group
        self.buttonGroup = QButtonGroup()
        self.buttonGroup.setExclusive(False)
        self.buttonGroup.buttonClicked[int].connect(self.buttonGroupClicked)        

        # group 1 : items (node, link, text)
        itemLayout = QGridLayout()
        nodeButton = QPushButton("Node")
        linkButton = QPushButton("Link")
        textButton = QPushButton("Text")
        itemLayout.addWidget(nodeButton, 0, 0)
        itemLayout.addWidget(linkButton, 0, 1)
        itemLayout.addWidget(textButton, 1, 0)
        itemLayout.setRowStretch(2, 1)
        itemLayout.setColumnStretch(2, 1)
        itemWidget = QWidget()
        itemWidget.setLayout(itemLayout)

        self.buttonGroup.addButton(nodeButton, self.NodeButton)
        self.buttonGroup.addButton(linkButton, self.LinkButton)
        self.buttonGroup.addButton(textButton, self.TextButton)

        # group 2 : background grid(blue, white, gray, none)
        backgroundLayout = QGridLayout()
        blueButton = QPushButton("Blue Grid")
        whiteButton = QPushButton("White Grid")
        grayButton = QPushButton("Gray Grid")
        noneButton = QPushButton("None Grid")
        backgroundLayout.addWidget( blueButton, 0, 0 )
        backgroundLayout.addWidget( whiteButton, 0, 1 )
        backgroundLayout.addWidget( grayButton, 1, 0 )
        backgroundLayout.addWidget( noneButton, 1, 1 )
        backgroundLayout.setRowStretch(2, 1)
        backgroundLayout.setColumnStretch(2, 1)
        backgroundWidget = QWidget()
        backgroundWidget.setLayout( backgroundLayout )

        self.buttonGroup.addButton(blueButton, 3)
        self.buttonGroup.addButton(whiteButton, 4)
        self.buttonGroup.addButton(grayButton, 5)
        self.buttonGroup.addButton(noneButton, 6)

        self.toolBox = QToolBox()
        self.toolBox.setSizePolicy( QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Ignored) )
        self.toolBox.setMinimumWidth( itemWidget.sizeHint().width() )
        self.toolBox.addItem( itemWidget, "Item Group" )
        self.toolBox.addItem( backgroundWidget, "Background Group" )
    
    def createView(self):
        # 設定 graphics view & scene
        self.scene = MyScene()
        self.scene.setSceneRect( QRectF(0, 0, 5000, 5000) )
        self.view = QGraphicsView( self.scene )

    def __init__(self):
        super(MyMainWindow, self).__init__()

        self.createMenus()
        self.createToolBox()
        self.createView()

        # 設定主要的 layout
        mainLayout = QHBoxLayout()
        mainLayout.addWidget( self.toolBox )
        mainLayout.addWidget( self.view )

        # 設定主要的 widget
        self.widget = QWidget()
        self.widget.setLayout( mainLayout )
        self.setCentralWidget( self.widget )

        # 設定 window 出現的位置跟大小 : setGeometry(左、上、寬、高）
        self.setGeometry(100, 100, 800, 500)
        # 設定 window title
        self.setWindowTitle("Simulator")



if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
   
    window = MyMainWindow()
    window.show()

    sys.exit( app.exec_() )    

