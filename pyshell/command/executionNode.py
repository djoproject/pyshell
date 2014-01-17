

class executionNode(object):
    def __init__(self, level, command = None, args = None, parent = None):
        #TODO command must a valid instance of command class
        
        #TODO parent must be an instance of executionNode or None
    
        #TODO args must be an instance of list or None
    
        self.command        = command #could be None only if root
        self.parent         = parent
        self.args           = args #can't be directly in input buffer because input buffer will contain the data from the previous piped command
        self.inputBuffer    = []
        self.outputBuffer   = []
        self.childs         = []
        self.executionCount = (0,0,0,) #TODO each time the node is execute, the counter is incremented on pre/pro/pos process
        
    def addChild(self, child):
        self.childs.append(child)
        
    def executePreprocess(self, stack):
        #execute preProcess for the first item the input buffer
    
        #if multi output:
            #-add the data in the input buffer and add breakpoint
            #the breakpoint are added only from the second result, the first will directly be executed byt the engine
                #be carefull to insert the last item of the result in first, because of the stack
    
        pass #TODO
        
    def executePostprocess(self, stack):
        #TODO execute postprocess with the first item in the buffer
            #don't forget to remove this item from the list
        
        #TODO manage multi output like preprocess management (see above)
            #but into output process
    
        pass #TODO
        
    def executeProcess(self, stack):
        #TODO from where came the process input ??? fail... need a process input buffer
    
        #TODO execute process
    
        #TODO put result into local output buffer
        
        pass  #TODO
