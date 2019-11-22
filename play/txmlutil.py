#!/bin/env jython
import sys, os, socket
#import com.dmp.amp.appcomponent.DomainApplicationComponentConfig
import com.dmp.amp.utility.XmlEncodingUtility
import java.lang.String

myxml = java.lang.String( "/nfs/home4/dmpapp/appd4ec/tmp/testData.xml" )
myutil = com.dmp.amp.utility.XmlEncodingUtility()
myobj = myutil.xmlFileToObject( myxml )
print dir( myobj )
print myobj.getTypeCode()
print myobj.getAppComponentIdentifier()
print myobj.getAppComponentName()
print myobj.getAppMnemonicCode()
print myobj.getPrimaryFilePath()
print myobj.getRuntimeFiles()
rtFiles = myobj.getRuntimeFiles()
print dir( rtFiles[0] )
