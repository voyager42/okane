'''
Created on Feb 13, 2012

@author: johan
'''

class CController():
    def __init__(self):        
        pass
    
    def setModel(self, model):
        self.model = model
        
    def setView(self, view):
        self.view = view
    
    def openFile(self, fn):
        self.model.openFile(fn)
        self.view.start()
        
    def onClick(self, event):
        self.model.processClick(event.GetPosition())
        print self.model.getState()
        
        
        
    
    
        
