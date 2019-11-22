#!/usr/bin/ksh
set -x
find ./ -name "*.py" -print | xargs dos2unix 
