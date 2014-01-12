import wx
import random
import itertools
import math
import cmath
import logging
import logging.config

logging.config.fileConfig('logging.conf')
motionlog=logging.getLogger('motion')
motionlog.setLevel(logging.DEBUG)

eventlog = logging.getLogger('event')
eventlog.setLevel(logging.INFO)
gravity = (0,math.pi) #(10, math.pi)
drag = 0.99 # should be a vector too?

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

def addVectors(v1, v2, *kwargs):
    "Add 2 vectors given in (r, phi) form"
    r1, phi1 = v1
    r2, phi2 = v2
    return cmath.polar(cmath.rect(r1, phi1) + cmath.rect(r2, phi2))

class Particle(object):
    """Represents a particle"""
    def __init__(self, pos=(0,0), mass=1.0, velocity=(0,0)):
        self.velocity = velocity  # (magnitude, angle in radians)
        if velocity:
            motionlog.debug("Particle got velocity %s, %s" % (velocity))

        self.mass = mass
        self.position = pos

    def updatePosition(self): # was updatePosition
        speed1 = self.velocity[0] * drag
        angle1 = self.velocity[1]
        # (speed, angle) = addVectors((speed1, angle1), gravity)
        (speed, angle) = (speed1, angle1)
        dx = math.sin(angle) * speed
        dy = -1*math.cos(angle) * speed
        self.velocity = (speed, angle)
        self.moveBy(dx, dy)

    def moveBy(self, deltaX, deltaY):
        currentX, currentY = self.position
        self.position = (currentX + deltaX, currentY + deltaY)
        # if (deltaX,deltaY) == (0,0):
        #     eventlog.info("STOPPED")

class Shape(Particle):
    """Represents a basic shape"""
    nextZOrder = itertools.count().next

    def __init__(self, pos, size, droptarget=False, velocity=(0,0)):
        Particle.__init__(self, pos=pos, velocity=velocity)
        self.size = size
        self.isClicked = self.isRightClicked = False
        self.zOrder = Shape.nextZOrder()
        self.frameState = "NORMAL"
        self.label = "UNTITLED"
        self.fillColour = (0, 0, 0)
        self.isDropTarget = droptarget
        #velocity = vel
        #self.mass = mass

    def __repr__(self):
        preturn "Shape(bounds=%r)" % (self.getBounds())

    def contains(self):
        raise NotImplementedError

    def generateList(self, num):
        raise NotImplementedError

    def moveTo(self, pos):
        self.position = pos

    def drawSelf(self):
        raise NotImplementedError

class Text(Shape):
    '''Represents some text'''
    def __init__(self, pos, size):
        Shape.__init__(self, pos, size)

    def drawSelf(self, dc):
        dc.SetTextForeground((255, 255, 0))
        dc.DrawText("Hello World", pos[0], pos[1])


class Circle(Shape):
    '''Represents a circle'''
    def __init__(self, pos, size, **kwargs):
        Shape.__init__(self, pos, size, **kwargs)

    def contains(self, x, y):
        return ((x - self.position[0])**2 + (y - self.position[1])**2 <= self.rad**2)

    def __repr__(self):
        return "Circle(x=%r, y=%r, rad=%r, droptarget=%r)" % (self.position[0], self.position[1], self.rad, self.isDropTarget)
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
    def __init__(self, startMoving=False):
        self.position = (random.randrange(300), random.randrange(300))
        self.rad = random.randrange(10, 150)
        if startMoving:
            velocity = (3*random.random(), random.uniform(0, math.pi*2))
        else:
            velocity=(0,0)
        Circle.__init__(self, self.position, self.rad, velocity=velocity)
        self.fillColour = (random.randrange(256), random.randrange(256), random.randrange(256))

class Rect(Shape):
    def __init__(self, pos, size, droptarget=False, **kwargs):
        Shape.__init__(self, pos, size, droptarget=droptarget, **kwargs)

    def getBounds(self):
        # motionlog.debug("Params: x: %s y: %s width: %s height: %s" % (self.position[0], self.position[1], self.size[0], self.size[1]))
        # motionlog.debug("bounds: x1: %s y1: %s x2: %s y2: %s" % (self.position[0], self.position[1], self.size[0], self.size[1]))
        return wx.Rect(self.position[0], self.position[1], self.size[0], self.size[1])
    def contains(self, x, y):
        if self.getBounds().InsideXY(x, y):
            eventlog.debug("%s contains %s,%s", self, x, y)
        return self.getBounds().InsideXY(x, y)

    def __repr__(self):
        return "Rect(x=%r, y=%r, width=%r, height=%r, droptarget=%r)" % (self.position[0], self.position[1], self.size[0], self.size[1], self.isDropTarget)

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
    def __init__(self, droptarget=False, startMoving=False):
        self.position = (random.randrange(300), random.randrange(300))
        self.size = (random.randrange(500), random.randrange(500))
        if startMoving:
            velocity = (3*random.random(), random.uniform(0, math.pi*2))
        else:
            velocity = (0,0)
        Rect.__init__(self, self.position, self.size, droptarget=droptarget, velocity=velocity)
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
        self.timer.Start(10) # 1000 milliseconds = 1 second
        self.shapes = list()
        self.clickedShapes = list()
        self.rightClickedShapes = list()
        self.frameState="NORMAL"
        #self.generateShapes()
#        t = Rect((10,10),(70,70))
        t = RandomRect()
        self.shapes.append(t)
 #       t = Rect((0,0), (30,30))
        t = RandomRect()
        self.shapes.append(t)
        self.lastMovePosition = (0,0)
        self.selectedShape = None

    def generateShapes(self):
        for i in range(10):
            self.shapes.append(RandomRect(startMoving=True))
        for i in range(10):
            self.shapes.append(RandomCircle(startMoving=True))

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
            for s in self.clickedShapes:
                s.isClicked=False
                s.state="NORMAL"
            del self.clickedShapes[:]
            # motionlog.debug("OnClick (%s, %s)" % (x, y)
            self.selectedShape = self.guessSelectedShape(e)
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
            if self.selectedShape != None:
                eventlog.info("RELEASING SELECTED SHAPE")
                self.targetShapes = [s for s in self.shapes if s is not self.selectedShape and s.contains(newX, newY)]
                if len(self.targetShapes) > 0:
                    self.targetShapes.sort(key=lambda shape: shape.zOrder, reverse=True)
                    s=self.targetShapes[0]
                    eventlog.info("TARGET SHAPE : %s", s)
                    try:
                        if s.isDropTarget:
                            eventlog.info("DO SOMETHING WITH THE DROPPED OBJECT")
                        else:
                            eventlog.info("%s is not a drop target ", s)
                        #motionlog.debug("DROPPED")
                            self.selectedShape.state="NORMAL"
                            self.frameState="NORMAL"
                    except:
                        eventlog.info("NO TARGET SHAPE")
                self.selectedShape.isClicked = False
                self.selectedShape.state="NORMAL"
                self.frameState="NORMAL"
                self.selectedShape.velocity=calcMouseVelocity((oldX,oldY), (newX, newY))

        self.Refresh()

    def OnTimer(self, e):
        self.Refresh()

    def OnPaint(self, e):
        dc = wx.PaintDC(self)
        for i in self.shapes:
            i.updatePosition()
            i.drawself(dc)

        if self.selectedShape != None:
            (x,y) = self.selectedShape.position
            self.targetShapes = [s for s in self.shapes if s.contains(x, y) and s is not self.selectedShape]
            if len(self.targetShapes) > 0:
                self.targetShapes.sort(key=lambda shape: shape.zOrder, reverse=True)
                s=self.targetShapes[0]
                eventlog.info("TARGET SHAPE : %s", s)
                try:
                    if s.isDropTarget:
                        eventlog.info("DO SOMETHING WITH THE COLLISION EVENT")
                    else:
                        eventlog.info("COLLISION BUT %s is not a drop target ", s)
                    #motionlog.debug("DROPPED")

                except:
                    eventlog.info("NO TARGET SHAPE")

def main():
    app = wx.App(redirect=False)
    top = Frame(None, "Okane", size=(620, 620))
    top.Show()
    app.MainLoop()

if __name__ == "__main__":
    random.seed()
    main()
