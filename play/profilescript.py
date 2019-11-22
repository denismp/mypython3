#Get cell name
import sys
print( dir( AdminControl ) )
print( dir( AdminConfig ) )
print( dir( AdminApp ) )
cellName = AdminControl.getCell()
print( "Cell name = " + cellName )
apps = AdminApp.list().splitlines()
print( apps )
for app in apps:
	#print( "app=" + app )
	argString = 'type=Application,name=' + app + ',*'
	#print( "argString=" + argString )
	appObj = AdminControl.completeObjectName( argString )
	if( appObj != ''):
		appStatus = 'running'
	else:
		appStatus = 'stopped'
	#Endif
	print( 'Application:' + app + '=' + appStatus )
#Endfor

sys.exit(0)
