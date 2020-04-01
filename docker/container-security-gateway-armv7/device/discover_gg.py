# /*
# * Copyright 2010-2017 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# *
# * Licensed under the Apache License, Version 2.0 (the "License").
# * You may not use this file except in compliance with the License.
# * A copy of the License is located at
# *
# *  http://aws.amazon.com/apache2.0
# *
# * or in the "license" file accompanying this file. This file is distributed
# * on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
# * express or implied. See the License for the specific language governing
# * permissions and limitations under the License.
# */


import sys
import uuid
import logging
import argparse
from AWSIoTPythonSDK.core.greengrass.discovery.providers import DiscoveryInfoProvider
from AWSIoTPythonSDK.core.protocol.connection.cores import ProgressiveBackOffCore
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from AWSIoTPythonSDK.exception.AWSIoTExceptions import DiscoveryInvalidRequestException


MAX_DISCOVERY_RETRIES = 10

class gg:
    
    def __init__(self, endpoint, rootCAPath, privateKeyPath, certificatePath, thingName):
        self.__gg_client = None
        host = endpoint
        rootCAPath = rootCAPath
        self.privateKeyPath = privateKeyPath
        self.certificatePath = certificatePath


        # Configure logging
        self.logger = logging.getLogger("AWSIoTPythonSDK.core")
        self.logger.setLevel(logging.INFO)
        streamHandler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        streamHandler.setFormatter(formatter)
        self.logger.addHandler(streamHandler)

        # Progressive back off core
        backOffCore = ProgressiveBackOffCore()

        # Discover GGCs
        discoveryInfoProvider = DiscoveryInfoProvider()
        discoveryInfoProvider.configureEndpoint(host)
        discoveryInfoProvider.configureCredentials(rootCAPath, certificatePath, privateKeyPath)
        discoveryInfoProvider.configureTimeout(10)  # 10 sec

        retryCount = MAX_DISCOVERY_RETRIES
        discovered = False
        self.groupCA = None
        self.clientId = thingName
        self.coreInfo = None
        self.groupId = None
        while retryCount != 0:
            try:
                discoveryInfo = discoveryInfoProvider.discover(thingName)
                caList = discoveryInfo.getAllCas()
                coreList = discoveryInfo.getAllCores()

                # We only pick the first ca and core info
                self.groupId, ca = caList[0]
                self.coreInfo = coreList[0]
                self.logger.info("Discovered GGC: %s from Group: %s" % (self.coreInfo.coreThingArn, self.groupId))

                self.groupCA = self.groupId + "_CA_" + str(uuid.uuid4()) + ".crt"
                groupCAFile = open(self.groupCA, "w")
                groupCAFile.write(ca)
                groupCAFile.close()

                discovered = True
                break
            except DiscoveryInvalidRequestException as e:
                self.logger.error("Invalid discovery request detected!")
                self.logger.error("Type: %s" % str(type(e)))
                self.logger.error("Error message: %s" % e.message)
                self.logger.error("Stopping...")
                break
            except BaseException as e:
                self.logger.error("Error in discovery!")
                self.logger.error("Type: %s" % str(type(e)))
                self.logger.error("Error message: %s" % e.message)
                self.logger.error("\n%d/%d retries left\n" % (retryCount, MAX_DISCOVERY_RETRIES))
                self.logger.error("Backing off...\n")
                backOffCore.backOff()
            retryCount -= 1
            
        if not discovered:
            self.logger.error("Discovery failed after %d retries. Exiting...\n" % (MAX_DISCOVERY_RETRIES))
            sys.exit(-1)


    def client(self):
    
        # Iterate through all connection options for the core and use the first successful one
        myAWSIoTMQTTClient = AWSIoTMQTTClient(self.clientId)
        myAWSIoTMQTTClient.configureCredentials(self.groupCA, self.privateKeyPath, self.certificatePath)

        connected = False
        for connectivityInfo in self.coreInfo.connectivityInfoList:
            currentHost = connectivityInfo.host
            currentPort = connectivityInfo.port
            self.logger.info("Trying to connect to core at %s:%d" % (currentHost, currentPort))
            myAWSIoTMQTTClient.configureEndpoint(currentHost, currentPort)
            myAWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 128, 20)
            myAWSIoTMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
            myAWSIoTMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
            myAWSIoTMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
            myAWSIoTMQTTClient.configureMQTTOperationTimeout(30)  # 30 sec
            try:
                myAWSIoTMQTTClient.connect()
                connected = True
                break
            except BaseException as e:
                self.logger.error("Error in connect!")
                self.logger.error("Type: %s" % str(type(e)))
                self.logger.error("Error message: %s" % e.message)

        if not connected:
            self.logger.error("Cannot connect to core %s. Exiting..." % self.coreInfo.coreThingArn)
            sys.exit(-2)
    
        return myAWSIoTMQTTClient

def main():
    # Read in command-line parameters
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--endpoint", action="store", required=True, dest="host", help="Your AWS IoT custom endpoint")
    parser.add_argument("-r", "--rootCA", action="store", required=True, dest="rootCAPath", help="Root CA file path")
    parser.add_argument("-c", "--cert", action="store", dest="certificatePath", help="Certificate file path")
    parser.add_argument("-k", "--key", action="store", dest="privateKeyPath", help="Private key file path")
    parser.add_argument("-n", "--thingName", action="store", dest="thingName", help="Targeted thing name")
    
    args = parser.parse_args()
    host = args.host
    rootCAPath = args.rootCAPath
    certificatePath = args.certificatePath
    privateKeyPath = args.privateKeyPath
    thingName = args.thingName
  
    
    if not args.certificatePath or not args.privateKeyPath or not args.rootCAPath or not args.host or not args.thingName:
        print("discover_gg --help")
        exit(2)
    
    _gg = gg(host, rootCAPath, privateKeyPath, certificatePath, thingName)
    _gg.client()

if __name__ == '__main__':
    main()
