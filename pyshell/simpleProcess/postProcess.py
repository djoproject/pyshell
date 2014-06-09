from pyshell.arg.decorator import shellMethod
from pyshell.arg.argchecker  import stringArgChecker,ArgChecker,listArgChecker

#@listdecorator("result",stringArgChecker())
#@environmentdecorator("printer","printer")
@shellMethod(result=listArgChecker(stringArgChecker())  )
def stringListResultHandler(result):
    for i in result:
        print(i)

#@argument("result")
#@environmentdecorator("printer","printer")
@shellMethod(result=ArgChecker())
def printResultHandler(result=None):
    if result != None:
        print(str(result))

#@listdecorator("result",ArgChecker())
#@environmentdecorator("printer","printer")
@shellMethod(result=listArgChecker(ArgChecker()))
def listResultHandler(result):
    for i in result:
        print(str(i))
        
#@listdecorator("result",ArgChecker())
#@environmentdecorator("printer","printer")
@shellMethod(result=listArgChecker(ArgChecker()))
def listFlatResultHandler(result):
    s = ""
    for i in result:
        s += str(i) + " "
    
    print(s)
