'''
Created on Feb 8, 2012

@author: johan
'''

import csv
import Model
import Shapes
import math
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

    def checkHit(self, x, y):
        print "You clicked %s at (%s, %s)" % (self.id, x, y)

class DrawableTransaction(Shapes.RandomPosCircle):
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
        Shapes.RandomPosCircle.__init__(self, startMoving=True)

    def __repr__(self):
        return "%s: DrawableTransaction(date=%r,cat=%r, desc=%r, amt=%r)" % (self.id, self.date, self.cat, self.desc, self.amt)

    def nextId(self):
        Transaction.transId = Transaction.transId + 1
        return Transaction.transId
