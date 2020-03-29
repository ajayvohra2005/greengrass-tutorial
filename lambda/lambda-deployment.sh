#!/bin/bash

if [ ! $# -gt 1 ]; 
then 
    echo "usage: $0 <lambda-name> pkg1 [pkg2 ... pkgN]"
    exit 0
fi

dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
pip3 install virtualenv
python3 -m virtualenv $1 
source $1/bin/activate
pip3 install "${@:2}" 
pkgs=$(find . | grep  -E 'lib/python3.[0-9]+/site-packages$')
cd ${pkgs} && zip -r ${dir}/$1.zip "${@:2}" 
deactivate
