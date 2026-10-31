#!/bin/bash

FILE="./docker-compose.yml"
GATEWAY=$(ip route show default | awk '{print $3}')
HOST_IP=$(ip route get "$GATEWAY" | awk -v ORS="" '{print $5}')

sed -i "s/__HOST__/"$HOST_IP"/g" "$FILE"

echo "Address for the proxy: https://homelab."$HOST_IP".sslip.io" 
