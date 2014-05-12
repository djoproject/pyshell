   #TODO ces methodes doivent se retrouver dans le module standardShell (il faut le créer)
    """def addCommand(self,CommandStrings,preProcess=None,process=None,postProcess=None,showInHelp=True):
        #build the command name
        name = " ".join(CommandStrings)
        
        #the helping message will be the message of the starting point
        if preProcess != None :
            helpMsg = preProcess.__doc__
        elif process != None:
            helpMsg = process.__doc__
        elif postProcess != None:
            helpMsg = postProcess.__doc__
        else:
            helpMsg = "this command do nothing"
        
        #build the command
        c = UniCommand(name,helpMsg,preProcess,process,postProcess,showInHelp)
        
        #add the command into the tries
        try:
            self.levelTries.insert(CommandStrings,c)
            return c
        except triesException as e:
            print self.printOnShell(str(e))
            return None"""
            
    """def addMultiCommand(self,CommandStrings,helpMessage,showInHelp=True):
        #build the command name
        name = " ".join(CommandStrings)
        
        #create the command 
        c = MultiCommand(name,helpMessage,showInHelp)
        
        #add the command into the tries
        try:
            self.levelTries.insert(CommandStrings,c)
            return c
        except triesException as e:
            print self.printOnShell(str(e))
            return None"""
            
    """def addAlias(self,CommandStrings,AliasCommandStrings):
        #pas aussi simple
            #on doit pouvoir gerer des alias avec des arguments fixe
        
        #commande speciale
            #contient le path vers la commande
            #les arguments ou une partie des arguments
        
        #TODO CommandStrings can't contain special token : >, >>, |, ...
        
        #TODO find the command in the tree
        
        #TODO build alias command
        
        #TODO insert in tree
        
        pass #TODO"""
