#!/bin/bash

# Cron Setup Script for No-IP DDNS Updater
# This script sets up automatic No-IP updates every 5 minutes

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UPDATER_SCRIPT="$SCRIPT_DIR/noip-updater.sh"

echo "Setting up No-IP DDNS updater cron job..."

# Check if updater script exists
if [ ! -f "$UPDATER_SCRIPT" ]; then
    echo "ERROR: noip-updater.sh not found at $UPDATER_SCRIPT"
    exit 1
fi

# Make sure the updater script is executable
chmod +x "$UPDATER_SCRIPT"

# Create cron job entry
CRON_ENTRY="*/5 * * * * $UPDATER_SCRIPT >/dev/null 2>&1"

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -q "$UPDATER_SCRIPT"; then
    echo "Cron job already exists for No-IP updater"
else
    # Add cron job
    (crontab -l 2>/dev/null; echo "$CRON_ENTRY") | crontab -
    echo "Cron job added: $CRON_ENTRY"
fi

echo "No-IP DDNS updater cron job setup completed"
echo "The updater will run every 5 minutes"
echo ""
echo "To view current cron jobs: crontab -l"
echo "To remove the cron job: crontab -e (then delete the line)"
echo ""
echo "Make sure to edit noip-updater.sh with your No-IP credentials before the first run!"

