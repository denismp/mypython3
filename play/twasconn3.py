#!/bin/env jython
import sys, os, socket

import com.ibm.websphere.management.AdminClient.CONNECTOR_TYPE as AdminClient_CONNECTOR_TYPE
import com.ibm.websphere.management.AdminClient.CONNECTOR_HOST as AdminClient_CONNECTOR_HOST
import com.ibm.websphere.management.AdminClient.CONNECTOR_PORT as AdminClient_CONNECTOR_PORT
import com.ibm.websphere.management.AdminClient.CONNECTOR_TYPE_RMI as AdminClient_CONNECTOR_TYPE_RMI
import com.ibm.websphere.management.AdminClient.CONNECTOR_TYPE_SOAP as AdminClient_CONNECTOR_TYPE_SOAP
import com.ibm.websphere.management.AdminClient.CONNECTOR_SECURITY_ENABLED as AdminClient_CONNECTOR_SECURITY_ENABLED
import com.ibm.websphere.management.AdminClient.USERNAME as AdminClient_USERNAME
import com.ibm.websphere.management.AdminClient.PASSWORD as AdminClient_PASSWORD
import com.ibm.websphere.management.AdminClient.CONNECTOR_SOAP_CONFIG as AdminClient_CONNECTOR_SOAP_CONFIG
import com.ibm.websphere.management.AdminClient.CONNECTOR_AUTO_ACCEPT_SIGNER as AdminClient_CONNECTOR_AUTO_ACCEPT_SIGNER
from com.ibm.websphere.management.AdminClient import * 

import com.ibm.websphere.security.auth.WSLoginFailedException
import com.ibm.ws.security.util.InvalidPasswordDecodingException
import com.ibm.websphere.security.WebSphereRuntimePermission
import com.ibm.websphere.management.AdminClientFactory
import com.ibm.websphere.management.exception.ConnectorException
import com.ibm.websphere.management.exception.InvalidAdminClientTypeException
import com.ibm.ws.security.util.InvalidPasswordDecodingException
import com.ibm.ws.exception.WsException
import com.ibm.websphere.management.exception
from com.ibm.websphere.management.exception import *

import java.util.Properties
import java.lang.NullPointerException
import java.lang.NoClassDefFoundError
import java.io.FileInputStream

sslFileInput = "/apps/WebSphere7/was1/AppServer/profileTemplates/management/documents/properties/ssl.client.props"
sslProps = java.util.Properties()
sslFileStream = java.io.FileInputStream( sslFileInput )
sslProps.load( sslFileStream )
sslFileStream.close()

print str( sslProps )

wsAdminFileInput = java.io.FileInputStream( "/apps/WebSphere7/profiles/cell101N2/properties/wsadmin.properties" )
wsAdminProps = java.util.Properties()
wsAdminProps.load( wsAdminFileInput )
wsAdminFileInput.close()
print str( wsAdminProps )

fileInput = java.io.FileInputStream( "/apps/WebSphere7/profiles/cell101N2/properties/soap.client.props" )
props = java.util.Properties()
props.load( fileInput )
fileInput.close()
#print str( props )
props.setProperty( AdminClient_CONNECTOR_SOAP_CONFIG, "/apps/WebSphere7/profiles/cell101N2/properties/soap.client.props" )

host = wsAdminProps.getProperty( "com.ibm.ws.scripting.host" )
port = wsAdminProps.getProperty( "com.ibm.ws.scripting.port" )

props.setProperty( AdminClient_CONNECTOR_TYPE, AdminClient_CONNECTOR_TYPE_SOAP )
props.setProperty( AdminClient_CONNECTOR_SECURITY_ENABLED, "true" )
props.setProperty( AdminClient_CONNECTOR_AUTO_ACCEPT_SIGNER, "true" )
props.setProperty( AdminClient_CONNECTOR_HOST, host  )
props.setProperty( AdminClient_CONNECTOR_PORT, port )

props.setProperty( "javax.net.ssl.trustStorePassword", "WebAS" )
props.setProperty( "javax.net.ssl.keyStorePassword", "WebAS" )

props.setProperty( "javax.net.ssl.trustStore", "/apps/WebSphere7/profiles/cell101N2/etc/DummyServerTrustFile.jks" )
props.setProperty( "javax.net.ssl.keyStore", "/apps/WebSphere7/profiles/cell101N2/etc/DummyServerKeyFile.jks" )
print str( props )

try:
	ac = com.ibm.websphere.management.AdminClientFactory.createAdminClient( props )
except java.lang.Exception, e:
	print str( e )
except com.ibm.websphere.management.exception.ConnectorException, ce:
	print str( ce )
except com.ibm.ws.security.util.InvalidPasswordDecodingException, ipe:
	print str( ipe )
except com.ibm.websphere.management.exception.InvalidAdminClientTypeException, iac:
	print str( iac )
except com.ibm.ws.exception.WsException, we:
	print str( we )
except com.ibm.ws.util.PlatformHelper, ph:
	print str( ph )
except java.lang.NoClassDefFoundError, nc:
	print str( nc )
