#!/bin/ksh
set -x

LIST="
ConfigureMNE.py
ConfigureWAS.py
ConfigWebServers.py
__init__.py
MakeNewFilesActive.py
PostConfig.py
RunWasPost.py
StopAllRunnableProcesses.py
"
cp $LIST /nfs/dist/dmp/amp/jython/pylib/DeploymentTasks

cd ..
cp __init__.py /nfs/dist/dmp/amp/jython/pylib
