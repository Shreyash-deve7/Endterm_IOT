import redis
import json
import sys
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

REDIS_HOST = "localhost"
REDIS_PORT = 6379
DEVICE_ID = "sensor_01"
NUM_READINGS = 10

def get_redis_connection():
    try:
        r = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            decode_responses=True,
            socket_connect_timeout=5
        )
        r.ping()
        return r
    except redis.ConnectionError as e:
        logger.error(f"Failed to connect to Redis: {e}")
        return None

def fetch_and_analyze(r, device_id, num_readings):
    list_key = f"sensors:{device_id}"
    
    try:
        readings = r.lrange(list_key, 0, num_readings - 1)
    except redis.RedisError as e:
        logger.error(f"Redis error: {e}")
        return
    
    if not readings:
        logger.warning(f"No readings found for device {device_id}")
        return
    
    temperatures = []
    
    print(f"\n=== Last {len(readings)} Readings for {device_id} ===")
    print("-" * 60)
    
    for idx, reading in enumerate(readings, 1):
        try:
            data = json.loads(reading)
            temp = data.get("value")
            ts = data.get("ts")
            
            if temp is None:
                logger.warning(f"Invalid reading data: {data}")
                continue
            
            temperatures.append(temp)
            dt = datetime.fromtimestamp(ts) if ts else "N/A"
            print(f"{idx}. Temperature: {temp}°C | Timestamp: {dt}")
        
        except json.JSONDecodeError:
            logger.error(f"Failed to parse reading: {reading}")
    
    if temperatures:
        avg_temp = sum(temperatures) / len(temperatures)
        max_temp = max(temperatures)
        min_temp = min(temperatures)
        
        print("-" * 60)
        print(f"Average Temperature: {avg_temp:.2f}°C")
        print(f"Max Temperature: {max_temp}°C")
        print(f"Min Temperature: {min_temp}°C")
        print(f"Readings Analyzed: {len(temperatures)}")

def main():
    r = get_redis_connection()
    if not r:
        logger.critical("Cannot proceed without Redis connection")
        sys.exit(1)
    
    fetch_and_analyze(r, DEVICE_ID, NUM_READINGS)

if __name__ == "__main__":
    main()
