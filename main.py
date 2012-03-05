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

wildcard = "CSV files (*.csv)|*.csv|" \
            "All files (*.*)|*.*"    


class Frame(wx.Frame):
    def __init__(self, parent, title, size=wx.DefaultSize):
        wx.Frame.__init__(self, parent, wx.ID_ANY, title, wx.DefaultPosition, size)
        menuBar = wx.MenuBar()
        menu = wx.Menu()
        m_open = menu.Append(wx.ID_FILE, "O&pen\tAlt-O", "Open file")
        m_exit = menu.Append(wx.ID_EXIT, "E&xit\tAlt-X", "Close window and exit program.")

        menuBar.Append(menu, "&File")
        self.SetMenuBar(menuBar)
        self.statusbar = self.CreateStatusBar()

        # MVC 
        self.controller = Controller.CController()
        self.model = Model.CModel()
        self.controller.setModel(self.model)

        self.totalsView = TotalsView.TotalsView(self, "Category/Totals View", (400, 300))
        
        self.totalsView.setModel(self.model)        
        self.controller.setView(self.totalsView)

        #self.transactionView = TransactionView.TransactionView(self, "Transaction View", (400,200))
        #self.transactionView.setModel(self.model)
        #self.controller.setView(self.transactionView)        

        # events
        self.Bind(wx.EVT_MENU, self.OnOpen, m_open)
        self.Bind(wx.EVT_MENU, self.OnClose, m_exit)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Bind(wx.EVT_LEFT_UP, self.OnClick)
        #self.Bind(wx.EVT_PAINT, self.totalsView.OnPaint)

        # layout
        #box = wx.BoxSizer(wx.VERTICAL)
        #box.Add(self.totalsView, wx.EXPAND)
        #box.Add(self.transactionView, wx.EXPAND)
        #self.SetSizer(box)
        #self.Layout()

    def OnClose(self, event):
        dlg = wx.MessageDialog(self, 
            "Do you really want to close this application?",
            "Confirm Exit", wx.OK|wx.CANCEL|wx.ICON_QUESTION)
        result = dlg.ShowModal()
        dlg.Destroy()
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
        
        self.controller.openFile(dlg.GetFilename())
        #self.totalsView.start()
        dlg.Destroy()
        self.Refresh()

    def OnClick(self, event):
        print "Frame OnClick"
        self.controller.onClick(event)

    # def OnPaint(self, e):
    #     print "OnPaint called"
    #     dc = wx.PaintDC(self)
    #     dc.SetPen(wx.Pen(wx.BLUE))
    #     dc.SetBrush(wx.Brush(wx.BLUE))
    #     # Go through the list of circles to draw all of them
    #     for circle in self.circles:
    #         dc.DrawCircle(circle[0], circle[1], 10)

    ## def OnTimer(self, e):
    ##     print "OnTimer called"
    ##     circlePos = (self.displaceX, self.displaceY)
    ##     self.circles.append(circlePos)

    ##     # Change position of the next circle that
    ##     # we want to append to the list next time
    ##     windowSize = self.GetClientSizeTuple()
    ##     maxX = windowSize[0] - 30
    ##     maxY = windowSize[1] - 30
    ##     self.displaceX += 40
    ##     if self.totalsView.displaceX > maxX:
    ##         self.totalsView.displaceX = 30
    ##         self.totalsView.displaceY += 40
    ##         if self.totalsView.displaceY > maxY:
    ##             self.timer.Stop()        
    ##             print "Timer Stopped"
    ##     self.Refresh()

    ## def OnClick(self, e):
    ##     print "Window clicked"
    ##     # Do something here to show the click was received.
    ##     # Here we remove a random circle.
    ##     n = len(self.totalsView.circles)
    ##     if n <= 1: # then dont do it
    ##         return
    ##     i = random.randrange(n)
    ##     del self.totalsView.circles[i]
    ##     print "Removed %dth circle" % (i,)
    ##     self.Refresh()

    # def OnPaint(self, event):
    #     pdc = wx.PaintDC(self)
    #     try:
    #         dc = wx.GCDC(pdc)
    #     except:
    #         dc = pdc
    #     rect = wx.Rect(0,0, 100, 100)
    #     for RGB, pos in [((178,  34,  34), ( 50,  90)),
    #                      (( 35, 142,  35), (110, 150)),
    #                      ((  0,   0, 139), (170,  90))
    #                      ]:
    #         r, g, b = RGB
    #         penclr   = wx.Colour(r, g, b, wx.ALPHA_OPAQUE)
    #         brushclr = wx.Colour(r, g, b, 128)   # half transparent
    #         dc.SetPen(wx.Pen(penclr))
    #         dc.SetBrush(wx.Brush(brushclr))
    #         rect.SetPosition(pos)
    #         dc.DrawRoundedRectangleRect(rect, 8)


def main():
    app = wx.App(redirect=False)   # Error messages go to popup window
    top = Frame(None, "Title", size=(620,460))
    top.Show()
    app.MainLoop()
    
if __name__ == "__main__":
    random.seed()
    main()
