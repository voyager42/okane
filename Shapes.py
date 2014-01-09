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
        self.size = size
        self.isClicked = self.isRightClicked = False
        self.zOrder = Shape.nextZOrder()
        self.frameState = "NORMAL"
        self.label = "UNTITLED"
        self.fillColour = (0, 0, 0)
        self.isDropTarget = droptarget
        #velocity = vel
        #self.mass = mass
        Particle.__init__(self, pos=pos, velocity=velocity)

    def __repr__(self):
        return "Shape(bounds=%r)" % (self.getBounds())

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
    def __init__(self, pos, rad, **kwargs):
        self.rad = rad
        Shape.__init__(self, pos=pos, size=(rad,rad), **kwargs)

    def contains(self, x, y):
        return ((x - self.position[0])**2 + (y - self.position[1])**2 <= self.rad**2)

    def __repr__(self):
        return "Circle(position=%r, rad=%r, droptarget=%r)" % (self.position, self.rad, self.isDropTarget)

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
    def __init__(self, startMoving=False, **kwargs):
        self.position = (random.randrange(300), random.randrange(300))
        self.rad = random.randrange(10, 150)

        if startMoving:
            self.velocity = (3*random.random(), random.uniform(0, math.pi*2))
        else:
            self.velocity=(0,0)

        Circle.__init__(self, pos=self.position, rad=self.rad, velocity=self.velocity)
        self.fillColour = (random.randrange(256), random.randrange(256), random.randrange(256))

class RandomPosCircle(RandomCircle):
    def __init__(self, **kwargs):
        RandomCircle.__init__(self, **kwargs)
        self.rad = 10
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
