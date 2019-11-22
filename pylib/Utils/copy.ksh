#!/bin/ksh
set -x

LIST="
Environment.py
__init__.py
MyLogger.py
MyUtils.py
StatusCookie.py
"
cp $LIST /nfs/dist/dmp/amp/jython/pylib/Utils

cd ..
cp __init__.py /nfs/dist/dmp/amp/jython/pylib
