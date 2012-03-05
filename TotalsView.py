'''
Created on Feb 13, 2012

@author: johan
'''
import wx
import colorsys
import random
import View

class TotalsView(View.CView):
    def __init__(self, parent, title, size=wx.DefaultSize):
        wx.Panel.__init__(self, parent, wx.ID_ANY, (0,0), size, name="View")
        print "size %s" % (wx.DefaultSize)

        self.Bind(wx.EVT_TIMER, self.OnTimer)
        self.Bind(wx.EVT_LEFT_UP, self.OnClick)
        self.Bind(wx.EVT_PAINT, self.OnPaint)        
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.timer = wx.Timer(self)
        self.isVisible=False
        self.Show()

    def start(self):
        self.render()
        self.timer.Start(1000) # 1000 milliseconds = 1 second
        self.isVisible = True
        
    def setModel(self, model):
        print "SETTING MODEL in VIEW"
        self.model = model
        self.model.addCallback(self.render)
        self.model.removeCallback(self.render)
        self.model.addCallback(self.render)
        
    def generateColours(self, n):
        self.colours = []
        for v in range(n):
            self.colours.append((random.randrange(255), random.randrange(255), random.randrange(255), 128))    
        print self.colours
        
    def generatePositions(self, n):
        width, height = self.GetSize()
        self.positions = []
        windowSize = self.GetClientSizeTuple()
        print "windowSize[0] = %s " %(windowSize[0])
        print "windowSize[1] = %s " %(windowSize[1])

        width = windowSize[0] - 30
        height = windowSize[1] - 30
        print "Width: %s" %(width)
        print "Height: %s" %(height)

        for i in range(n):
            x, y = random.randrange(width), random.randrange(height)
            #print "x: %s, y: %s" % (x, y)
            self.positions.append((x, y))
                
    def render(self):
        self.totals = self.model.getTotals()
        self.num = len(self.model.getTotals())         
        self.generateColours(self.num)
        self.generatePositions(self.num)
            
        # for (k, v) in self.totals:
        #     print " ( %s , %s ) " % (k, v)
            
    def OnSize(self, e):
        print "OnSize called"
        self.Refresh()    

    def OnTimer(self, e):
        print "OnTimer called"
        self.Refresh()

    def OnClick(self, event):
        # propagate event so that the Controller can handle it
        self.propagateEvent(event)

    def propagateEvent(self, event):
        event.ResumePropagation(event.StopPropagation() + 1)
        event.Skip()

    def OnPaint(self, e):
        if self.isVisible:
            print "OnPaint called"
            dc = wx.PaintDC(self)
            dc.SetPen(wx.Pen(wx.BLUE))
            for i in range(self.num):
                (k, v, n) = self.totals[i]
                (x, y) = self.positions[i]
                print "(%s, %s, %s, %s)" % (x, y, v, n)
                if n:
                    v = v * -1
                    if v <= 100:
                        (r, g, b, a) = self.colours[i]
                        dc.SetBrush(wx.Brush(wx.Colour(r, g, b, a)))
                        dc.DrawCircle(x, y, v)
