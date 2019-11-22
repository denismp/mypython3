#!/bin/ksh
set -x

LIST="

ConfigureMNEThread.py
ConfigureWASThread.py
ConfigWebServerThread.py
__init__.py
MakeNewFilesActiveThread.py
PostConfigThread.py
RunWasPostThread.py
StopRunnableProcessThread.py
"
cp $LIST /nfs/dist/dmp/amp/jython/pylib/MyThreads

cd ..
cp __init__.py /nfs/dist/dmp/amp/jython/pylib
