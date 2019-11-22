#!/bin/env jython
import sys, os, socket
import com.dmp.was.admin.service.WASAdminClient
import com.ibm.websphere.management.configservice.ConfigServiceProxy
import com.ibm.websphere.management.application.AppManagementProxy
import com.ibm.websphere.management.Session
import java.lang.NullPointerException
import java.lang.NoClassDefFoundError
#import javax.management.JMRuntimeException
import com.ibm.websphere.management.exception.ConfigServiceException
import com.ibm.websphere.security.WebSphereRuntimePermission
import com.ibm.websphere.security.auth.WSLoginFailedException
import com.ibm.ws.security.util.InvalidPasswordDecodingException
wasAdminClient				= None
try:
	#wasAdminClient			= com.dmp.was.admin.service.WASAdminClient()
	#wasAdminClient			= com.dmp.was.admin.service.WASAdminClient( "dilabvirt31-v1", "was7admin", "was7adm1n", None )
	wasAdminClient			= com.dmp.was.admin.service.WASAdminClient( "dilabvirt31-v1", None, None, None )
	myclient				= wasAdminClient.createRMIDefault()
	#myclient				= wasAdminClient.createSOAPDefault()
	print "Connection successful!"
	#wasAdminClient.printResults()
	#results				= wasAdminClient.getResults()
	#print results
	#print dir( wasAdminClient )
	#wasAdminClient.printResults()
	configServiceProxy		= com.ibm.websphere.management.configservice.ConfigServiceProxy( myclient )
	#print "CONFIG"
	#print dir( configServiceProxy )

	appManagementJMXProxy	= com.ibm.websphere.management.application.AppManagementProxy.getJMXProxyForClient( myclient )
	session					= com.ibm.websphere.management.Session( "was7admin", False )
	sessionID				= session.getSessionId()
	#configServiceProxy.save( session, False )
	print "sessionID=" + str( sessionID )
	#configServiceProxy.discard( session )

	print "SUCCESS"

except com.ibm.websphere.management.exception.ConfigServiceException, cfge:
	print "FAILED"
	print str( cfge )
except com.ibm.websphere.management.exception.ConnectorException, ce:
	print "FAILED"
	print str( ce )
except Exception, e:
	print "FAILED"
	print str( e )
except BaseException, be:
	print "FAILED"
	print str( be )
except BaseException, be:
	print "FAILED"
	print str( be )
except java.lang.NoClassDefFoundError, ne:
	print "FAILED"
	print str( ne )

print "COMPLETE"
