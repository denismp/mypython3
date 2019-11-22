#!/bin/ksh
set -x

LIST="
AdminClient.py
AppManagementService.py
AppManager.py
AttributeUtils.py
AuthAliasManager.py
ClusterReport.py
ConfigService.py
DataSourcesManager.py
EndPointManager.py
__init__.py
JavaProcessDefEnvManager.py
JavaVirtualMachineManager.py
JDBCProviderManager.py
NotificationListener.py
PMIServiceManager.py
ProcessExecutionManager.py
SessionManager.py
TemplateListManager.py
Utils.py
VirtualHostManager.py
WasCommonOps.py
WasData.py
WasEnvironment.py
WasObject.py
WasOps.py
WasProperties.py
WASServerClusterTasks.py
WasSession.py
ApplicationClassLoaderPolicyManager.py
LibraryRefManager.py
ThreadPoolManager.py
StreamRedirectManager.py
WilyManager.py
BootStrapPortManager.py
SoapPortManager.py
ServerWeightsManager.py
AppServerManager.py
"
cp $LIST /nfs/dist/dmp/amp/jython/pylib/Was

cd ..
cp __init__.py /nfs/dist/dmp/amp/jython/pylib
