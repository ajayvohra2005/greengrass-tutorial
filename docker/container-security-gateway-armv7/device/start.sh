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

ENDPOINT=
DEVICE=

CERT=${DEVICE}/${DEVICE}-certificate.pem.crt
KEY=${DEVICE}/${DEVICE}-private.pem.key
ROOTCA=root-CA.crt

python3 security_gateway.py -e  $ENDPOINT -r $ROOTCA -c $CERT  -k  $KEY  -d $DEVICE
