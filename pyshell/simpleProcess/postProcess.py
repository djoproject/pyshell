from decorator import shellMethod
from argchecker import stringArgChecker,ArgChecker,environmentChecker,listArgChecker
from arg import environment

#@listdecorator("result",stringArgChecker())
#@environmentdecorator("printer","printer")
@shellMethod(  printer=environmentChecker("printer",environment),  result=listArgChecker(stringArgChecker())  )
def stringListResultHandler(printer,result):
    #if result == None or len(result) == 0:
    #    Executer.printOnShell("no item available")
    #    return
        
    for i in result:
        printer.printOnShell(i)

#@argument("result")
#@environmentdecorator("printer","printer")
@shellMethod(printer=environmentChecker("printer",environment),result=ArgChecker())
def printResultHandler(printer,result=None):
    if result != None:
        printer.printOnShell(str(result))

#@listdecorator("result",ArgChecker())
#@environmentdecorator("printer","printer")
@shellMethod(printer=environmentChecker("printer",environment),result=listArgChecker(ArgChecker()))
def listResultHandler(printer,result):
    #if result == None or len(result) == 0:
    #    Executer.printOnShell("no item available")
    #    return

    for i in result:
        printer.printOnShell(str(i))
        
#@listdecorator("result",ArgChecker())
#@environmentdecorator("printer","printer")
@shellMethod(printer=environmentChecker("printer",environment),result=listArgChecker(ArgChecker()))
def listFlatResultHandler(printer,result):
    #if result == None or len(result) == 0:
    #    Executer.printOnShell("no item available")
    #    return

    s = ""
    for i in result:
        s += str(i) + " "
    
    printer.printOnShell(s)
