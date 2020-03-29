import greengrasssdk
import requests
import logging
import json

logger = logging.getLogger()
logger.setLevel(logging.INFO)
ggclient=greengrasssdk.client("iot-data")

def lambda_handler(event, context):
    resp = requests.get('http://localhost/')
    resp_json = resp.json()
    logger.info(str(resp_json))
   
    thingName='raspi-gg-superior'
    shadow_update = f'$aws/things/{thingName}/shadow/update'

    msg={}
    msg['state']={"reported": resp_json}
    json_msg=json.dumps(msg)
    logger.info(json_msg)

    ggclient.publish(topic=shadow_update, qos=0, payload=json_msg)
    return