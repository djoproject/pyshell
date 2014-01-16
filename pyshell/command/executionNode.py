

class executionNode(object):
    def __init__(self, command = None, args = None, parent = None):
        #TODO command must a valid instance of command class
        
        #TODO parent must be an instance of executionNode or None
    
        #TODO args must be an instance of list or None
    
        self.command = command #could be None only if root
        self.parent = parent
        self.args = args #can't be directly in input buffer because input buffer will contain the data from the previous piped command
        self.inputBuffer = []
        self.outputBuffer = []
        self.childs = []
        self.currentExploredChild = -1 #TODO this variable will probably be useless with the breakpoint system
        self.executionCount = 0 #each time the node is execute, the counter is incremented
        self.id = 0 #TODO par ordre d'insertion et surtout par ordre d'execution
        
    def addChild(self, child):
        self.childs.append(child)
        
    def executePreprocess(self, pqueue):
        #execute preProcess for the last data in the input buffer
    
        #if multi output:
            #-add the data in the input buffer and add breakpoint
            #the breakpoint are added only from the second result, the first will directly be executed byt the engine
    
        pass #TODO
        
    def executePostprocess(self, pqueue):
        #manage multi output like preprocess management (see above)
            #but into output process
    
        pass #TODO
        
    def executeProcess(self, pqueue):
        #put result into local output buffer
        
        pass  #TODO
