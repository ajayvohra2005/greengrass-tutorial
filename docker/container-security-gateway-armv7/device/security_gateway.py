'''
/*
 * Copyright 2010-2020 Amazon.com, Inc. or its affiliates. All Rights Reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the "License").
 * You may not use this file except in compliance with the License.
 * A copy of the License is located at
 *
 *  http://aws.amazon.com/apache2.0
 *
 * or in the "license" file accompanying this file. This file is distributed
 * on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
 * express or implied. See the License for the specific language governing
 * permissions and limitations under the License.
 */
 '''

import sys, traceback
import logging
import time
import getopt

import json


from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient


class security_gateway:
    
    def __init__(self, deviceId, endpoint, rootCAPath, privateKeyPath, certificatePath):
        
        # Configure logging
        self.logger = logging.getLogger("AWSIoTPythonSDK.core")
        self.logger.setLevel(logging.DEBUG)
        streamHandler = logging.StreamHandler()
        
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        streamHandler.setFormatter(formatter)
        self.logger.addHandler(streamHandler)
        
        self.reported = {}
        self.reported['owner'] = "none"
        self.reported['status'] = "inactive"
        self.reported['mode'] = "none"
        
        self.desired = None
        self.delta = None
         
        self.__initIotClient(deviceId, endpoint, rootCAPath, privateKeyPath, certificatePath)
        
    def __initIotClient(self, devieId, endpoint, rootCAPath, privateKeyPath, certificatePath):

        # Init AWSIoTMQTTClient
        self.iot_client = None
        self.client_id=str(deviceId)
        
        
        self.iot_client = AWSIoTMQTTClient(self.client_id)
        self.iot_client.configureEndpoint(endpoint, 8883)
        self.iot_client.configureCredentials(rootCAPath, privateKeyPath, certificatePath)

        # AWSIoTMQTTClient connection configuration
        self.iot_client.configureAutoReconnectBackoffTime(1, 128, 20)
        self.iot_client.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
        self.iot_client.configureDrainingFrequency(2)  # Draining: 2 Hz
        self.iot_client.configureConnectDisconnectTimeout(10)  # 10 sec
        self.iot_client.configureMQTTOperationTimeout(30)  # 30 sec
        
        self.update_topic = "$aws/things/" + self.client_id + "/shadow/update"
        self.get_topic = "$aws/things/" + self.client_id + "/shadow/get"
        self.client_state = "INIT"
        self.logger.info(self.client_state)

    def connect(self):
        # Connect and subscribe to AWS IoT
        self.client_state = "CONNECT"
        self.logger.info(self.client_state)
        self.iot_client.connect()
        time.sleep(2)
       
        update_accepted_topic="$aws/things/" + self.client_id + "/shadow/update/accepted"
        update_rejected_topic="$aws/things/" + self.client_id + "/shadow/update/rejected"
        get_accepted_topic="$aws/things/" + self.client_id + "/shadow/get/accepted"
        get_rejected_topic="$aws/things/" + self.client_id + "/shadow/get/rejected"
        update_delta_topic="$aws/things/" + self.client_id + "/shadow/update/delta"
        update_documents_topic="$aws/things/" + self.client_id + "/shadow/update/documents"
        
        self.iot_client.subscribe(update_documents_topic, 1, self.updateDocumentsCallback)
        self.iot_client.subscribe(update_delta_topic, 1, self.updateDeltaCallback)
        self.iot_client.subscribe(update_rejected_topic, 1, self.updateRejectedCallback)
        self.iot_client.subscribe(update_accepted_topic, 1, self.updateAcceptedCallback)
        self.iot_client.subscribe(get_rejected_topic, 1, self.getRejectedCallback)
        self.iot_client.subscribe(get_accepted_topic, 1, self.getAcceptedCallback)
        
        
    def getState(self):
        self.client_state = "GET_PENDING"
        self.logger.info(self.client_state)
        self.iot_client.publish(self.get_topic, "", 1)
        
    def reportState(self):
        
        msg = {}
        state={}
        
        state['reported']=self.reported
        msg['state']=state
        
        json_msg = json.dumps(msg)
        self.client_state = "UPDATE_PENDING"
        self.logger.info(self.client_state)
        self.iot_client.publish(self.update_topic, json_msg, 1)
          
    def updateDeltaCallback(self, client, userdata, message):
        try:	
            msg=message.payload
            self.handleUpdateDeltaMessage(msg)
            self.client_state = "DELTA"
            self.logger.info(self.client_state)
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            
            traceback.print_tb(exc_traceback, limit=20, file=sys.stdout)
            
    def updateDocumentsCallback(self, client, userdata, message):
        try:	
            msg=message.payload
            self.handleUpdateDocumentsMessage(msg)
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            
            traceback.print_tb(exc_traceback, limit=20, file=sys.stdout)
    
    
    def getRejectedCallback(self, client, userdata, message):
        try:	
            msg=message.payload
            self.handleGetRejectedMessage(msg)
            if self.client_state == "GET_PENDING":
                self.client_state = "GET_REJECTED"
                self.logger.info(self.client_state)
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_tb(exc_traceback, limit=20, file=sys.stdout)
            
    def getAcceptedCallback(self, client, userdata, message):
        try:	
            msg=message.payload
            self.handleGetAcceptedMessage(msg)
            if self.client_state == "GET_PENDING":
                self.client_state = "GET_ACCEPTED"
                self.logger.info(self.client_state)
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_tb(exc_traceback, limit=20, file=sys.stdout)
    
    def updateRejectedCallback(self, client, userdata, message):
        try:	
            msg=message.payload
            self.handleUpdateRejectedMessage(msg)
            if self.client_state == "UPDATE_PENDING":
                self.client_state = "UPDATE_REJECTED"
                self.logger.info(self.client_state)
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_tb(exc_traceback, limit=20, file=sys.stdout)
            
    def updateAcceptedCallback(self, client, userdata, message):
        try:	
            msg=message.payload
            self.handleUpdateAcceptedMessage(msg)
            if self.client_state == "UPDATE_PENDING":
                self.client_state = "UPDATE_ACCEPTED"
                self.logger.info(self.client_state)
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_tb(exc_traceback, limit=20, file=sys.stdout)
  
    
    def getAttrValue(self, dict, key):
        value = None
        try:
            value = dict[key]
        except KeyError:
            pass
        
        return value
    
    
    def handleUpdateRejectedMessage(self, message):
        self.logger.info("Enter handleUpdateRejectedMessage")
       
        try:
            msg=json.loads(message)
            self.logger.info(msg)
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_tb(exc_traceback, limit=20, file=sys.stdout)
        finally:
            self.logger.info("Exit handleUpdateRejectedMessage")
            
    def handleUpdateAcceptedMessage(self, message):
        self.logger.info("Enter handleUpdateAcceptedMessage")
       
        try:
            msg=json.loads(message)
            self.logger.info(msg)
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            
            traceback.print_tb(exc_traceback, limit=20, file=sys.stdout)
        finally:
            self.logger.info("Exit handleUpdateAcceptedMessage")
            
    def handleGetRejectedMessage(self, message):
        self.logger.info("Enter handleGetRejectedMessage")
       
        try:
            msg=json.loads(message)
            self.logger.info(msg)
            if msg['code'] == 404:
                self.reportState()
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            
            traceback.print_tb(exc_traceback, limit=20, file=sys.stdout)
        finally:
            self.logger.info("Exit handleGetRejectedMessage")
    
 
    def handleGetAcceptedMessage(self, message):
        self.logger.info("Enter handleGetAcceptedMessage")
       
        try:
            msg=json.loads(message)
            state = msg['state']
            self.reported = self.getAttrValue(state, "reported")
            self.desired = self.getAttrValue(state, "desired")
            self.delta = self.getAttrValue(state, "delta")
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_tb(exc_traceback, limit=20, file=sys.stdout)
        finally:
            self.logger.info("Exit handleGetAcceptedMessage")
    
    def handleUpdateDocumentsMessage(self, message):
        self.logger.info("Enter handleUpdateDocumentsMessage")
       
        try:
            msg=json.loads(message)
            self.logger.info( msg)
            
            current = msg["current"]
            state = current["state"]
            self.reported = self.getAttrValue(state, "reported")
            self.desired = self.getAttrValue(state, "desired")
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_tb(exc_traceback, limit=20, file=sys.stdout)
        finally:
            self.logger.info("Exit handleUpdateDocumentsMessage")
            
    def handleUpdateDeltaMessage(self, message):
        self.logger.info("Enter handleUpdateDeltaMessage")
       
        try:
            msg=json.loads(message)
            self.logger.info(msg)
            self.delta = msg["state"]  
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_tb(exc_traceback, limit=20, file=sys.stdout)
        finally:
            self.logger.info("Exit handleUpdateDeltaMessage")

    def processDelta(self):
        self.logger.info("Enter processDelta")
        try:
            if self.delta:
                if self.reported:
                    for key in self.delta:
                        self.reported[key] = self.delta[key]
                else:
                    self.reported = self.delta
        
                self.reportState()
            self.client_state = "SYNCED"
            self.logger.info(self.client_state)
            self.logger.info("Exit processDelta")
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_tb(exc_traceback, limit=20, file=sys.stdout)
        finally:
            self.logger.info("Exit handleUpdateDeltaMessage")
            
    def doSecurityChecks(self):
        self.logger.info("do security checks")
        time.sleep(2)
        
    def start(self):
        self.connect()
        
        self.getState()
        while self.client_state != "GET_ACCEPTED":
            time.sleep(2)
        self.processDelta()
        
        while True:
            self.doSecurityChecks()
            if self.client_state == "DELTA":
                self.processDelta()
        
# Usage
usageInfo = """Usage:

Use certificate based mutual authentication:
python security_gateway.py -e <endpoint> -r <rootCAFilePath> -c <certFilePath> -k <privateKeyFilePath> -d <deviceId>


Type "python security_gateway.py -h" for available options.
"""
# Help info
helpInfo = """-e, --endpoint
	Your AWS IoT custom endpoint
-r, --rootCA
	Root CA file path
-c, --cert
	Certificate file path
-k, --key
	Private key file path
-d, --device
	Device Id
-h, --help
	Help information
"""

# Read in command-line parameters
useWebsocket = False
endpoint = ""
rootCAPath = ""
certificatePath = ""
privateKeyPath = ""
deviceId=""

try:
    opts, args = getopt.getopt(sys.argv[1:], "hwe:k:c:r:d:f:", ["help", "endpoint=", "key=","cert=","rootCA=", "device="])
    if len(opts) == 0:
        raise getopt.GetoptError("No input parameters!")
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print(helpInfo)
            exit(0)
        if opt in ("-e", "--endpoint"):
            endpoint = arg
        if opt in ("-r", "--rootCA"):
            rootCAPath = arg
        if opt in ("-c", "--cert"):
            certificatePath = arg
        if opt in ("-k", "--key"):
            privateKeyPath = arg
        if opt in ("-d", "--device"):
            deviceId = arg
except getopt.GetoptError:
    print(usageInfo)
    exit(1)

# Missing configuration notification
missingConfiguration = False
if not endpoint:
    print("Missing '-e' or '--endpoint'")
    missingConfiguration = True
    
if not rootCAPath:
    print("Missing '-r' or '--rootCA'")
    missingConfiguration = True

if not certificatePath:
    print("Missing '-c' or '--cert'")
    missingConfiguration = True
    
if not privateKeyPath:
    print("Missing '-k' or '--key'")
    missingConfiguration = True
    
if not deviceId:
    print("Missing '-d' or '--device'")
    missingConfiguration = True
    
if not deviceId:
    print("Missing '-d' or '--device'")
    missingConfiguration = True
       
if missingConfiguration:
    exit(2)

security_gateway = security_gateway(deviceId, endpoint, rootCAPath, privateKeyPath, certificatePath)
security_gateway.start()

