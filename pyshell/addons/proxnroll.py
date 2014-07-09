#!/usr/bin/python
# -*- coding: utf-8 -*-

#Copyright (C) 2014  Jonathan Delvaux <pyshell@djoproject.net>

#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#any later version.

#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""def readAllFun(envi):
    ls = []
    for i in range(0,0xffff):
        apdu = ProxnrollAPDUBuilder.readBinary(i)
        apduAnswer = executeAPDU(envi,apdu)
        
        if apduAnswer.sw1 != 0x90 and apduAnswer.sw2 != 0x00:
            print "%x %x" % (apduAnswer.sw1, apduAnswer.sw2)
            break
        
        ls.append(apduAnswer)
    return ls

##############################################################################################################
##############################################################################################################
##############################################################################################################
#(CommandStrings=,preProcess=None,process=None,argChecker=None,postProcess=None,showInHelp=True):

try:
    Executer
except NameError:
    print "  No variable Executer found, this is an addon, it can't be executed alone"
    exit()
            
t = tokenValueArgChecker({"off":ProxnrollAPDUBuilder.colorOFF,"on":ProxnrollAPDUBuilder.colorON,"auto":ProxnrollAPDUBuilder.colorAUTO,"slow":ProxnrollAPDUBuilder.colorSLOW,"quick":ProxnrollAPDUBuilder.colorQUICK,"beat":ProxnrollAPDUBuilder.colorBEAT})
i0to60000 = IntegerArgChecker(0,60000)


Executer.addCommand(CommandStrings=["proxnroll","setlight"],                               preProcess=ProxnrollAPDUBuilder.setLedColorFun,process=executeAPDU,argChecker=DefaultArgsChecker([("red",t),("green",t),("yellow_blue",t)],2))
Executer.addCommand(CommandStrings=["proxnroll","setbuzzer"],                              preProcess=ProxnrollAPDUBuilder.setBuzzerDuration,process=executeAPDU,                                  argChecker=DefaultArgsChecker([("duration",i0to60000)],0))
Executer.addCommand(CommandStrings=["proxnroll","calypso","setspeed","9600"],              preProcess=ProxnrollAPDUBuilder.configureCalypsoSamSetSpeed9600,process=executeAPDU)
Executer.addCommand(CommandStrings=["proxnroll","calypso","setspeed","115200"],            preProcess=ProxnrollAPDUBuilder.configureCalypsoSamSetSpeed115200,process=executeAPDU)
Executer.addCommand(CommandStrings=["proxnroll","calypso","enabledigestupdate"],           preProcess=ProxnrollAPDUBuilder.configureCalypsoSamEnableInternalDigestUpdate,process=executeAPDU)
Executer.addCommand(CommandStrings=["proxnroll","calypso","disabledigestupdate"],          preProcess=ProxnrollAPDUBuilder.configureCalypsoSamDisableInternalDigestUpdate,process=executeAPDU)
                
Executer.addCommand(CommandStrings=["proxnroll","vendor"],                   preProcess=ProxnrollAPDUBuilder.getDataVendorName,process=executeAPDU                                   ,postProcess=resultHandlerAPDUAndConvertDataToString)
Executer.addCommand(CommandStrings=["proxnroll","product","name"],           preProcess=ProxnrollAPDUBuilder.getDataProductName,process=executeAPDU                                  ,postProcess=resultHandlerAPDUAndConvertDataToString)
Executer.addCommand(CommandStrings=["proxnroll","product","serialString"],   preProcess=ProxnrollAPDUBuilder.getDataProductSerialNumber,process=executeAPDU                          ,postProcess=resultHandlerAPDUAndConvertDataToString)
Executer.addCommand(CommandStrings=["proxnroll","product","usbidentifiel"],  preProcess=ProxnrollAPDUBuilder.getDataProductUSBIdentifier,process=executeAPDU                         ,postProcess=resultHandlerAPDUAndConvertDataToString)
Executer.addCommand(CommandStrings=["proxnroll","product","version"],        preProcess=ProxnrollAPDUBuilder.getDataProductVersion,process=executeAPDU                               ,postProcess=resultHandlerAPDUAndConvertDataToString)
Executer.addCommand(CommandStrings=["proxnroll","product","serial"],         preProcess=ProxnrollAPDUBuilder.getDataProductSerialNumber,process=executeAPDU   ,postProcess=resultHandlerAPDUAndPrintData)

Executer.addCommand(CommandStrings=["proxnroll","card","serial"],            preProcess=ProxnrollAPDUBuilder.getDataCardSerialNumber,process=executeAPDU                             ,postProcess=resultHandlerAPDUAndPrintData)
Executer.addCommand(CommandStrings=["proxnroll","card","ats"],               preProcess=ProxnrollAPDUBuilder.getDataCardATS,process=executeAPDU               ,postProcess=resultHandlerAPDUAndPrintData)
Executer.addCommand(CommandStrings=["proxnroll","card","completeIdentifier"],preProcess=ProxnrollAPDUBuilder.getDataCardCompleteIdentifier,process=executeAPDU,postProcess=resultHandlerAPDUAndPrintData)
Executer.addCommand(CommandStrings=["proxnroll","card","type"],              preProcess=ProxnrollAPDUBuilder.getDataCardType,process=executeAPDU              ,postProcess=ProxnrollAPDUBuilder.parseDataCardType)
Executer.addCommand(CommandStrings=["proxnroll","card","shortSerial"],       preProcess=ProxnrollAPDUBuilder.getDataCardShortSerialNumber,process=executeAPDU ,postProcess=resultHandlerAPDUAndPrintData)
Executer.addCommand(CommandStrings=["proxnroll","card","atr"],               preProcess=ProxnrollAPDUBuilder.getDataCardATR,process=executeAPDU               ,postProcess=printATR) #resultHandlerAPDUAndPrintData
Executer.addCommand(CommandStrings=["proxnroll","hardwareIdentifier"],       preProcess=ProxnrollAPDUBuilder.getDataHarwareIdentifier,process=executeAPDU     ,postProcess=resultHandlerAPDUAndPrintData)

Executer.addCommand(CommandStrings=["proxnroll","control","tracking","resume"],            preProcess=ProxnrollAPDUBuilder.slotControlResumeCardTracking,process=executeAPDU)
Executer.addCommand(CommandStrings=["proxnroll","control","tracking","suspend"],           preProcess=ProxnrollAPDUBuilder.slotControlSuspendCardTracking,process=executeAPDU)
Executer.addCommand(CommandStrings=["proxnroll","control","rffield","stop"],               preProcess=ProxnrollAPDUBuilder.slotControlStopRFField,process=executeAPDU)
Executer.addCommand(CommandStrings=["proxnroll","control","rffield","start"],              preProcess=ProxnrollAPDUBuilder.slotControlStartRFField,process=executeAPDU)
Executer.addCommand(CommandStrings=["proxnroll","control","rffield","reset"],              preProcess=ProxnrollAPDUBuilder.slotControlResetRFField,process=executeAPDU)

Executer.addCommand(CommandStrings=["proxnroll","control","t=cl","deactivation"],          preProcess=ProxnrollAPDUBuilder.slotControlTCLDeactivation,process=executeAPDU)
Executer.addCommand(CommandStrings=["proxnroll","control","t=cl","activation","a"],        preProcess=ProxnrollAPDUBuilder.slotControlTCLActivationTypeA,process=executeAPDU)
Executer.addCommand(CommandStrings=["proxnroll","control","t=cl","activation","b"],        preProcess=ProxnrollAPDUBuilder.slotControlTCLActivationTypeB,process=executeAPDU)
Executer.addCommand(CommandStrings=["proxnroll","control","t=cl","disable","next"],        preProcess=ProxnrollAPDUBuilder.slotControlDisableNextTCL,process=executeAPDU)
Executer.addCommand(CommandStrings=["proxnroll","control","t=cl","disable","every"],       preProcess=ProxnrollAPDUBuilder.slotControlDisableEveryTCL,process=executeAPDU)
Executer.addCommand(CommandStrings=["proxnroll","control","t=cl","enable"],                preProcess=ProxnrollAPDUBuilder.slotControlEnableTCLAgain,process=executeAPDU)
Executer.addCommand(CommandStrings=["proxnroll","control","t=cl","reset"],                 preProcess=ProxnrollAPDUBuilder.slotControlResetAfterNextDisconnectAndDisableNextTCL,process=executeAPDU)

Executer.addCommand(CommandStrings=["proxnroll","control","stop"],                         preProcess=ProxnrollAPDUBuilder.slotControlStop,process=executeAPDU)
Executer.addCommand(CommandStrings=["proxnroll","test"],                                   preProcess=ProxnrollAPDUBuilder.test,process=executeAPDU
                    ,argChecker=InfiniteArgsChecker("datas",hexaArgChecker(),[("expected_answer_size",IntegerArgChecker(0,255)),("delay_to_answer",IntegerArgChecker(0,63))])
                    ,postProcess=resultHandlerAPDUAndPrintDataAndSW)

typeAB = tokenValueArgChecker({"a":True,"b":False})
typeVolatile = tokenValueArgChecker({"volatile":True,"nonvolatile":False})
Executer.addCommand(CommandStrings=["proxnroll","mifare","loadkey"],                       preProcess=ProxnrollAPDUBuilder.loadKey,process=executeAPDU,                 
argChecker=DefaultArgsChecker([("KeyIndex",IntegerArgChecker(0,15)),("KeyName",stringArgChecker()),("isTypeA",typeAB),("InVolatile",typeVolatile)],2))
Executer.addCommand(CommandStrings=["proxnroll","mifare","authenticate"],                  preProcess=ProxnrollAPDUBuilder.generalAuthenticate,process=executeAPDU,     
argChecker=DefaultArgsChecker([("blockNumber",hexaArgChecker(0,0xFF)),("KeyIndex",IntegerArgChecker(0,15)),("isTypeA",typeAB),("InVolatile",typeVolatile)],2))

i = IntegerArgChecker()
#TODO add the expected argument to readBinary
Executer.addCommand(CommandStrings=["proxnroll","read"],                                   preProcess=ProxnrollAPDUBuilder.readBinary,process=executeAPDU,                 argChecker=DefaultArgsChecker([("address",i)],0),postProcess=resultHandlerAPDUAndPrintData)
Executer.addCommand(CommandStrings=["proxnroll","mifare","read"],                          preProcess=ProxnrollAPDUBuilder.mifareClassicRead,process=executeAPDU,          argChecker=DefaultArgsChecker([("blockNumber",hexaArgChecker()),("KeyName",stringArgChecker())],1),postProcess=resultHandlerAPDUAndPrintData)
Executer.addCommand(CommandStrings=["proxnroll","update"],                                 preProcess=ProxnrollAPDUBuilder.updateBinary,process=executeAPDU,               argChecker=InfiniteArgsChecker("datas",hexaArgChecker(),[("address",hexaArgChecker(0,0xFFFF))],defaultLimitChecker(0xFF)))

timeoutType = tokenValueArgChecker({"default":ProxnrollAPDUBuilder.timeoutDefault,
                                    "1ms":ProxnrollAPDUBuilder.timeout1ms,
                                    "2ms":ProxnrollAPDUBuilder.timeout2ms,
                                    "4ms":ProxnrollAPDUBuilder.timeout4ms,
                                    "8ms":ProxnrollAPDUBuilder.timeout8ms,
                                    "16ms":ProxnrollAPDUBuilder.timeout16ms,
                                    "32ms":ProxnrollAPDUBuilder.timeout32ms,
                                    "65ms":ProxnrollAPDUBuilder.timeout65ms,
                                    "125ms":ProxnrollAPDUBuilder.timeout125ms,
                                    "250ms":ProxnrollAPDUBuilder.timeout250ms,
                                    "500ms":ProxnrollAPDUBuilder.timeout500ms,
                                    "1s":ProxnrollAPDUBuilder.timeout1s,
                                    "2s":ProxnrollAPDUBuilder.timeout2s,
                                    "4s":ProxnrollAPDUBuilder.timeout4s})
                                    
protocoleType = tokenValueArgChecker({"default":ProxnrollAPDUBuilder.protocolType_ISO14443_TCL,
                                    "ISO14443A":ProxnrollAPDUBuilder.protocolType_ISO14443A,
                                    "ISO14443B":ProxnrollAPDUBuilder.protocolType_ISO14443B,
                                    "ISO15693":ProxnrollAPDUBuilder.protocolType_ISO15693,
                                    "ISO15693UID":ProxnrollAPDUBuilder.protocolType_ISO15693_WithUID,
                                    "ISO14443ANOCRC":ProxnrollAPDUBuilder.protocolType_ISO14443A_WithoutCRC,
                                    "ISO14443BNOCRC":ProxnrollAPDUBuilder.protocolType_ISO14443B_WithoutCRC,
                                    "ISO15693NOCRC":ProxnrollAPDUBuilder.protocolType_ISO15693_WithoutCRC})
                                    
redirectionType = tokenValueArgChecker({"main":ProxnrollAPDUBuilder.redirectionToMainSlot,
                                        "1":ProxnrollAPDUBuilder.redirectionTo1stSlot,
                                        "2":ProxnrollAPDUBuilder.redirectionTo2ndSlot,
                                        "3":ProxnrollAPDUBuilder.redirectionTo3rdSlot,
                                        "4":ProxnrollAPDUBuilder.redirectionTo4stSlot})
                                        
partialType = tokenValueArgChecker({"8":ProxnrollAPDUBuilder.lastByte_Complete_WithoutCRC,
                                        "1":ProxnrollAPDUBuilder.lastByte_With1bits_WithoutCRC,
                                        "2":ProxnrollAPDUBuilder.lastByte_With2bits_WithoutCRC,
                                        "3":ProxnrollAPDUBuilder.lastByte_With3bits_WithoutCRC,
                                        "4":ProxnrollAPDUBuilder.lastByte_With4bits_WithoutCRC,
                                        "5":ProxnrollAPDUBuilder.lastByte_With5bits_WithoutCRC,
                                        "6":ProxnrollAPDUBuilder.lastByte_With6bits_WithoutCRC,
                                        "7":ProxnrollAPDUBuilder.lastByte_With7bits_WithoutCRC})

Executer.addCommand(CommandStrings=["proxnroll","encapsulate","standard"],                 preProcess=ProxnrollAPDUBuilder.encapsulate,process=executeAPDU               ,argChecker=InfiniteArgsChecker("datas",hexaArgChecker(),[("protocolType",protocoleType),("timeoutType",timeoutType)],defaultLimitChecker(0xFF)),postProcess=resultHandlerAPDUAndPrintDataAndSW)
Executer.addCommand(CommandStrings=["proxnroll","encapsulate","redirection"],              preProcess=ProxnrollAPDUBuilder.encapsulate,process=executeAPDU               ,argChecker=InfiniteArgsChecker("datas",hexaArgChecker(),[("protocolType",redirectionType),("timeoutType",timeoutType)],defaultLimitChecker(0xFF)),postProcess=resultHandlerAPDUAndPrintDataAndSW)
Executer.addCommand(CommandStrings=["proxnroll","encapsulate","partial"],                  preProcess=ProxnrollAPDUBuilder.encapsulate,process=executeAPDU               ,argChecker=InfiniteArgsChecker("datas",hexaArgChecker(),[("protocolType",partialType),("timeoutType",timeoutType)],defaultLimitChecker(0xFF)),postProcess=resultHandlerAPDUAndPrintDataAndSW)
Executer.addCommand(CommandStrings=["proxnroll","mifare","update"],                        preProcess=ProxnrollAPDUBuilder.mifareClassifWrite,process=executeAPDU        ,argChecker=InfiniteArgsChecker("datas",hexaArgChecker(),[("blockNumber",hexaArgChecker()),("KeyName",stringArgChecker())],defaultLimitChecker(0xFF)))
Executer.addCommand(CommandStrings=["proxnroll","readall"],                                process=readAllFun,                                     postProcess=printByteListList)
"""
