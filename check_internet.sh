#!/bin/bash

# Server-URL
SERVER_URL="http://dein-server-ip:5000/update"

# Funktion, um zu prüfen, ob eine Internetverbindung besteht
check_internet() {
    wget -q --spider http://google.com

    if [ $? -eq 0 ]; then
        echo "Online"
    else
        echo "Offline"
    fi
}

# Funktion, um den Status an den Server zu senden
send_status() {
    STATUS=$(check_internet)
    curl -X POST -d "status=$STATUS" $SERVER_URL
}

# Skript alle 5 Minuten ausführen
while true; do
    send_status
    sleep 300
done
