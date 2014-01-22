#TODO
    #-how to detect a Non return function from a None return function?
        #the two case will return None :/
        #http://stackoverflow.com/questions/15300550/python-return-return-none-and-no-return-at-all

def genericProcess(stack, inputbuffer, cmd)
    #extract data from buffer
    if len(inputbuffer) == 0:
        pass #TODO raise no data to execute
    
    nextData = inputbuffer.pop(0)
    
    #manage no data
    if nextData == None:
        nextData = []
    
    #process data
    if hasattr(cmd, "checker"):
        data = cmd.checker.checkArgs(nextData)
    else:
        data = {}

    #execute preProcess for the first item the input buffer
    r = cmd(**data)

    #convert every result in multi output
    if not isinstance(r, MultiOutput):
        r = [r]

    return r

class executionNode(object):
    def __init__(self, command = None, args = None, parent = None):
        #command must a valid instance of command class
        if not isinstance(command, Command):
            pass #TODO raise
        
        #parent must be an instance of executionNode or None
        if executionNode != None and not isinstance(parent, executionNode):
            pass #TODO raise
    
        #args must be an instance of list or None
        if args!= None and not isinstance(args, list) and not isinstance(args, tuple):
            pass #TODO raise
    
        self.command        = command #could be None only if root
        self.parent         = parent
        self.args           = args #can't be directly in input buffer because input buffer will contain the data from the previous piped command
        self.preBuffer      = []
        self.processBuffer  = []
        self.postBuffer     = []
        self.childs         = []
        self.executionCount = (0,0,0,)
        
    def addChild(self, child):
        self.childs.append(child)

    def executePreprocess(self, stack):
        self.executionCount = (self.executionCount[0]+1, self.executionCount[1], self.executionCount[2],)
        
        r = genericProcess( stack, self.preBuffer, self.command.preProcess)

        if len(self.childs) > 0:
            for i in range(0, len(self.childs)):
                c = self.childs[len(self.childs) - i - 1]
                c.preBuffer.extend(r)
                stack.extend(  [(c, 0,)] * len(r) )
        else:
            #the process has reach a leaf node
            stack.extend(  [(self, 1,)] * len(r) )
            self.processBuffer.extend(r)

    def executeProcess(self, stack):
        self.executionCount = (self.executionCount[0], self.executionCount[1]+1, self.executionCount[2],)
        r = genericProcess( stack, self.processBuffer, self.command.process)
        stack.extend(  [(self, 2,)] * len(r) )  
        self.postBuffer.extend(r)

    def executePostprocess(self, stack):
        self.executionCount = (self.executionCount[0], self.executionCount[1], self.executionCount[2]+1,)
    
        #execute process
        r = genericProcess( stack, self.postBuffer, self.command.postProcess)
        
        #do we have reach the root node, if not, forward the result to the parent
        if self.parent != None:
            stack.extend(  [(self.parent, 2,)] * len(r) )
            self.parent.postBuffer.extend(r)
        

