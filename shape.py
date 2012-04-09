import wx
import random
import itertools

class Shape(object):
    """Represents a basic shape"""
    nextZOrder = itertools.count().next
    def __init__(self, pos, size, droptarget=False):
        self.setPosition(pos)
        self.setSize(size)
        self.isClicked = self.isRightClicked = False
        self.zOrder = Shape.nextZOrder()
        self.state = "NORMAL"
        self.label = "UNTITLED"        
        self.fillColour = (0, 0, 0)
        self.droptarget = droptarget
        self.velocity = (0, 0)
        self.drag = (1, 1)
    def setPosition(self, pos):
        raise NotImplementedError
    def setVelocity(self, xvel, yvel):
        self.velocity = (xvel, yvel)
    def setMass(self, mass):
        self.mass = mass
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
    def setRightClicked(self, clicked):
        self.isRightClicked = clicked
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
    def setfillColour(self, colour):
        self.fillColour = colour
    def isDropTarget(self):
        return self.droptarget
    def updatePosition(self):
        velX, velY = self.velocity
        speedX = abs(velX)
        speedY = abs(velY)

        velX = velX*(self.mass)
        velY = velY*(self.mass)
            
        if abs(velX) < 0.001:
            velX = 0
        if abs(velY) < 0.001:
            velY = 0
        self.moveBy(velX, velY)
        self.setVelocity(velX, velY)

    
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
        # dc.SetPen(wx.Pen("BLACK", 5))
        # dc.SetBrush(wx.Brush(self.fillColour, wx.SOLID))
        # dc.DrawCircle(self.x, self.y, self.rad)
        dc.SetPen(wx.Pen("BLACK",1))
        if self.state == "LEFT_DRAGGING": # state should include clicked status too
            dc.SetPen(wx.Pen("GRAY",1))
            dc.SetBrush(wx.Brush((70,70,70), wx.SOLID))
        if self.state == "NORMAL":
            dc.SetPen(wx.Pen("BLACK",1))            
            if self.isClicked or self.isRightClicked:
                dc.SetBrush(wx.Brush((30,30,30), wx.SOLID))
            else:            
                dc.SetBrush(wx.Brush(self.fillColour, wx.SOLID))
        dc.DrawCircle(self.x, self.y, self.rad)
        dc.EndDrawing()
    
class RandomCircle(Circle):
    def __init__(self):
        pos = (random.randrange(300), random.randrange(300))
        size = random.randrange(10, 150)
        Circle.__init__(self, pos, size)
        self.fillColour = (random.randrange(256), random.randrange(256), random.randrange(256))

class Rect(Shape):
    def __init__(self, pos, size, droptarget=False):
        Shape.__init__(self, pos, size, droptarget=droptarget)        
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
        if self.state == "LEFT_DRAGGING": # state should include clicked status too
            dc.SetPen(wx.Pen("GRAY",1))
            dc.SetBrush(wx.Brush((30,30,30), wx.SOLID))
        if self.state == "NORMAL":
            dc.SetPen(wx.Pen("BLACK",1))            
            if self.isClicked:
                dc.SetBrush(wx.Brush((30,30,30), wx.SOLID))
            else:            
                dc.SetBrush(wx.Brush(self.fillColour, wx.SOLID))
        # dc.SetPen(wx.Pen("BLACK", 5))
        # dc.SetBrush(wx.Brush(self.fillColour, wx.SOLID))
        dc.DrawRectangle(self.x, self.y, self.width, self.height)
        dc.EndDrawing()
        
class RandomRect(Rect):
    def __init__(self, droptarget=False):
        pos = (random.randrange(300), random.randrange(300))
        size = (random.randrange(500), random.randrange(500))
        Rect.__init__(self, pos, size, droptarget=droptarget)
        self.fillColour = (random.randrange(256), random.randrange(256), random.randrange(256))

class Frame(wx.Frame):
    def __init__(self, parent, title, size=wx.DefaultSize):
        wx.Frame.__init__(self, parent, wx.ID_ANY, title, wx.DefaultPosition, size)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_TIMER, self.OnTimer)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnClick)
        self.Bind(wx.EVT_RIGHT_DOWN, self.OnClick)
        self.Bind(wx.EVT_LEFT_UP, self.OnRelease)
        self.Bind(wx.EVT_RIGHT_UP, self.OnRelease)
        self.Bind(wx.EVT_MOTION, self.OnMotion)
        self.timer = wx.Timer(self)
        self.timer.Start(100) # 1000 milliseconds = 1 second
        self.shapes = list()
        #self.generateShapes()
        self.clickedShapes = list()
        self.rightClickedShapes = list()
        self.state="NORMAL"
        
        t = RandomRect(droptarget="True")
        t.setVelocity(0,0)
        t.setMass(1.0)
        self.shapes.append(t)
        t = RandomCircle()
        t.setVelocity(0,0)
        t.setMass(0.5)
        self.shapes.append(t)
        
    def generateShapes(self):
        for i in range(10):
            self.shapes.append(RandomRect())
        for i in range(10):
            self.shapes.append(RandomCircle())
    def OnMotion(self, e):
        if self.state == "POSSIBLE_LEFT_DRAG" and e.LeftIsDown():
            self.state = "LEFT_DRAGGING"
            self.selectedShape.setState(self.state)
        elif self.state == "LEFT_DRAGGING" and e.LeftIsDown(): 
            # or ((self.state == "RIGHT_DRAGGING" and e.RightIsDown()):
            newX, newY = e.GetPosition()
            oldX, oldY = self.lastPosition
            deltaX = newX - oldX
            deltaY = newY - oldY
            
            if (abs(deltaX) > 10) or (abs(deltaY) > 10):            
                self.selectedShape.moveBy(deltaX, deltaY)
                self.lastPosition = e.GetPosition()
            self.Refresh()
        else:
            self.state = "MOTION"
    def isLeftClick(self, e):
        return (e.GetButton() == wx.MOUSE_BTN_LEFT)
    def isRightClick(self, e):
        return (e.GetButton() == wx.MOUSE_BTN_RIGHT)
    def guessSelectedShape(self, e):
        x, y = e.GetPosition()
        if self.isLeftClick(e):
            self.clickedShapes = [s for s in self.shapes if s.contains(x, y)]
            self.clickedShapes.sort(key=lambda shape: shape.zOrder, reverse=True)
            print "clickedShapes: %s" % (self.clickedShapes)
            if e.ShiftDown():
                if len(self.clickedShapes) > 1:
                    return self.clickedShapes[1]
            else:
                try: 
                    clicked = self.clickedShapes[0]
                    return clicked
                except:
                    for s in self.shapes:
                        s.setState("NORMAL")
                    return None
        if self.isRightClick(e):
            self.rightClickedShapes = [s for s in self.shapes if s.contains(x, y)]
            self.rightClickedShapes.sort(key=lambda shape: shape.zOrder, reverse=True)
            print "rightClickedShapes: %s" % (self.rightClickedShapes)
            if e.ShiftDown():
                if len(self.rightClickedShapes) > 1:
                    return self.rightClickedShapes[1]
            else:
                try: 
                    clicked = self.rightClickedShapes[0]
                    return clicked
                except:
                    for s in self.shapes:
                        s.setState("NORMAL")
                    return None
        
    def OnClick(self, e):
        x, y = e.GetPosition()
        if self.isLeftClick(e):
            for s in self.clickedShapes:
                s.setClicked(False)
                s.setState("NORMAL")
            del self.clickedShapes[:]
            # print "OnClick (%s, %s)" % (x, y) 
            self.selectedShape = self.guessSelectedShape(e)
            try:
                self.selectedShape.setClicked(True)
                self.state = "POSSIBLE_LEFT_DRAG"
            except:
                pass
        elif self.isRightClick(e):
            print "RIGHT CLICK"
            for s in self.rightClickedShapes:
                s.setRightClicked(False)
            del self.rightClickedShapes[:]
            try:
                self.selectedShape.setRightClicked(True)
                self.state = "POSSIBLE_RIGHT_DRAG"
            except:
                pass
        self.lastPosition = (x, y)
        # print "Shape %s has a hit" % (self.clickedShapes[0])
        self.Refresh()
        e.Skip() # recommended practise        

    def OnRelease(self,e):
        if self.state=="LEFT_DRAGGING":
            newX, newY = e.GetPosition()
            oldX, oldY = self.lastPosition
            deltaX = newX - oldX
            deltaY = newY - oldY            
            if (abs(deltaX) > 10) or (abs(deltaY) > 10):
                self.selectedShape.moveBy(deltaX, deltaY)
            self.targetShapes = [s for s in self.shapes if s.contains(newX, newY) and s is not self.selectedShape]
            self.targetShapes.sort(key=lambda shape: shape.zOrder, reverse=True)
            try:
                shape = self.targetShapes[0]
                if self.targetShapes[0].isDropTarget():
                    print "DO SOMETHING WITH THE DROPPED OBJECT"
                    #print "DROPPED"
                    self.state=="MOTION"
                self.selectedShape.setState("NORMAL")
            except:
                print "NO TARGET SHAPE"
                
            self.Refresh()
    def OnTimer(self, e):
        self.Refresh()
    def OnPaint(self, e):
        dc = wx.PaintDC(self)
        for i in self.shapes:
            i.updatePosition()
            i.drawself(dc)
            
def main():
    app = wx.App(redirect=False)
    top = Frame(None, "Okane", size=(620, 620))
    top.Show()
    app.MainLoop()
    
if __name__ == "__main__":
    random.seed()
    main()
    
            
