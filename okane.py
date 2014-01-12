'''
Created on Feb 8, 2012

@author: johan
'''
import sys
import os
import transaction
import wx
import random
import wx.html
import Controller
import Model
import View
import TransactionView
import TotalsView
import csv
import Shapes
import logging
import logging.config
import math


logging.basicConfig(level=logging.WARN)
motionlog=logging.getLogger('motion')
motionlog.setLevel("WARN")

eventlog = logging.getLogger('event')
eventlog.setLevel("INFO")
wildcard = "CSV files (*.csv)|*.csv|" \
            "All files (*.*)|*.*"

def calcMouseVelocity(posOld, posNew):
    "Computes the velocity of the mouse"
    dX = posNew[0] - posOld[0]
    dY = posNew[1] - posOld[1]
    motionlog.debug("dX = %s" % (dX))
    motionlog.debug("dY = %s" % (dY))
    angle = math.atan2(dY, dX) + 0.5*math.pi
    speed = 0.05* math.hypot(dX, dY)
    motionlog.debug("Speed = %s, Angle = %s deg" % (speed, math.degrees(angle)))
    if speed*speed < 10:
        return (speed, angle)
    else:
        return (0,0)

class Frame(wx.Frame):
    def __init__(self, parent, title, size=wx.DefaultSize):
        wx.Frame.__init__(self, parent, wx.ID_ANY, title, wx.DefaultPosition, size)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_TIMER, self.OnTimer)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnClick)
        self.Bind(wx.EVT_RIGHT_DOWN, self.OnClick)
        self.Bind(wx.EVT_LEFT_UP, self.OnRelease)
        self.Bind(wx.EVT_RIGHT_UP, self.OnRelease)
        self.Bind(wx.EVT_MOTION, self.OnMotion)
        menuBar = wx.MenuBar()
        menu = wx.Menu()
        m_open = menu.Append(wx.ID_FILE, "O&pen\tAlt-O", "Open file")
        m_exit = menu.Append(wx.ID_EXIT, "E&xit\tAlt-X", "Close window and exit program.")

        menuBar.Append(menu, "&File")
        self.SetMenuBar(menuBar)
        self.statusbar = self.CreateStatusBar()

        # MVC
        # self.controller = Controller.CController()
        # self.model = Model.CModel()
        # self.controller.setModel(self.model)

        # self.totalsView = TotalsView.TotalsView(self, "Category/Totals View", (400, 300))

        # self.totalsView.setModel(self.model)
        # self.controller.setView(self.totalsView)

        #self.transactionView = TransactionView.TransactionView(self, "Transaction View", (400,200))
        #self.transactionView.setModel(self.model)
        #self.controller.setView(self.transactionView)

        # events
        self.Bind(wx.EVT_MENU, self.OnOpen, m_open)
        self.Bind(wx.EVT_MENU, self.OnClose, m_exit)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Bind(wx.EVT_SIZE, self.OnSize)


        #self.Bind(wx.EVT_LEFT_UP, self.OnClick)

        self.transactionList = []
        self.transactionDict = {}
        self.transactionTotals = {}
        self.modelChangedCallbacks = []

        self.shapes = list()
        self.clickedShapes = list()
        self.rightClickedShapes = list()
        self.timer = wx.Timer(self)
        self.timer.Start(100)
        self.shapes = list()
        self.clickedShapes = list()
        self.rightClickedShapes = list()
        self.frameState="NORMAL"
        #self.generateShapes()
        t = transaction.Bucket(pos=(10,10), size=(70,70), amt=0, desc="Bucket", cat="test", droptarget=True)
        #t = Shapes.RandomRect()
        self.shapes.append(t)
 #       t = Rect((0,0), (30,30))
        #t = Shapes.RandomRect()
        #self.shapes.append(t)
        self.lastMovePosition = (0,0)
        self.selectedShape = None

        # layout
        #box = wx.BoxSizer(wx.VERTICAL)
        #box.Add(self.totalsView, wx.EXPAND)
        #box.Add(self.transactionView, wx.EXPAND)
        #self.SetSizer(box)
        #self.Layout()

    def dumpTransactionList(self):
        for t in self.shapes:
            print t

    def openFile(self, fn):
        ifile = open(fn, "rb")
        reader = csv.reader(ifile)
        for row in reader:
            if len(row) > 0 and row[0] == "HIST":
                self.shapes.append(transaction.DrawableTransaction(date=row[1], amt=row[3], cat=row[4], desc=row[5]))
        ifile.close()
        #self.dumpTransactionList()
        #self.createDicts()
        #self.dumpDicts()
        #self.notifyModelChanged()

    def OnClose(self, event):
        dlg = wx.MessageDialog(self,
            "Do you really want to close this application?",
            "Confirm Exit", wx.OK|wx.CANCEL|wx.ICON_QUESTION)
        result = dlg.ShowModal()
        if result == wx.ID_OK:
            self.Destroy()

    def OnOpen(self, event):
        dlg = wx.FileDialog(
            self, message="Choose a file",
            defaultDir=os.getcwd(),
            defaultFile="",
            wildcard=wildcard,
            style=wx.OPEN | wx.MULTIPLE | wx.CHANGE_DIR)
        dlg.ShowModal()

        self.openFile(dlg.GetFilename())

        #self.totalsView.start()
        dlg.Destroy()
        self.Refresh()

    def OnSize(self, event):
        print "ON SIZE"
        hsize = event.GetSize()[0] * 0.75
        self.SetSizeHints(minW=-1, minH=hsize, maxH=hsize)
        self.SetTitle(str(event.GetSize()))
        self.Refresh()

    def isLeftClick(self, e):
        return (e.GetButton() == wx.MOUSE_BTN_LEFT)

    def isRightClick(self, e):
        return (e.GetButton() == wx.MOUSE_BTN_RIGHT)

    def guessSelectedShape(self, e):
        x, y = e.GetPosition()
        if self.isLeftClick(e):
            self.clickedShapes = [s for s in self.shapes if s.contains(x, y)]
            self.clickedShapes.sort(key=lambda shape: shape.zOrder, reverse=True)
            eventlog.info("clickedShapes: %s" % (self.clickedShapes))

            if e.ShiftDown():
                if len(self.clickedShapes) > 1:
                    return self.clickedShapes[1]
            else:
                try:
                    clicked = self.clickedShapes[0]
                    return clicked
                except:
                    for s in self.shapes:
                        s.state = "NORMAL"
                    return None
        if self.isRightClick(e):
            self.rightClickedShapes = [s for s in self.shapes if s.contains(x, y)]
            self.rightClickedShapes.sort(key=lambda shape: shape.zOrder, reverse=True)
            eventlog.info("rightClickedShapes: %s" % (self.rightClickedShapes))
            if e.ShiftDown():
                if len(self.rightClickedShapes) > 1:
                    return self.rightClickedShapes[1]
            else:
                try:
                    clicked = self.rightClickedShapes[0]
                    return clicked
                except:
                    for s in self.shapes:
                        s.state = "NORMAL"
                    return None

    def add(self, s):
        self.shapes.append(t)

    def OnMotion(self, e):
        newX, newY = e.GetPosition()
        if self.frameState == "POSSIBLE_LEFT_DRAG" and e.LeftIsDown():
            self.frameState = self.selectedShape.state = "LEFT_DRAGGING"
        elif self.frameState == "LEFT_DRAGGING" and e.LeftIsDown():
            # or ((self.frameState == "RIGHT_DRAGGING" and e.RightIsDown()):
            oldX, oldY = self.lastMovePosition
            deltaX = newX - oldX
            deltaY = newY - oldY
            self.selectedShape.moveBy(deltaX, deltaY)
        else:
            self.frameState = "MOTION"
            calcMouseVelocity(self.lastMovePosition, (newX, newY))
        self.lastMovePosition = e.GetPosition()
        self.Refresh()

    def OnClick(self, e):
        x, y = e.GetPosition()
        if self.isLeftClick(e):
            eventlog.info("LEFT CLICK")
            for s in self.clickedShapes:
                s.isClicked=False
                s.state="NORMAL"
            del self.clickedShapes[:]
            # motionlog.debug("OnClick (%s, %s)" % (x, y)
            self.selectedShape = self.guessSelectedShape(e)
            eventlog.info("%s", self.selectedShape)
            self.statusbar.SetStatusText("%r" %(self.selectedShape))
            try:
                self.selectedShape.isClicked=True
                self.frameState = self.selectedShape.state = "POSSIBLE_LEFT_DRAG"
                self.selectedShape.velocity =(0,0)
            except:
                pass
        elif self.isRightClick(e):
            eventlog.info("RIGHT CLICK")
            for s in self.rightClickedShapes:
                s.isRightClicked=False
            del self.rightClickedShapes[:]
            try:
                self.selectedShape.isRightClicked=True
                self.frameState = self.selectedShape.state = "POSSIBLE_RIGHT_DRAG"
            except:
                pass
        self.lastPosition = (x, y)
        # motionlog.debug("Shape %s has a hit" % (self.clickedShapes[0])
        self.Refresh()
        e.Skip() # recommended practice

    def OnRelease(self,e):
        if self.frameState=="LEFT_DRAGGING":
            newX, newY = e.GetPosition()
            oldX, oldY = self.lastPosition
            deltaX = newX - oldX
            deltaY = newY - oldY
        self.Refresh()

    def OnTimer(self, e):
        for i in self.shapes:
            i.updatePosition()
            (x,y) = i.position
            self.targetShapes = [s for s in self.shapes if s.contains(x, y) and s is not i and i.isVisible()]
            if len(self.targetShapes) > 0:
                self.targetShapes.sort(key=lambda shape: shape.zOrder, reverse=True)
                s=self.targetShapes[0]
                eventlog.info("TARGET SHAPE : %s", s)
#                try:
                if s.isDropTarget:
                    eventlog.info("DO SOMETHING WITH THE COLLISION EVENT")
                    s.add(i.amt)
                    i.container=s
                    i.hide()
                else:
                    eventlog.info("COLLISION BUT %s is not a drop target ", s)
                motionlog.debug("DROPPED")

 #               except:
 #                   eventlog.info("NO TARGET SHAPE")

        self.Refresh()

    def OnPaint(self, e):
        dc = wx.PaintDC(self)
        for i in self.shapes:
            i.drawself(dc)


        # if self.selectedShape != None:
        #     (x,y) = self.selectedShape.position
        #     self.targetShapes = [s for s in self.shapes if s.contains(x, y) and s is not self.selectedShape]
        #     if len(self.targetShapes) > 0:
        #         self.targetShapes.sort(key=lambda shape: shape.zOrder, reverse=True)
        #         s=self.targetShapes[0]
        #         eventlog.info("TARGET SHAPE : %s", s)
        #         try:
        #             if s.isDropTarget:
        #                 eventlog.info("DO SOMETHING WITH THE COLLISION EVENT")
        #                 s.add(self.selectedShape.amt)
        #                 self.selectedShape.container=s
        #             else:
        #                 eventlog.info("COLLISION BUT %s is not a drop target ", s)
        #             motionlog.debug("DROPPED")

        #         except:
        #             eventlog.info("NO TARGET SHAPE")


def main():
    app = wx.App(redirect=False)   # Error messages go to popup window
    top = Frame(None, "Okane", size=(620, 620))
    top.Show()
    app.MainLoop()




if __name__ == "__main__":
    random.seed()
    main()
