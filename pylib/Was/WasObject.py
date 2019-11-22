#!/usr/bin/env jython
######################################################################################
##	WasObject.py
##
##	Python module deals with WebSphere objects.
######################################################################################
##
##	MODIFICATION HISTORY:
##	DATE		WHOM				DESCRIPTION
##	11/11/2009	Denis M. Putnam		Created.
######################################################################################
import os, sys
import re
import socket
from array import array
from pylib.Utils.MyLogger import *
from pylib.Utils.MyUtils import *
from java.lang import String
from java.lang import NullPointerException
from java.lang import NoClassDefFoundError

class WasObject():
	"""WasObject class """

	##################################################################################
	#	__init__()
	#
	#	DESCRIPTION:
	#		Class initializer.
	#
	#	PARAMETERS:
	#		See below.
	#
	#	RETURN:
	#		An instance of this class
	##################################################################################
	def __init__(
				self, 
				objectName=None,
				logger=None
		):
		"""Class Initializer.
           PARAMETERS:
               objectName   - instance of the java.lang.String class that contains something like: "WebSphere:name=HelloWoldService1EAR,process=as_cell101a_01,platform=dynamicproxy,node=cell101N2,J2EEName=HelloWoldService1EAR,Server=as_cell101a_01,version=7.0.0.3,type=Application,mbeanIdentifier=cells/cell101/applications/HelloWoldService1EAR.ear/deployments/HelloWoldService1EAR/deployment.xml#ApplicationDeployment_1243014014001,cell=cell101,spec=1.0"
               logger         - instance of the pylib.Utils.MyLogger class.

           RETURN:
               An instance of this class
		"""
		self.logger			= logger
		self.objectName		= objectName
		self.debug( __name__ + ".__init__(): objectString=" + str( objectName.toString() ) + '\n' )
		self.parseData( str( objectName.toString() ) )
		self.logMySelf()
		self.validate()

	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	parseData()
	#
	#	DESCRIPTION:
	#		Parse the given data string and add the attribute/values to this object.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def parseData(self, dataString=None):
		"""Parse the given data string and add the attribute/values to this object.
           PARAMETERS:
               dataString - something like: "WebSphere:name=HelloWoldService1EAR,process=as_cell101a_01,platform=dynamicproxy,node=cell101N2,J2EEName=HelloWoldService1EAR,Server=as_cell101a_01,version=7.0.0.3,type=Application,mbeanIdentifier=cells/cell101/applications/HelloWoldService1EAR.ear/deployments/HelloWoldService1EAR/deployment.xml#ApplicationDeployment_1243014014001,cell=cell101,spec=1.0"

           RETURN:
               Nothing
		"""
		firstTime = True
		data = str( dataString ).split( "," )
		for pair in data:
			#print pair
			mykey, myvalue = pair.split( "=" )
			#print mykey
			#print myvalue
			if re.match( r'WebSphere.*', mykey ): mykey = "WebSphere_name"
			setattr( self, mykey, myvalue )
		#Endfor
	
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	validate()
	#
	#	DESCRIPTION:
	#		Validate the parameters and calculated values.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	#		True for valid.
	##################################################################################
	def validate(self):
		"""Validate the parameters and calculated values.
           PARAMETERS:

           RETURN:
               True for valid or False.
		"""
		rVal = False
		#return rVal
		return True

	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	logMySelf()
	#
	#	DESCRIPTION:
	#		Log myself.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def logMySelf(self, debugOnly=True):
		"""Log myself.
        PARMETERS:
            debugOnly is either True or False.  A value of True will only log if the
            logger's debug flag is set.
        """

		myAttrs = dir( self )
		for attr in myAttrs:
			try:
				#if re.search( '__doc__',  attr ): continue
				##if re.search( '__module__',  attr ): continue
				#if re.search( 'bound method', str( getattr( self, attr ) ) ): continue
				##if re.search( 'instance', str( getattr( self, attr ) ) ): continue
				if( debugOnly == True ):
					self.debug( __name__ + ".logMySelf(): " + str( attr ) + "=" + str( getattr( self, attr ) ) + "\n" )
				else:
					self.logIt( __name__ + ".logMySelf(): " + str( attr ) + "=" + str( getattr( self, attr ) ) + "\n" )
				#Endif
			except:
				continue
			#Endtry
		#Endfor
		#self.env.logMySelf( debugOnly=debugOnly )

	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	getAttributeKeys()
	#
	#	DESCRIPTION:
	#		Get the parsed attribute keys.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def getAttributeKeys(self):
		"""Get the parsed attribute keys.
        PARMETERS:
        RETURN:
            A list of the attributes.
        """

		rAttrs  = list()
		myAttrs = dir( self )
		for attr in myAttrs:
			try:
				if re.search( '__doc__',  attr ): continue
				if re.search( '__module__',  attr ): continue
				if re.search( 'bound method', str( getattr( self, attr ) ) ): continue
				if re.search( 'instance', str( getattr( self, attr ) ) ): continue
				#print "attr=" + '"' + str( attr ) + '"'
				rAttrs.append( str( attr ) )
				#print dir( rAttrs.tostring() )
			except:
				continue
			#Endtry
		#Endfor
		#for i in rAttrs:
		#	print i
		return rAttrs 
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	getValue()
	#
	#	DESCRIPTION:
	#		Get the parsed attribute value.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def getValue(self, attribute):
		"""Get the parsed attribute value.
        PARMETERS:
            attribute - the name of the attribute.
        RETURN:
            The value of the attribute.
        """
		try:
			return getattr( self, attribute )
		except:
			return "NONE"
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	printValues()
	#
	#	DESCRIPTION:
	#		Print the parsed attribute/value to the stdout.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def printValues(self):
		"""Print the parsed attribute/value pairs to the stdout.
        PARMETERS:
        RETURN:
        """
		ostr = str()
		for attr in self.getAttributeKeys():
			ostr = ostr + str( attr ) + '=' + str( self.getValue( attr ) ) + ',' 	
		print ostr

	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	logIt()
	#
	#	DESCRIPTION:
	#		Write a message to the log and possibly stdout.
	#
	#	PARAMETERS:
	#		msg - what you want to log.
	#
	#	RETURN:
	##################################################################################
	def logIt(self, msg):
		"""Write a message to the log and possibly stdout."""

		if( self.logger ): self.logger.logIt( msg )

	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	debug()
	#
	#	DESCRIPTION:
	#		Write a message to the log and possibly stdout.
	#
	#	PARAMETERS:
	#		msg - what you want to log.
	#
	#	RETURN:
	##################################################################################
	def debug(self, msg):
		"""Write a message to the log and possibly stdout."""

		if( self.logger ): self.logger.debug( msg )

	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	closeMe()
	#
	#	DESCRIPTION:
	#		Closes this instance.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def closeMe(self):
		"""Closes this instance."""
		self.debug( __name__ + ".closeMe(): called.\n" )
	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	__del__()
	#
	#	DESCRIPTION:
	#		Closes this instance.
	#
	#	PARAMETERS:
	#	RETURN:
	##################################################################################
	def __del__(self):
		"""Closes this instance."""
		#self.logIt( __name__ + ".__del__(): called.\n" )
		self.closeMe()
	##################################################################################
	#Enddef
	##################################################################################

######################################################################################
#Endclass
######################################################################################

#########################################################################
#	For testing.
#########################################################################
def main():
	myLogger	= MyLogger( LOGFILE="/tmp/WasObject.log", STDOUT=True, DEBUG=True )
	#myObject	= WasObject( objectName="WebSphere:name=HelloWoldService1EAR,process=as_cell101a_01,platform=dynamicproxy,node=cell101N2,J2EEName=HelloWoldService1EAR,Server=as_cell101a_01,version=7.0.0.3,type=Application,mbeanIdentifier=cells/cell101/applications/HelloWoldService1EAR.ear/deployments/HelloWoldService1EAR/deployment.xml#ApplicationDeployment_1243014014001,cell=cell101,spec=1.0", logger=myLogger )
	#ar = myObject.getAttributeKeys()
	#for attr in ar:
	#	#print attr
	#	print attr + '=' + str( myObject.getValue( attr ) )
	#myObject.printValues()
	##################################################################################
	#Enddef
	##################################################################################

#########################################
#   End
#########################################
if __name__ == "__main__":
	main()

