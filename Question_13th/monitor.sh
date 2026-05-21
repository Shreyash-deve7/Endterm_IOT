

LOG_FILE="monitor.log"
CONSUMER="consumer.py"

while true
do
    if pgrep -f "$CONSUMER" > /dev/null
    then
        echo "$(date '+%Y-%m-%d %H:%M:%S') - Consumer is running."
    else
        echo "$(date '+%Y-%m-%d %H:%M:%S') - Consumer not found. Restarting it." >> "$LOG_FILE"
        python3 "$CONSUMER" &
    fi
    sleep 30
done
