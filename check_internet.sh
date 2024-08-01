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

# Funktion, um die öffentliche IP-Adresse zu ermitteln
get_public_ip() {
    curl -s http://checkip.amazonaws.com
}

# Funktion, um den Netzwerkverkehr zu messen
get_traffic() {
    # Nimm an, dass eth0 das Netzwerkinterface ist
    RX_BYTES=$(ifconfig eth0 | grep 'RX bytes' | awk '{print $2}' | cut -d':' -f2)
    TX_BYTES=$(ifconfig eth0 | grep 'TX bytes' | awk '{print $6}' | cut -d':' -f2)
    echo "$RX_BYTES $TX_BYTES"
}

# Funktion, um Systeminformationen zu sammeln
get_system_info() {
    HOSTNAME=$(hostname)
    IP_ADDRESS=$(hostname -I | awk '{print $1}')
    PUBLIC_IP=$(get_public_ip)
    UPTIME=$(uptime -p)
    LOAD=$(uptime | awk -F 'load average:' '{ print $2 }')
    MEMORY=$(free -m | grep Mem | awk '{ print $3 "/" $2 " MB" }')
    DISK=$(df -h / | grep / | awk '{ print $3 "/" $2 }')
    TRAFFIC=$(get_traffic)
    RX_BYTES=$(echo $TRAFFIC | awk '{print $1}')
    TX_BYTES=$(echo $TRAFFIC | awk '{print $2}')

    echo "hostname=$HOSTNAME&ip=$IP_ADDRESS&public_ip=$PUBLIC_IP&status=$(check_internet)&uptime=$UPTIME&load=$LOAD&memory=$MEMORY&disk=$DISK&rx_bytes=$RX_BYTES&tx_bytes=$TX_BYTES"
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
