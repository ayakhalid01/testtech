# إعداد Telegram Bot للنشر التلقائي

## خطوات الإعداد:

### 1. إنشاء Telegram Bot
1. افتح تطبيق Telegram
2. ابحث عن: **@BotFather**
3. ابدأ محادثة واكتب: `/newbot`
4. اتبع التعليمات:
   - اختر اسم للبوت (مثال: TechFlow Jobs Bot)
   - اختر username للبوت (مثال: techflow_jobs_bot)
5. احفظ الـ **Bot Token** اللي هيديهولك (مثال: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### 2. إنشاء Telegram Channel
1. افتح Telegram → New Channel
2. اختر اسم القناة (مثال: TechFlow Jobs)
3. اجعل القناة **Public** واختر username (مثال: @techflow_jobs)
4. أضف البوت كـ **Admin** في القناة:
   - افتح القناة → Settings → Administrators
   - Add Administrator → ابحث عن البوت
   - اعطيه صلاحية **Post Messages**

### 3. الحصول على Channel ID

**إذا كانت القناة Public:**
- الـ Channel ID هو: `@your_channel_username`
- مثال: `@techflow_jobs`

**إذا كانت القناة Private:**
استخدم هذا البوت للحصول على الـ ID:
1. ابحث عن: **@getmyid_bot**
2. أضفه للقناة
3. سيرسل لك الـ Channel ID (مثال: `-1001234567890`)

**أو استخدم هذه الطريقة:**
```bash
# أرسل رسالة للقناة أولاً من البوت، ثم استخدم:
curl "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates"
```
ابحث عن `"chat":{"id":-1001234567890}` في النتيجة

### 4. إضافة المعلومات في الكود

افتح ملف `scraper.py` وحدّث هذه الأسطر:

```python
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN = "123456789:ABCdefGHIjklMNOpqrsTUVwxyz"  # من @BotFather
TELEGRAM_CHANNEL_ID = "@techflow_jobs"  # أو -1001234567890 للقنوات Private
```

### 5. استخدام النشر التلقائي

```bash
# نشر على Telegram فقط
python scraper.py --send-telegram

# نشر على Blogger + Telegram
python scraper.py --upload --send-telegram

# نشر على WhatsApp + Telegram
python scraper.py --send-whatsapp --send-telegram

# نشر كامل (Blogger + WhatsApp + Telegram + Skills)
python scraper.py --upload --send-whatsapp --send-telegram --selenium-skills
```

## مميزات Telegram Bot:

✅ **مجاني 100%** - مفيش أي رسوم
✅ **Unlimited messages** - بدون حدود
✅ **No API limits** - مفيش rate limiting
✅ **Rich formatting** - دعم Markdown (Bold, Italic, Links)
✅ **Instant delivery** - الرسائل بتوصل فوراً
✅ **Easy setup** - إعداد سريع في دقائق

## أمثلة عملية:

### مثال 1: البوت Token من @BotFather
```
6123456789:AAHdqTcvCH1vGWJxfSeofSAs0K5PALDsaw
```

### مثال 2: Channel ID (Public)
```
@techflow_jobs
```

### مثال 3: Channel ID (Private)
```
-1001234567890
```

## تنسيق الرسائل:

البوت بيستخدم **Markdown formatting**:
- `*bold text*` → **bold text**
- `_italic_` → *italic*
- `[link text](URL)` → clickable link
- `🔗📍💰` → emojis مدعومة

## حل المشاكل الشائعة:

### Error: "Chat not found"
- تأكد إن البوت **Admin** في القناة
- تأكد إن الـ Channel ID صحيح

### Error: "Bot was blocked"
- افتح محادثة مع البوت واضغط `/start`

### Error: "Unauthorized"
- تأكد إن الـ Bot Token صحيح
- تأكد إنك نسخت الـ token كامل

## روابط مفيدة:
- Telegram Bot API: https://core.telegram.org/bots/api
- @BotFather: https://t.me/BotFather
- @getmyid_bot: https://t.me/getmyid_bot

## الحالة:
- ✅ الكود جاهز
- ⏳ محتاج تنشئ Bot من @BotFather
- ⏳ محتاج تضيف Bot Token و Channel ID
