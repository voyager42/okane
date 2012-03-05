'''
Created on Feb 13, 2012

@author: johan
'''
import transaction
import csv

class CModel():
    def __init__(self):
        self.transactionList = []
        self.transactionDict = {}
        self.transactionTotals = {}
        self.modelChangedCallbacks = []
        
    def dumpTransactionList(self):
        for t in self.transactionList:
            print t
            
    def dumpDicts(self):
        print "CATEGORIES"
        for k in self.transactionDict.keys():
            outstr =  k + ":"
            for v in self.transactionDict[k]:
                outstr += str(v.id) + " "
            print outstr3
        print "================================"
        print "TOTALS"
        for k in self.transactionTotals.keys():
            print "%s: %s" % (k, self.transactionTotals[k])
            
    def openFile(self, fn):
        ifile = open(fn, "rb")
        reader = csv.reader(ifile)
        for row in reader:
            if len(row) > 0 and row[0] == "HIST":
                self.transactionList.append(transaction.Transaction(row[1], row[3], row[4], row[5]))
        ifile.close()
        #self.dumpTransactionList()
        self.createDicts()
        #self.dumpDicts()
        self.notifyModelChanged()

    def createDicts(self):
        for l in self.transactionList:
            print l
            if self.transactionDict.has_key(l.cat):
                self.transactionDict[l.cat].append(l)
                self.transactionTotals[l.cat] += l.amt
            else:
                self.transactionDict[l.cat] = []                
                self.transactionDict[l.cat].append(l)
            if self.transactionTotals.has_key(l.cat):
                self.transactionTotals[l.cat] += l.amt
            else:
                self.transactionTotals[l.cat] = l.amt
                
                
    def getTotals(self):
        tupTotals = []
        for k in self.transactionTotals.keys():
            tupTotals.append((k, self.transactionTotals[k], self.transactionTotals[k] < 0))
        return tupTotals

    def processClick(self, pos):
        x, y = pos
        print "model: processClick (%s, %s)" % (x, y)
        for t in self.transactionList:
            if t.checkHit(x, y):
                self.state = "DRAG"

    def getState(self):
        return self.state        
            
    def getTransactionList(self):
        return self.transactionList

    def generatePositions(self, n):
        # move to model
        width, height = self.GetSize()
        self.positions = []
        windowSize = self.GetClientSizeTuple()
        width = windowSize[0] - 30
        height = windowSize[1] - 30
        print "Width: %s" %(width)
        print "Height: %s" %(height)

        for i in range(n):
            x, y = random.randrange(width), random.randrange(height)
            self.transactionList[i].position = (x, y)
            
            #print "x: %s, y: %s" % (x, y)
            #self.positions.append((x, y))
                
    def addCallback(self, func):
        print "Setting callback"
        self.modelChangedCallbacks.append(func)

    def removeCallback(self, func):
        print "Setting callback"
        try:
            self.modelChangedCallbacks.remove(self.callbacks.index(func))
        except:
            print "Could not remove func"
            
    def notifyModelChanged(self):
        for f in self.modelChangedCallbacks:
            f()
            
            
    
    
    
    
