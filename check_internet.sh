#!/bin/bash

# Server-URL
SERVER_URL="http://45.149.78.188:8000/update"

# Funktion, um zu prüfen, ob eine Internetverbindung besteht
check_internet() {
    wget -q --spider http://google.com
    if [ $? -eq 0 ]; then
        echo "Online"
    else
        echo "Offline"
    fi
}

# Funktion, um Systeminformationen zu sammeln
get_system_info() {
    HOSTNAME=$(hostname)
    IP_ADDRESS=$(hostname -I | awk '{print $1}')
    UPTIME=$(uptime -p)
    LOAD=$(uptime | awk -F 'load average:' '{ print $2 }')
    MEMORY=$(free -m | grep Mem | awk '{ print $3 "/" $2 " MB" }')
    DISK=$(df -h / | grep / | awk '{ print $3 "/" $2 }')

    echo "hostname=$HOSTNAME&ip=$IP_ADDRESS&status=$(check_internet)&uptime=$UPTIME&load=$LOAD&memory=$MEMORY&disk=$DISK"
}

# Funktion, um den Status an den Server zu senden
send_status() {
    SYSTEM_INFO=$(get_system_info)
    curl -X POST -d "$SYSTEM_INFO" $SERVER_URL
}

# Skript alle 5 Minuten ausführen
while true; do
    send_status
    sleep 300
done
