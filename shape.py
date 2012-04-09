import wx
import random
import itertools

class Shape(object):
    """Represents a basic shape"""
    nextZOrder = itertools.count().next
    def __init__(self, pos, size, droptarget=False):
        self.position = pos
        self.size = size
        self.isClicked = self.isRightClicked = False
        self.zOrder = Shape.nextZOrder()
        self.frameState = "NORMAL"
        self.label = "UNTITLED"        
        self.fillColour = (0, 0, 0)
        self.isDropTarget = droptarget
        self.velocity = (0, 0)
        self.drag = (1, 1)
        #velocity = vel
        #self.mass = mass
    def __repr__(self):
        return "Shape(bounds=%r)" % (self.getBounds()) 
    def contains(self):
        raise NotImplementedError
    def generateList(self, num):
        raise NotImplementedError
    def moveTo(self, pos):
        self.position = pos
    def moveBy(self, deltaX, deltaY):
        currentX, currentY = self.position
        self.position = (currentX + deltaX, currentY + deltaY)
    def drawSelf(self):
        raise NotImplementedError
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
        self.velocity = (velX, velY)

    
class Text(Shape):
    '''Represents some text'''
    def __init__(self, pos, size):
        Shape.__init__(self, pos, size)
    def drawSelf(self, dc):
        dc.SetTextForeground((255, 255, 0))
        dc.DrawText("Hello World", pos[0], pos[1])
        
class Circle(Shape):
    '''Represents a circle'''
    def __init__(self, pos, size):
        Shape.__init__(self, pos, size)
    def contains(self, x, y):
        return ((x - self.position[0])**2 + (y - self.position[1])**2 <= self.rad**2)
    def __repr__(self):
        return "Circle(x=%r, y=%r, rad=%r)" % (self.position[0], self.position[1], self.rad)
    def drawself(self, dc):
        dc.BeginDrawing()
        dc.SetPen(wx.Pen("BLACK",1))
        if self.frameState == "LEFT_DRAGGING": # state should include clicked status too
            dc.SetPen(wx.Pen("GRAY",1))
            dc.SetBrush(wx.Brush((70,70,70), wx.SOLID))
        if self.frameState == "NORMAL":
            dc.SetPen(wx.Pen("BLACK",1))            
            if self.isClicked or self.isRightClicked:
                dc.SetBrush(wx.Brush((30,30,30), wx.SOLID))
            else:            
                dc.SetBrush(wx.Brush(self.fillColour, wx.SOLID))
        dc.DrawCircle(self.position[0], self.position[1], self.rad)
        dc.EndDrawing()
    
class RandomCircle(Circle):
    def __init__(self):
        self.position = (random.randrange(300), random.randrange(300))
        self.rad = random.randrange(10, 150)
        Circle.__init__(self, self.position, self.rad)
        self.fillColour = (random.randrange(256), random.randrange(256), random.randrange(256))

class Rect(Shape):
    def __init__(self, pos, size, droptarget=False):
        Shape.__init__(self, pos, size, droptarget=droptarget) 
    def getBounds(self):
        # print "Params: x: %s y: %s width: %s height: %s" % (self.position[0], self.position[1], self.size[0], self.size[1])
        # print "bounds: x1: %s y1: %s x2: %s y2: %s" % (self.position[0], self.position[1], self.size[0], self.size[1])
        return wx.Rect(self.position[0], self.position[1], self.size[0], self.size[1])
    def contains(self, x, y):
        return self.getBounds().InsideXY(x, y)
    def __repr__(self):
        return "Rect(x=%r, y=%r, width=%r, height=%r)" % (self.position[0], self.position[1], self.size[0], self.size[1])
    def drawself(self, dc):
        dc.BeginDrawing()
        if self.frameState == "LEFT_DRAGGING": # state should include clicked status too
            dc.SetPen(wx.Pen("GRAY",1))
            dc.SetBrush(wx.Brush((30,30,30), wx.SOLID))
        if self.frameState == "NORMAL":
            dc.SetPen(wx.Pen("BLACK",1))            
            if self.isClicked:
                dc.SetBrush(wx.Brush((30,30,30), wx.SOLID))
            else:            
                dc.SetBrush(wx.Brush(self.fillColour, wx.SOLID))
        dc.DrawRectangle(self.position[0], self.position[1], self.size[0], self.size[1])
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
        self.frameState="NORMAL"
        
        t = RandomRect(droptarget="True")
        t.velocity = (0,0)
        t.mass = 1.0
        self.shapes.append(t)
        t = RandomCircle()
        t.velocity = (0,0)
        t.mass = 0.5
        self.shapes.append(t)
        
    def generateShapes(self):
        for i in range(10):
            self.shapes.append(RandomRect())
        for i in range(10):
            self.shapes.append(RandomCircle())
    def OnMotion(self, e):
        if self.frameState == "POSSIBLE_LEFT_DRAG" and e.LeftIsDown():
            self.frameState = self.selectedShape.state = "LEFT_DRAGGING"
        elif self.frameState == "LEFT_DRAGGING" and e.LeftIsDown(): 
            # or ((self.frameState == "RIGHT_DRAGGING" and e.RightIsDown()):
            newX, newY = e.GetPosition()
            oldX, oldY = self.lastPosition
            deltaX = newX - oldX
            deltaY = newY - oldY
            
            if (abs(deltaX) > 10) or (abs(deltaY) > 10):            
                print "MOVING"
                self.selectedShape.moveBy(deltaX, deltaY)
                self.lastPosition = e.GetPosition()
            self.Refresh()
        else:
            self.frameState = "MOTION"
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
                        s.state = "NORMAL"
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
                        s.state = "NORMAL"
                    return None
        
    def OnClick(self, e):
        x, y = e.GetPosition()
        if self.isLeftClick(e):
            for s in self.clickedShapes:
                s.isClicked=False
                s.state="NORMAL"
            del self.clickedShapes[:]
            # print "OnClick (%s, %s)" % (x, y) 
            self.selectedShape = self.guessSelectedShape(e)
            try:
                self.selectedShape.isClicked=True
                self.frameState = self.selectedShape.state = "POSSIBLE_LEFT_DRAG"
            except:
                pass
        elif self.isRightClick(e):
            print "RIGHT CLICK"
            for s in self.rightClickedShapes:
                s.isRightClicked=False
            del self.rightClickedShapes[:]
            try:
                self.selectedShape.isRightClicked=True
                self.frameState = self.selectedShape.state = "POSSIBLE_RIGHT_DRAG"
            except:
                pass
        self.lastPosition = (x, y)
        # print "Shape %s has a hit" % (self.clickedShapes[0])
        self.Refresh()
        e.Skip() # recommended practise        

    def OnRelease(self,e):
        if self.frameState=="LEFT_DRAGGING":
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
                    self.frameState="MOTION"
                self.selectedShape.state="NORMAL"
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
    
            
