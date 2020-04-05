#!/bin/sh

set -e

# Check to see if root CA file exists, download if not
if [ ! -f ./root-CA.crt ]; then
  printf "\nDownloading AWS IoT Root CA certificate from AWS...\n"
  curl https://www.amazontrust.com/repository/AmazonRootCA1.pem > root-CA.crt
fi

# Check to see if AWS Device SDK for Python exists, download if not
if [ ! -d ./aws-iot-device-sdk-python ]; then
  printf "\nCloning the AWS SDK...\n"
  git clone https://github.com/aws/aws-iot-device-sdk-python.git
  cd aws-iot-device-sdk-python
  sudo python3 setup.py install 
  cd ..
fi

# set thing name below
THING=
# set Thing endpoint below
ENDPOINT=

# Place the Thing crypto files in ./thing folder.
# This shell script assumes the crypto files 
# aee named thing-certificate.pem.crt, thing-private.pem.key
# and thing-public.pem.key
CERT=thing/thing-certificate.pem.crt
KEY=thing/thing-private.pem.key
ROOTCA=root-CA.crt

python3 security_gateway.py -e  $ENDPOINT -r $ROOTCA -c $CERT  -k  $KEY  -d $THING
