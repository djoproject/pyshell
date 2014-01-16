

class executionNode(object):
    def __init__(self, command = None, args = None, parent = None):
        #TODO command must a valid instance of command class
        
        #TODO parent must be an instance of executionNode or None
    
        #TODO args must be an instance of list or None
    
        self.command = command #could be None only if root
        self.parent = parent
        self.args = args #TODO must be in inputBuffer, no ?
        self.inputBuffer = []
        self.outputBuffer = []
        self.childs = []
        self.currentExploredChild = -1
        
    def addChild(self, child):
        self.childs.append(child)
