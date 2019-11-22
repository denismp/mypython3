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
from com.ibm.websphere.management.AdminClient import * 
import com.ibm.ws.util.PlatformHelper
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

fileInput = java.io.FileInputStream( "/apps/WebSphere7/profiles/cell101N2/properties/soap.client.props" )
props = java.util.Properties()
props.load( fileInput )
print str( props )
props.setProperty( AdminClient_CONNECTOR_TYPE, AdminClient_CONNECTOR_TYPE_SOAP )
props.setProperty( AdminClient_CONNECTOR_SECURITY_ENABLED, "false" )
props.setProperty( AdminClient_CONNECTOR_HOST, "dilabvirt31-v1" )
#props.setProperty( AdminClient_CONNECTOR_PORT, "11700" )
#props.setProperty( AdminClient_CONNECTOR_PORT, "8879" )
props.setProperty( AdminClient_CONNECTOR_PORT, "8880" )

props.setProperty( AdminClient_USERNAME, "was7admin" )
props.setProperty( AdminClient_PASSWORD, "was7adm1n" )
#props.setProperty( AdminClient_PASSWORD, "{xor}KD4saT47Mm4x" )

#props.setProperty( "javax.net.ssl.trustStore", "/apps/WebSphere6/profiles/cell103N2/etc/ClientTrust.jks" )
#props.setProperty( "javax.net.ssl.keyStore", "/apps/WebSphere6/profiles/cell103N2/etc/ClientKey.jks" )
#props.setProperty( "javax.net.ssl.trustStorePassword", "WebAS" )
#props.setProperty( "javax.net.ssl.keyStorePassword", "WebAS" )

#props.setProperty( "com.ibm.ssl.trustStore", "/apps/WebSphere6/profiles/cell103N2/etc/ClientTrust.jks" )
#props.setProperty( "com.ibm.ssl.keyStore", "/apps/WebSphere6/profiles/cell103N2/etc/ClientKey.jks" )
#props.setProperty( "com.ibm.ssl.trustStorePassword", "{xor}MissbzEzJg\=\=" )
#props.setProperty( "com.ibm.ssl.keyStorePassword", "{xor}MissbzEzJg\=\=" )
#props.setProperty( "com.ibm.ssl.protocol", "SSL" )
#props.setProperty( "com.ibm.ssl.trustStoreType", "JKS" )
#props.setProperty( "com.ibm.ssl.keyStoreType", "JKS" )

print AdminClient_CONNECTOR_TYPE
print AdminClient_CONNECTOR_HOST
print AdminClient_CONNECTOR_PORT
print AdminClient_USERNAME
print AdminClient_PASSWORD
print AdminClient_CONNECTOR_TYPE_RMI
print AdminClient_CONNECTOR_TYPE_SOAP
print AdminClient_CONNECTOR_SECURITY_ENABLED
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
