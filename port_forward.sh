#!/bin/bash

# --- Step 1: Install the UPnP Command-Line Tool ---
echo "INFO: Updating package list and installing 'miniupnpc'..."
sudo apt update
sudo apt install -y miniupnpc

# Check if the installation was successful
if ! command -v upnpc &> /dev/null
then
    echo "ERROR: 'upnpc' command could not be found. Installation may have failed."
    exit 1
fi
echo "INFO: 'miniupnpc' installed successfully."
echo "----------------------------------------------------"


# --- Step 2: Find the Pi's Local IP Address ---
PI_IP=$(hostname -I | awk '{print $1}')

if [ -z "$PI_IP" ]; then
    echo "ERROR: Could not determine the Raspberry Pi's IP address."
    exit 1
fi
echo "INFO: Your Raspberry Pi's IP Address is: $PI_IP"
echo "----------------------------------------------------"


# --- Step 3: Attempt to Set Up Port Forwarding via UPnP ---
APP_NAME="RPi-SSH"
EXTERNAL_PORT=2222
INTERNAL_PORT=22
PROTOCOL="TCP"

echo "INFO: Attempting to add a new port forwarding rule..."
echo "  - Application: RPi-SSH"
echo "  - External Port: 2222"
echo "  - Internal Port: 22 (to Pi IP: $PI_IP)"
echo "  - Protocol: TCP"
echo ""

upnpc -e "$APP_NAME" -a "$PI_IP" "$INTERNAL_PORT" "$EXTERNAL_PORT" "$PROTOCOL"

echo "----------------------------------------------------"


# --- Step 4: Verify the Rule ---
echo "INFO: Checking router for active port forwarding rules..."
echo ""
upnpc -l

echo ""
echo "----------------------------------------------------"
echo "SUCCESS: The script has finished."
echo "If you see your rule listed above, it likely worked!"
echo ""
echo "IMPORTANT: If you see errors like 'No UPnP device found', UPnP is likely disabled on your router."
echo "You will need to set up the port forward manually in your router's admin page."
echo "----------------------------------------------------"