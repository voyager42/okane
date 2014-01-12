'''
Created on Feb 8, 2012

@author: johan
'''

import csv
import Model
import Shapes
import math
import wx

class Enum(set):
    def __getattr__(self, name):
        if name in self:
            return name
        raise AttributeError

Type = Enum(["EXPENSE", "INCOME"])

class TransactionList(list):
    """Represents a list of bank transactions"""
    def __init__(self, name=None):
        list.__init__(self)
        self.name = name
#        http://wiki.python.org/moin/HowTo/Sorting


    def getName(self):
        return self.name

class Bucket(Shapes.Rect):
    """Represents a bucket to which transactions can be added"""
    transId = 0
    def __init__(self, amt, cat, desc, **kwargs):
        """constructor"""
        self.cat = cat
        self.desc = desc
        self.amt = float(amt)
        self.labels=list()
        self.contents = []
        Shapes.Rect.__init__(self, **kwargs)

    def __repr__(self):
        return "Bucket(cat=%r, desc=%r, amt=%r)" % (self.cat, self.desc, self.amt)

    def add(self, t):
        self.amt += t

class Transaction(object):
    """Represents a bank transaction"""
    transId = 0
    def __init__(self, date, amt, cat, desc):
        """constructor"""
        self.id = self.nextId()
        self.date = date
        self.cat = cat
        self.desc = desc
        self.amt = float(amt)
        self.labels=list()
        self.position = (0,0)
        if amt < 0:
            self.labels.append("EXPENSE")
        else:
            self.labels.append("INCOME")

    def __repr__(self):
        return "%s: Transaction(date=%r,cat=%r, desc=%r, amt=%r)" % (self.id, self.date, self.cat, self.desc, self.amt)

    def nextId(self):
        Transaction.transId = Transaction.transId + 1
        return Transaction.transId

class DrawableTransaction(Shapes.RandomPosCircle):
    """Represents a bank transaction"""
    transId = 0
    def __init__(self, date, amt, cat, desc):
        """constructor"""
        print "new DrawableTransaction"
        self.id = self.nextId()
        self.date = date
        self.cat = cat
        self.desc = desc
        self.amt = float(amt)
        self.labels=list()
        self.position = (0,0)
        if self.amt < 0:
            self.labels.append("EXPENSE")
        else:
            self.labels.append("INCOME")
        Shapes.RandomPosCircle.__init__(self, startMoving=True)

    def __repr__(self):
        return "%s: DrawableTransaction(date=%r,cat=%r, desc=%r, amt=%r)" % (self.id, self.date, self.cat, self.desc, self.amt)

    def nextId(self):
        Transaction.transId = Transaction.transId + 1
        return Transaction.transId

    def add(self, amt):
        self.amt += amt

    def drawself(self, dc):
        if self.isVisible():
            Shapes.RandomPosCircle.drawself(self,dc)
            dc.BeginDrawing()
            dc.SetPen(wx.Pen("BLACK",1))
            dc.SetBrush(wx.Brush(self.fillColour, wx.SOLID))
            dc.DrawRectangle(self.position[0], self.position[1], 10,20)
            dc.SetTextForeground((0, 0, 0))
            dc.DrawText(str(self.amt), self.position[0]+5, self.position[1]+5)
            dc.EndDrawing
