from kafka import KafkaConsumer

def main():
    topic = "app-logs"
    output_file = "errors_only.log"

    consumer = KafkaConsumer(
        topic,
        bootstrap_servers="localhost:9092",
        auto_offset_reset="earliest",
        group_id="log-error-group",
        value_deserializer=lambda v: v.decode("utf-8")
    )

    print("Listening for messages on topic:", topic)

    for message in consumer:
        line = message.value
        if "error" in line.lower():
            with open(output_file, "a") as f:
                f.write(line + "\n")
            print("Error line saved:", line)

if __name__ == "__main__":
    main()