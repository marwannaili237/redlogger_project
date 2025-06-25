#!/bin/bash

# No-IP Dynamic DNS Updater Script for Redlogger
# This script updates your No-IP hostname with your current public IP address

# Configuration
NOIP_USERNAME="your_noip_username"
NOIP_PASSWORD="your_noip_password"
NOIP_HOSTNAME="your-domain.ddns.net"

# Log file
LOG_FILE="/var/log/noip-updater.log"

# Function to log messages
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

# Function to get current public IP
get_public_ip() {
    # Try multiple services to get public IP
    IP=$(curl -s https://ipinfo.io/ip 2>/dev/null)
    if [ -z "$IP" ]; then
        IP=$(curl -s https://icanhazip.com 2>/dev/null)
    fi
    if [ -z "$IP" ]; then
        IP=$(curl -s https://ifconfig.me 2>/dev/null)
    fi
    echo "$IP"
}

# Function to get current IP from No-IP
get_noip_ip() {
    nslookup "$NOIP_HOSTNAME" | grep -A1 "Name:" | tail -1 | awk '{print $2}'
}

# Function to update No-IP
update_noip() {
    local current_ip="$1"
    local response
    
    response=$(curl -s -u "$NOIP_USERNAME:$NOIP_PASSWORD" \
        "https://dynupdate.no-ip.com/nic/update?hostname=$NOIP_HOSTNAME&myip=$current_ip")
    
    case "$response" in
        "good"*)
            log_message "SUCCESS: IP updated to $current_ip"
            return 0
            ;;
        "nochg"*)
            log_message "INFO: IP unchanged ($current_ip)"
            return 0
            ;;
        "nohost")
            log_message "ERROR: Hostname not found"
            return 1
            ;;
        "badauth")
            log_message "ERROR: Invalid username/password"
            return 1
            ;;
        "badagent")
            log_message "ERROR: Bad user agent"
            return 1
            ;;
        "!donator")
            log_message "ERROR: Feature not available for free accounts"
            return 1
            ;;
        "abuse")
            log_message "ERROR: Account blocked for abuse"
            return 1
            ;;
        *)
            log_message "ERROR: Unknown response: $response"
            return 1
            ;;
    esac
}

# Main execution
main() {
    log_message "Starting No-IP DDNS update check"
    
    # Check if configuration is set
    if [ "$NOIP_USERNAME" = "your_noip_username" ] || [ "$NOIP_PASSWORD" = "your_noip_password" ] || [ "$NOIP_HOSTNAME" = "your-domain.ddns.net" ]; then
        log_message "ERROR: Please configure your No-IP credentials in this script"
        exit 1
    fi
    
    # Get current public IP
    current_ip=$(get_public_ip)
    if [ -z "$current_ip" ]; then
        log_message "ERROR: Could not determine public IP address"
        exit 1
    fi
    
    log_message "Current public IP: $current_ip"
    
    # Get current No-IP hostname IP
    noip_ip=$(get_noip_ip)
    log_message "Current No-IP hostname IP: $noip_ip"
    
    # Update if IPs are different
    if [ "$current_ip" != "$noip_ip" ]; then
        log_message "IP addresses differ, updating No-IP..."
        if update_noip "$current_ip"; then
            log_message "No-IP update completed successfully"
        else
            log_message "No-IP update failed"
            exit 1
        fi
    else
        log_message "IP addresses match, no update needed"
    fi
    
    log_message "No-IP DDNS update check completed"
}

# Run main function
main "$@"

