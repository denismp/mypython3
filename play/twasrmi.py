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

sslFile = "file:/apps/WebSphere7/profiles/cell101Dmgr/properties/ssl.client.props"
sasFile = "file:/apps/WebSphere7/profiles/cell101Dmgr/properties/sas.client.props"
ibmsoapFile = "file:/apps/WebSphere7/profiles/cell101Dmgr/properties/soap.client.props"

props = java.util.Properties()

props.setProperty( AdminClient_CONNECTOR_TYPE, AdminClient_CONNECTOR_TYPE_SOAP )
props.setProperty( AdminClient_CONNECTOR_HOST, "dilabvirt31-v1"  )
props.setProperty( AdminClient_CONNECTOR_PORT, "9809" )
props.setProperty( AdminClient_CONNECTOR_PORT, "8879" )
props.setProperty( AdminClient_USERNAME, "was7admin" )
props.setProperty( AdminClient_PASSWORD, "was7adm1n" )
props.setProperty( "com.ibm.CORBA.ConfigURL", sasFile )
props.setProperty( "com.ibm.SSL.ConfigURL", sslFile )
props.setProperty( "com.ibm.SOAP.ConfigURL", ibmsoapFile )
props.setProperty( "java.security.auth.login.config", "/apps/WebSphere7/profiles/cell101Dmgr/properties/wsjaas_client.conf" )
props.setProperty( "was.install.root", "/apps/WebSphere7/was1/AppServer" )
props.setProperty( "user.install.root", "/apps/WebSphere7/profiles/cell101Dmgr" )
props.setProperty( "was.repository.root", "/apps/WebSphere7/profiles/cell101Dmgr/config" )
props.setProperty( "local.cell", "cell101" )
props.setProperty( "local.node", "cell101Manager" )

print str( props )

try:
	ac = com.ibm.websphere.management.AdminClientFactory.createAdminClient( props )
except java.lang.Exception, e:
	print str( e )
except com.ibm.websphere.management.exception.ConnectorException, ce:
	print str( ce )
	traceback.print_stack()
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
