[app]

title = Redlogger
package.name = redlogger
package.domain = org.redlogger
source.dir = .
source.include_exts = py,png,jpg,kv,atlas

version = 0.1

requirements = python3,kivy,requests,pyjnius

orientation = portrait

# Android specific permissions
android.permissions = \ 
    INTERNET,\ 
    ACCESS_NETWORK_STATE,\ 
    ACCESS_WIFI_STATE,\ 
    CHANGE_WIFI_STATE,\ 
    ACCESS_FINE_LOCATION,\ 
    ACCESS_COARSE_LOCATION,\ 
    READ_EXTERNAL_STORAGE,\ 
    WRITE_EXTERNAL_STORAGE,\ 
    RECORD_AUDIO,\ 
    CAMERA,\ 
    READ_PHONE_STATE,\ 
    RECEIVE_BOOT_COMPLETED

# Android service to use
android.services = redlogger_service:redlogger_service.py

# Android BroadcastReceiver for boot start
android.receivers = org.redlogger.redlogger.ServiceReceiver

# (str) The log level
# one of "debug", "info", "warning", "error", "critical"
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1

# (str) The Android NDK version to use
# If you have a numeric version, you can use it. Otherwise, use a string like "r23b".
android.ndk = 23b

# (str) The Android SDK version to use
android.sdk = 24

# (str) The Android API level to use
android.api = 27

# (str) The Android build tools version to use
android.build_tools = 30.0.3


