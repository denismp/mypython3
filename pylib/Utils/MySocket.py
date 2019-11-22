#!/usr/bin/env jython
######################################################################################
##	MySocket.py
##
##	Python module deals with sockets.
######################################################################################
##
##	MODIFICATION HISTORY:
##	DATE		WHOM				DESCRIPTION
##	03/30/2011	Denis M. Putnam		Created.
######################################################################################
import re #@UnusedImport
import socket
from pylib.Utils.MyLogger import * #@UnusedWildImport
from pylib.Utils.MyUtils import * #@UnusedWildImport

class MySocket:
	"""
    MySocket class that deals with sockets.
    """

	##################################################################################
	#	__init__()
	#
	#	DESCRIPTION:
	#		Class initializer.
	#
	#	PARAMETERS:
	#		logger	    - instance of the pylib.Utils.MyLogger class.
	#
	#	RETURN:
	#		An instance of this class
	##################################################################################
	def __init__(self, hostname='', port=50007, logger=None):
		"""Class Initializer.
           PARAMETERS:
               hostname - name of the host.  Use default for the server side.
               port     - port number of the socket.
               logger   - instance of the pylib.Utils.MyLogger class.

           RETURN:
               An instance of this class
		"""
		self.logger			 = logger
		self.utils			 = MyUtils()
		self.hostname		 = hostname
		self.port			 = port
		self.mySocket		 = socket.socket( socket.AF_INET, socket.SOCK_STREAM )

	##################################################################################
	#Enddef
	##################################################################################

	##################################################################################
	#	bindAndListen()
	#
	#	DESCRIPTION:
	#		Bind and listen on the socket.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def bindAndListen(self):
		"""Bind and listen on the socket.  This is the server side.
        PARMETERS:
        """
		self.mySocket.bind( (self.hostname, self.port) )
		self.mySocket.listen( 1 )
	##################################################################################
	#Enddef
	##################################################################################
	
	##################################################################################
	#	connect()
	#
	#	DESCRIPTION:
	#		Connect to the socket.  This is the client side.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def connect(self):
		"""Connect to the socket.  This is the client side.
        PARMETERS:
        """
		self.mySocket.connect( (self.hostname, self.port) )
	##################################################################################
	#Enddef
	##################################################################################
	
	##################################################################################
	#	clientSend()
	#
	#	DESCRIPTION:
	#		Send data to the socket.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def clientSend(self, data):
		"""Send data to the socket.
        PARMETERS:
        	data - data to send.
        """
		self.mySocket.send( data )
	##################################################################################
	#Enddef
	##################################################################################
	
	##################################################################################
	#	clientReceive()
	#
	#	DESCRIPTION:
	#		Receive data from the socket.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def clientReceive(self, packetSize=2048):
		"""Receive data from the socket.
        PARMETERS:
        	packetSize - number of bytes to read per recv request.
        	
        RETURN:
        	( numBytesRead, data )
        """


		data  			= self.mySocket.recv( packetSize )
		numBytesRead	= len( data )
		return ( numBytesRead, data )
	##################################################################################
	#Enddef
	##################################################################################
	
	##################################################################################
	#	serverRead()
	#
	#	DESCRIPTION:
	#		Receive data from the socket.  This is the server side.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def serverRead(self, numBytesRequested, packetSize=2048):
		"""Receive data from the socket.  This is the server side.
        PARMETERS:
            numBytesRequested - total number of bytes to be read.
        	packetSize - number of bytes to read per recv request.
        RETURN:
        	( conn, data )
        """
		data = ""
		totalNumBytes = 0
		conn = None
		addr = None
		
		try:
			conn, addr = self.mySocket.accept()
		except KeyboardInterrupt, ke:
			self.logIt( __name__ + '.serverRead(): got keyboard interrupt.  ' + str( ke ) + "\n" )
			return ( None, None )
		self.logIt( __name__ + '.serverRead(): Connected by ' + str( addr ) + "\n" )
		
		while totalNumBytes < numBytesRequested:
			currentData = conn.recv( packetSize )
			if not currentData: 
				self.logIt( __name__ + '.serverRead(): Received no data\n' )
				return ( None, None )

			#conn.send(data)
			numBytes = len( currentData )
			totalNumBytes += numBytes
			data += currentData
			
		#conn.close()
		self.logIt( __name__ + '.serverRead(): Number of bytes received=' + str( len( data ) ) + "\n" )
		return ( conn, data )
	##################################################################################
	#Enddef
	##################################################################################
	
	##################################################################################
	#	serverRead()
	#
	#	DESCRIPTION:
	#		Receive data from the socket.  This is the server side.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def serverReadMsgNum(self, packetSize=2048):
		"""Receive data from the socket.  This is the server side.
        PARMETERS:
            numBytesRequested - total number of bytes to be read.
        	packetSize - number of bytes to read per recv request.
        RETURN:
        	( conn, data )
        """
		data = ""
		conn = None
		addr = None
		
		try:
			conn, addr = self.mySocket.accept()
			data = conn.recv( packetSize )
			if data is not None: 
				data = socket.ntohl(long( str( data ) ) )
		except KeyboardInterrupt, ke:
			self.logIt( __name__ + '.serverReadMsgNum(): got keyboard interrupt.  ' + str( ke ) + "\n" )
			return ( None, None )
		self.logIt( __name__ + '.serverReadMsgNum(): Connected by ' + str( addr ) + "\n" )
		
		self.logIt( __name__ + '.serverReadMsgNum(): Number of bytes received=' + str( len( str( data ) ) ) + "\n" )
		return ( conn, str( data ) )
	##################################################################################
	#Enddef
	##################################################################################
	
	##################################################################################
	#	serverSend()
	#
	#	DESCRIPTION:
	#		Receive data from the socket.  This is the server side.
	#
	#	PARAMETERS:
	#
	#	RETURN:
	##################################################################################
	def serverSend(self, conn, data):
		"""Send data to the socket.  This is the server side.
		   The caller is responsible for calling the conn.close().
        PARMETERS:
            conn - connection retrieved from a previous call to serverRead().
        	data - the data to be sent.
        RETURN:
        """
		if conn is not None and data is not None:
			numbytes = len( data )
			totalBytesSent	= 0
			bytesSent		= 0
			totalBytesSent = conn.send(data)
			while totalBytesSent < numbytes:
				bytesSent = conn.send(data[totalBytesSent:])
				totalBytesSent += bytesSent
		#conn.close()
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

		myAttrs = dir(self)
		for attr in myAttrs:
			#if re.search('__doc__', attr): continue
			#if re.search('__module__', attr): continue
			#if re.search('bound method', str(getattr(self, attr))): continue
			#if re.search('instance', str(getattr(self, attr))): continue
			if(debugOnly == True):
				self.debug("pylib.Utils.MySocket.logMySelf(): " + str(attr) + "=" + str(getattr(self, attr)) + "\n")
			else:
				self.logIt("pylib.Utils.MySocket.logMySelf(): " + str(attr) + "=" + str(getattr(self, attr)) + "\n")
			#Endif
		#Endfor
		#self.logEnv( debugOnly=debugOnly )

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

		if(self.logger): self.logger.logIt(msg)

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

		if(self.logger): self.logger.debug(msg)

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
		pass
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
	#
	#	RETURN:
	##################################################################################
	def __del__(self):
		"""Closes this instance."""
		self.closeMe()
	##################################################################################
	#Enddef
	##################################################################################

#####################################################################################
#Endclass
#####################################################################################

#########################################################################
#	For testing.
#########################################################################
def main():
	myLogger = MyLogger(LOGFILE="/tmp/MySocket.log", STDOUT=True, DEBUG=False)
	myObject = MySocket(logger=myLogger)
	myObject.logMySelf(debugOnly=False)
	myObject.bindAndListen()
	conn, data = myObject.serverRead(1, packetSize=1024)
	myObject.serverSend(conn, data)
	conn.close()

	myObject.closeMe();
	##################################################################################
	#Enddef
	##################################################################################

#########################################
#   End
#########################################
if __name__ == "__main__":
	main()
