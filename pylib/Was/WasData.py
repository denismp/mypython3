#!/usr/bin/env jython
######################################################################################
##	WasData.py
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
from pylib.Was.AdminClient import *
from java.lang import String
from java.lang import NullPointerException
from java.lang import NoClassDefFoundError
from javax.management import ObjectName

class WasData():
	"""WasData class """

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
				logger=None
		):
		"""Class Initializer.
           PARAMETERS:
               logger         - instance of the pylib.Utils.MyLogger class.

           RETURN:
               An instance of this class
		"""
		self.logger			= logger
		self.objectNames	= list()
		self.sortedObjectNames = list()
		self.attributes		= list()
		self.myutils		= MyUtils()
		self.logMySelf()
		self.validate()

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
	#	queryWAS()
	#
	#	DESCRIPTION:
	#		Add the given WasObject instance to this container.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	#		A list of javax.management.ObjectName's.
	##################################################################################
	def queryWAS(self,adminClient,query="WebSphere:*"):
		"""Add the given WasObject instance to this container.
           PARAMETERS:
               adminClient - an instance of the pylib.Was.AdminClient class
               query       - something like: WebSphere:*:type=Server,* or *:node=Node1,type=Server,* or *:type=JVM,process=server1,node=Node1,* or *:process=server1,* or *:process=server1,node=Node1,* or any combination of 
                             type    The resource type that the MBean represents
                             name    The name identifier for the individual instance of the MBean
                             cell    The name of the cell in which the MBean is executing
                             node    The name of the node in which the MBean is executing
                             process The name of the process in which the MBean is executing

           RETURN:
               A list of javax.management.ObjectName's.
		"""
		self.objectNames = list()
		try:
			#objName         = ObjectName( "WebSphere:*" )
			objName         = ObjectName( query )

			objNameSet      = adminClient.connection.queryNames( objName, None )
			#print dir( objNameSet )

			iter = objNameSet.iterator()
			while iter.hasNext():
				myObject = iter.next()
				#self.objectNames.append( ObjectName( myObject.toString() ) )
				#print dir( myObject )
				self.objectNames.append( myObject )
			#Endwhile
			#self.sortData() # Too slow here.  Do it only when asked.
		except Exception, e:
			self.logIt( __name__ +  ".queryWAS(): " + str( e ) + "\n" )
			return list() # an empty list
		return self.objectNames
	##################################################################################
	#Enddef
	##################################################################################

	#######################################################
	#	sortData()
	#
	#	DESCRIPTION:
	#		Sort the ObjectName data.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	#		a sorted array
	#######################################################
	def sortData(self):
		"""Sort the ObjectName data."""
		self.debug( __name__ + ".sortData(): Started..." + '\n' )
		wArr = list()
		tObjectNames = list()
		self.sortedObjectNames = list()
		dStr = ""
		for data in self.objectNames:
			dStr = data.toString()
			#self.logIt( __name__ + ".sortData(): dStr=" + str( dStr ) + '\n' )
			wArr.append( dStr )
		#Endfor
		wArr.sort()
		for item in wArr:
			for objectName in self.objectNames:
				if str( item ) == str( objectName.toString() ):
					self.sortedObjectNames.append( objectName )
				#Endif
			#Endfor
		#Endfor
		self.debug( __name__ + ".sortData(): Finished." + '\n' )
		return self.sortedObjectNames
	#######################################################
	#	Enddef
	#######################################################

	#######################################################
	#	getAllPossibleAttributes()
	#
	#	DESCRIPTION:
	#		Sort the ObjectName data.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	#		a sorted array
	#######################################################
	def getAllPossibleAttributes(self):
		"""Sort the ObjectName data."""
		rAr = list()
		for data in self.objectNames:
			attrs = str( data.toString() ).split( ',' )
			for things in attrs:
				name, value = things.split( '=' )
				if re.match( r'WebSphere:.*', str( name ) ):
					rAr.append( "WebSphereObject" )
				else:
					rAr.append( name )
				#Endif
			#Endif
		#Endif
		myutils = MyUtils()
		rAr = myutils.uniquer( rAr )
		rAr.sort()
		self.attributes = rAr
		return self.attributes
	#######################################################
	#	Enddef
	#######################################################

	#######################################################
	#	writeData()
	#
	#	DESCRIPTION:
	#		write the given list of ObjectNames to the given file
	#
	#	PARAMETERS:
	#
	#	RETURN:
	#######################################################
	def writeData(self,fileName):
		"""Write the data."""
		self.sortData()

		#################################################
		#	Set up the header.
		#################################################
		header = ""
		attrs = self.getAllPossibleAttributes()
		alen  = len( attrs )
		i = 0
		for attr in self.getAllPossibleAttributes():
			if i < alen - 1:
				header += attr + ","	
			else:
				header += attr + "\n"
			i += 1
		#Endif
		try:
			oFH = open( fileName, 'w' )
			oFH.write( header )

			#############################################
			#	Create an array of NONE values.
			#############################################
			ar = list()
			for i in range( 0,alen ):
				ar.append( 'NONE' )
			#Endif

			##################################################
			#	Process all the data.
			##################################################
			for data in self.sortedObjectNames:

				##############################################
				#	Get the data and match the values to the
				#	header columns and store the values
				#	into the proper index of the array.
				##############################################
				elements = str( data ).split( ',' )
				for element in elements:
					name, value = str( element ).split( '=' )
					i = 0
					for col in attrs:
						if col == "WebSphereObject" and re.match( r'WebSphere:.*', name ):
							ar[i] = str( name + '=' + value )
						if col == name:
							ar[i] = value
						#Endif
						i += 1
					#Endif
				#Endfor

				##############################################
				#	Build the row to be written.
				##############################################
				ostr = ""
				i = 0
				for value in ar:
					if i < alen - 1:
						ostr += value + ","	
					else:
						ostr += value + "\n"
					i += 1
				#Endif

				#	Write it.
				oFH.write( ostr  )

				#############################################
				#	Reset the array of NONE values
				#	for the next row.
				#############################################
				ar = list()
				for i in range( 0,alen ):
					ar.append( 'NONE' )
				#Endif
			#Endfor
			oFH.close()
		except Exception, e:
			self.logIt( __name__ + ".writeData(): " + str( e ) + "\n" )
			raise
		#Endtry
	#######################################################
	#	Enddef
	#######################################################

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
	myLogger	= MyLogger( LOGFILE="/tmp/WasData.log", STDOUT=True, DEBUG=True )
	#adminObject = AdminClient( logger=myLogger, hostname="dilabvirt31-v1" )
	adminObject	= AdminClient( logger=myLogger, hostname="dilabvirt31-v1", cellName='cellA' )
	myclient	= None
	try:
		myclient = adminObject.createSOAPDefault()
	except:
		myLogger.logIt( "main(): Unable to connect to the AdminClient().  Make sure that the WebSphere Server Manager is running.\n" )
		raise	
	wasDataObject	= WasData( logger=myLogger )
	wasDataObject.queryWAS( myclient, query="WebSphere:*" )
	#print dir( wasDataObject.objectNames[0] )
	#print str( wasDataObject.objectNames[0].toString() )
	wasDataObject.writeData( "/nfs/home4/dmpapp/appd4ec/tmp/wastest2.csv" )
	for data in wasDataObject.sortedObjectNames:
		myLogger.logIt( str( data.toString() ) + '\n' )
	#Endfor
	myattrs = wasDataObject.getAllPossibleAttributes()
	for attr in wasDataObject.attributes:
		myLogger.logIt( attr + '\n' )
	#Endif
	wasDataObject.closeMe()
	adminObject.closeMe()
	##################################################################################
	#Enddef
	##################################################################################

#########################################
#   End
#########################################
if __name__ == "__main__":
	main()

