import wx
import random
import itertools
import operator

class Shape(object):
    """Represents a basic shape"""
    nextZOrder = itertools.count().next
    def __init__(self, pos, size):
        self.setPosition(pos)
        self.setSize(size)
        self.isClicked = False
        self.zOrder = Shape.nextZOrder()
        self.state = "NORMAL"
        self.label = "UNTITLED"        
    def setPosition(self, pos):
        raise NotImplementedError
    def setSize(self, size):
        raise NotImplementedError
    def __repr__(self):
        return "Shape(bounds=%r)" % (self.getBounds()) 
    def contains(self):
        raise NotImplementedError
    def generateList(self, num):
        raise NotImplementedError
    def setClicked(self, clicked):
        self.isClicked = clicked
    def moveTo(self, pos):
        self.setPosition(pos)
    def moveBy(self, deltaX, deltaY):
        currentX = self.x
        currentY = self.y
        self.setPosition((currentX + deltaX, currentY + deltaY))
    def setState(self, state):
        self.state = state
    def setLabel(self, label):
        self.label = label
    def drawSelf(self):
        raise NotImplementedError

class Text(Shape):
    '''Represents some text'''
    def __init__(self, pos, size):
        Shape.__init__(self, pos, size)
    def setText(self, text):
        self.text = text
    def drawSelf(self, dc):
        dc.SetTextForeground((255, 255, 0))
        dc.DrawText("Hello World", pos[0], pos[1])
        
class Circle(Shape):
    '''Represents a circle'''
    def __init__(self, pos, size):
        Shape.__init__(self, pos, size)
    def setPosition(self, pos):
        self.x, self.y = pos
    def setSize(self, size):
        self.rad = size
    def contains(self, x, y):
        return ((x - self.x)**2 + (y - self.y)**2 <= self.rad**2)
    def __repr__(self):
        return "Circle(x=%r, y=%r, rad=%r)" % (self.x, self.y, self.rad)
    def drawself(self, dc):
        dc.BeginDrawing()
        dc.SetPen(wx.Pen("BLACK",1))
        if self.state == "DRAGGING": # state should include clicked status too
            dc.SetPen(wx.Pen("GRAY",1))
            dc.SetBrush(wx.Brush((70,70,70), wx.SOLID))
        if self.state == "NORMAL":
            dc.SetPen(wx.Pen("BLACK",1))            
            if self.isClicked:
                dc.SetBrush(wx.Brush((30,30,30), wx.SOLID))
            else:            
                dc.SetBrush(wx.Brush(self.colour, wx.SOLID))
        dc.DrawCircle(self.x, self.y, self.rad)
        dc.EndDrawing()
    
class RandomCircle(Circle):
    def __init__(self):
        pos = (random.randrange(300), random.randrange(300))
        size = random.randrange(10, 150)
        Circle.__init__(self, pos, size)
        self.colour = (random.randrange(256), random.randrange(256), random.randrange(256))

class Rect(Shape):
    def __init__(self, pos, size):
        Shape.__init__(self, pos, size)        
    def setPosition(self, pos):
        self.x, self.y = pos
    def setSize(self, size):
        self.width, self.height = size
    def getBounds(self):
        # print "Params: x: %s y: %s width: %s height: %s" % (self.x, self.y, self.width, self.height)
        # print "bounds: x1: %s y1: %s x2: %s y2: %s" % (self.x, self.y, self.width, self.height)
        return wx.Rect(self.x, self.y, self.width, self.height)
    def contains(self, x, y):
        return self.getBounds().InsideXY(x, y)
    def __repr__(self):
        return "Rect(x=%r, y=%r, width=%r, height=%r)" % (self.x, self.y, self.width, self.height)
    def drawself(self, dc):
        dc.BeginDrawing()
        if self.state == "DRAGGING": # state should include clicked status too
            dc.SetPen(wx.Pen("GRAY",1))
            dc.SetBrush(wx.Brush((70,70,70), wx.SOLID))
        if self.state == "NORMAL":
            dc.SetPen(wx.Pen("BLACK",1))            
            if self.isClicked:
                dc.SetBrush(wx.Brush((30,30,30), wx.SOLID))
            else:            
                dc.SetBrush(wx.Brush(self.colour, wx.SOLID))
        dc.DrawRectangle(self.x, self.y, self.width, self.height)
        dc.EndDrawing()
        
class RandomRect(Rect):
    def __init__(self):
        pos = (random.randrange(300), random.randrange(300))
        size = (random.randrange(500), random.randrange(500))
        Rect.__init__(self, pos, size)
        self.colour = (random.randrange(256), random.randrange(256), random.randrange(256))

class Frame(wx.Frame):
    def __init__(self, parent, title, size=wx.DefaultSize):
        wx.Frame.__init__(self, parent, wx.ID_ANY, title, wx.DefaultPosition, size)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_TIMER, self.OnTimer)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnClick)
        self.Bind(wx.EVT_LEFT_UP, self.OnRelease)
        self.Bind(wx.EVT_MOTION, self.OnMotion)
        self.timer = wx.Timer(self)
        self.timer.Start(1000) # 1000 milliseconds = 1 second
        self.shapes = list()
        self.generateShapes()
        self.clickedShapes = list()
        self.state="MOTION"
    def generateShapes(self):
        for i in range(10):
            self.shapes.append(RandomRect())
        for i in range(10):
            self.shapes.append(RandomCircle())
    def OnMotion(self, e):
        if self.state == "POSSIBLE_DRAG" and e.LeftIsDown():
            self.state = "DRAGGING"
            self.selectedShape.setState(self.state)
        elif self.state == "DRAGGING" and e.LeftIsDown():
            newX, newY = e.GetPosition()
            oldX, oldY = self.lastPosition
            self.selectedShape.moveBy(newX - oldX, newY - oldY)
            self.lastPosition = e.GetPosition()
            self.Refresh()
        else:
            self.state = "MOTION"
    def guessSelectedShape(self, e):
        x, y = e.GetPosition()
        self.clickedShapes = [s for s in self.shapes if s.contains(x, y)]
        self.clickedShapes.sort(key=lambda shape: shape.zOrder, reverse=True)
        # print "clickedShapes: %s" % (self.clickedShapes)
        if e.ShiftDown():
            if len(self.clickedShapes) > 1:
                return self.clickedShapes[1]
        else:
            return self.clickedShapes[0]
    def OnClick(self, e):
        x, y = e.GetPosition()
        for s in self.clickedShapes:
            s.setClicked(False)
        del self.clickedShapes[:]
        # print "OnClick (%s, %s)" % (x, y) 
        self.selectedShape = self.guessSelectedShape(e)
        self.selectedShape.setClicked(True)
        self.state = "POSSIBLE_DRAG"
        self.lastPosition = (x, y)
        # print "Shape %s has a hit" % (self.clickedShapes[0])
        self.Refresh()
        e.Skip() # recommended practise        
    def OnRelease(self,e):
        if self.state=="DRAGGING":
            newX, newY = e.GetPosition()
            oldX, oldY = self.lastPosition
            self.clickedShapes[0].moveBy(newX-oldX, newY-oldY)
            self.state=="MOTION"
            self.selectedShape.setState("NORMAL")
            self.Refresh()
    def OnTimer(self, e):
        self.Refresh()
    def OnPaint(self, e):
        dc = wx.PaintDC(self)
        for i in self.shapes:
            i.drawself(dc)
            
def main():
    app = wx.App(redirect=False)
    top = Frame(None, "Title", size=(620, 620))
    top.Show()
    app.MainLoop()
    
if __name__ == "__main__":
    print "HELLO WORLD_"
    random.seed()
    main()
    
            
