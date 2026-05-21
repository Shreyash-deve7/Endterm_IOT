from kafka import KafkaProducer
import sys

def main():
    topic = "app-logs"
    log_file = "app.log"

    producer = KafkaProducer(
        bootstrap_servers="localhost:9092",
        value_serializer=lambda v: v.encode("utf-8")
    )

    try:
        with open(log_file, "r") as f:
            for line in f:
                line = line.strip()
                if line:
                    producer.send(topic, line)
                    print("Sent:", line)
    except FileNotFoundError:
        print("Error: the file '" + log_file + "' was not found.")
        sys.exit(1)

    producer.flush()
    producer.close()
    print("Done sending all log lines.")

if __name__ == "__main__":
    main()