'''
Created on Feb 13, 2012

@author: johan
'''
import wx
import colorsys
import random

class CView(wx.Panel):
    def __init__(self, parent, title, size=wx.DefaultSize):
        wx.Panel.__init__(self, parent, wx.ID_ANY, wx.DefaultPosition, size, name="View")
        
        self.Bind(wx.EVT_TIMER, self.OnTimer)
        self.Bind(wx.EVT_LEFT_UP, self.OnClick)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.timer = wx.Timer(self)
        self.Show()

    def start(self):
        self.render()
        self.timer.Start(1000) # 1000 milliseconds = 1 second
        
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
        width = windowSize[0] - 30
        height = windowSize[1] - 30
        print "Width: %s" %(width)
        print "Height: %s" %(height)

        for i in range(n):
            x, y = random.randrange(width), random.randrange(height)
            #print "x: %s, y: %s" % (x, y)
            self.positions.append((x, y))
                
    def render(self):
        print "============= RENDER ============"
        self.totals = self.model.getTotals()
        self.num = len(self.model.getTotals())         
        self.generateColours(self.num)
        self.generatePositions(self.num)
            
        # for (k, v) in self.totals:
        #     print " ( %s , %s ) " % (k, v)
            
        

    def OnTimer(self, e):
        print "OnTimer called"
        self.Refresh()
        ## circlePos = (self.displaceX, self.displaceY)
        ## self.circles.append(circlePos)

        ## # # Change position of the next circle that
        ## # # we want to append to the list next time
        ## windowSize = self.GetClientSizeTuple()
        ## maxX = windowSize[0] - 30
        ## maxY = windowSize[1] - 30
        ## self.displaceX += 40
        ## if self.displaceX > maxX:
        ##     self.displaceX = 30
        ##     self.displaceY += 40
        ##     if self.displaceY > maxY:
        ##         self.timer.Stop()        
        ##         print "Timer Stopped"
       


    def OnClick(self, e):
        print "Window clicked"
        # Do something here to show the click was received.
        # Here we remove a random circle.
        n = len(self.circles)
        if n <= 1: # then dont do it
            return
        i = random.randrange(n)
        del self.circles[i]
        print "Removed %dth circle" % (i,)
        self.Refresh()

    
    def OnPaint(self, e):
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
                print "r: %s g: %s b: %s a: %s" %(r, g, b, a)
                dc.SetBrush(wx.Brush(wx.Colour(r, g, b, a)))
                dc.DrawCircle(x, y, v)
        # Go through the list of circles to draw all of them
        #for circle in self.circles:
        #    dc.DrawCircle(circle[0], circle[1], 10)

    # def onPaint(self, evt):
    #     print evt
    #     pdc = wx.PaintDC(self)
    #     try:
    #         dc = wx.GCDC(pdc)
    #     except:
    #         dc = pdc
        #totals = self.model.getTotals()
        
        
            #dc.Clear()
#        for i in range(len(self.model.getTotals())):
#            print i
#            r, g, b = self.colours[i]
#            x, y = self.positions[i]
#            rad = round(totals[i])
#            if rad < 0.0:
#                rad = rad * - 1
#            penclr   = wx.Colour(r, g, b, wx.ALPHA_OPAQUE)
#            brushclr = wx.Colour(r, g, b, 128)   # half transparent
#            dc.SetPen(wx.Pen(penclr))
#            dc.SetBrush(wx.Brush(brushclr))
#            dc.DrawCircle(x, y, float(rad))
##        else:     
#         rect = wx.Rect(0,0, 100, 100)
#         for RGB, pos in [((178,  34,  34), ( 50,  90)),
#                             (( 35, 142,  35), (110, 150)),
#                             ((  0,   0, 139), (170,  90))
#                             ]:
#             r, g, b = RGB
#             penclr   = wx.Colour(r, g, b, wx.ALPHA_OPAQUE)
#             brushclr = wx.Colour(r, g, b, 128)   # half transparent
#             dc.SetPen(wx.Pen(penclr))
#             dc.SetBrush(wx.Brush(brushclr))
# #            x, y = pos
# #            dc.DrawCircle(x, y, 40)
#             rect.SetPosition(pos)
#             dc.DrawRoundedRectangleRect(rect, 8)
