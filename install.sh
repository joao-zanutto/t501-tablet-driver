#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
INSTALL_PATH="/usr/local/bin/tablet-init.py"
UDEV_RULE="/etc/udev/rules.d/99-tablet-t501.rules"

if [ "$(id -u)" -ne 0 ]; then
    echo "This script must be run as root (use sudo)"
    exit 1
fi

echo "Installing tablet-init.py to $INSTALL_PATH..."
cp "$SCRIPT_DIR/tablet-init.py" "$INSTALL_PATH"
chmod +x "$INSTALL_PATH"

echo "Installing udev rule to $UDEV_RULE..."
cat > "$UDEV_RULE" << 'EOF'
# Initialize T501 tablet full drawing area on plug-in
ACTION=="add", SUBSYSTEM=="hidraw", ATTRS{idVendor}=="08f2", ATTRS{idProduct}=="6811", RUN+="/usr/local/bin/tablet-init.py"
EOF

echo "Reloading udev rules..."
udevadm control --reload-rules

echo "Done. Unplug and replug the tablet to activate."
