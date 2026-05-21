import paho.mqtt.client as mqtt
import json
import time
import logging
from datetime import datetime
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BROKER_HOST = "localhost"
BROKER_PORT = 1883
TOPIC = "sensors/temperature"
DEVICE_ID = "sensor_01"
PUBLISH_INTERVAL = 2

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logger.info(f"Connected to broker {BROKER_HOST}:{BROKER_PORT}")
    else:
        logger.error(f"Failed to connect, return code {rc}")

def on_publish(client, userdata, mid):
    logger.debug(f"Message published successfully with MID: {mid}")

def on_disconnect(client, userdata, rc):
    if rc != 0:
        logger.warning(f"Unexpected disconnection {rc}")

def main():
    client = mqtt.Client(client_id=DEVICE_ID)
    client.on_connect = on_connect
    client.on_publish = on_publish
    client.on_disconnect = on_disconnect
    
    try:
        client.connect(BROKER_HOST, BROKER_PORT, keepalive=60)
    except Exception as e:
        logger.error(f"Connection error: {e}")
        return
    
    client.loop_start()
    
    try:
        while True:
            temp_value = 25.0 + random.uniform(-2, 2)
            payload = {
                "device_id": DEVICE_ID,
                "value": round(temp_value, 1),
                "ts": int(datetime.now().timestamp())
            }
            
            result = client.publish(TOPIC, json.dumps(payload))
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                logger.info(f"Published: {payload}")
            else:
                logger.warning(f"Publish failed with code: {result.rc}")
            
            time.sleep(PUBLISH_INTERVAL)
    
    except KeyboardInterrupt:
        logger.info("Shutting down publisher...")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        client.loop_stop()
        client.disconnect()
        logger.info("Publisher stopped")

if __name__ == "__main__":
    main()
