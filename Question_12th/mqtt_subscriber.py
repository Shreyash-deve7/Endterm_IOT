import paho.mqtt.client as mqtt
import redis
import json
import logging
import sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BROKER_HOST = "localhost"
BROKER_PORT = 1883
TOPIC = "sensors/temperature"
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_MAX_READINGS = 100

redis_conn = None
mqtt_client = None

def connect_redis():
    try:
        r = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            decode_responses=True,
            socket_connect_timeout=5
        )
        r.ping()
        logger.info(f"Connected to Redis at {REDIS_HOST}:{REDIS_PORT}")
        return r
    except redis.ConnectionError as e:
        logger.error(f"Redis connection failed: {e}")
        return None

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logger.info(f"Connected to MQTT broker at {BROKER_HOST}:{BROKER_PORT}")
        client.subscribe(TOPIC)
        logger.info(f"Subscribed to topic: {TOPIC}")
    else:
        logger.error(f"Failed to connect to broker, return code {rc}")

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        device_id = payload.get("device_id", "unknown")
        list_key = f"sensors:{device_id}"
        
        redis_conn.lpush(list_key, json.dumps(payload))
        redis_conn.ltrim(list_key, 0, REDIS_MAX_READINGS - 1)
        
        current_length = redis_conn.llen(list_key)
        logger.info(f"Stored - Key: {list_key} | Data: {payload} | List size: {current_length}")
    
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON received: {msg.payload}")
    except redis.RedisError as e:
        logger.error(f"Redis error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error processing message: {e}")

def on_disconnect(client, userdata, rc):
    if rc != 0:
        logger.warning(f"Unexpected MQTT disconnection {rc}")

def main():
    global redis_conn, mqtt_client
    
    redis_conn = connect_redis()
    if not redis_conn:
        logger.critical("Cannot start without Redis connection")
        sys.exit(1)
    
    mqtt_client = mqtt.Client(client_id="subscriber_01")
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    mqtt_client.on_disconnect = on_disconnect
    
    try:
        mqtt_client.connect(BROKER_HOST, BROKER_PORT, keepalive=60)
    except Exception as e:
        logger.error(f"Failed to connect to MQTT broker: {e}")
        sys.exit(1)
    
    try:
        logger.info("Starting subscriber loop...")
        mqtt_client.loop_forever()
    except KeyboardInterrupt:
        logger.info("Shutting down subscriber...")
    except Exception as e:
        logger.error(f"Unexpected error in loop: {e}")
    finally:
        mqtt_client.disconnect()
        logger.info("Subscriber stopped")

if __name__ == "__main__":
    main()
