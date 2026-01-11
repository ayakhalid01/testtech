# 🚀 دليل نشر TechFlow على EC2

## 📋 المتطلبات
- سيرفر AWS EC2Ubuntu (t2.small أو أكبر)
- مفتاح SSH (.pem file)
- رابط GitHub: https://github.com/ayakhalid01/testtech.git

---

## 1️⃣ الاتصال بالسيرفر

```bash
ssh -i your-key.pem ubuntu@your-ec2-ip
```

---

## 2️⃣ تحديث النظام وتنزيل الأدوات

```bash
# تحديث النظام
sudo apt update && sudo apt upgrade -y

# تنزيل الأدوات الأساسية
sudo apt install -y git curl wget build-essential

# تنزيل Python 3.11+
sudo apt install -y python3 python3-pip python3-venv
python3 --version

# تنزيل Node.js 20
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs
node --version
npm --version
```

---

## 3️⃣ سحب المشروع من GitHub

```bash
cd ~
git clone https://github.com/ayakhalid01/testtech.git
cd testtech
```

---

## 4️⃣ تجهيز الـ Backend (FastAPI)

```bash
cd ~/testtech/backend

# إنشاء بيئة افتراضية
python3 -m venv venv
source venv/bin/activate

# تنزيل المكتبات
pip install -r requirements.txt

# إنشاء ملف .env
nano .env
```

**الصق إعدادات البيئة:**
```env
SUPABASE_URL=https://zxoostjcukaritjzxmwh.supabase.co
SUPABASE_KEY=مفتاح_سوباباس_بتاعك
SUPABASE_SERVICE_KEY=مفتاح_الخدمة
API_SECRET_KEY=مفتاح_سري
ENCRYPTION_KEY=generate-with-fernet-key
```

احفظ: `Ctrl+X` → `Y` → `Enter`

---

## 5️⃣ تجهيز الـ Frontend (Next.js)

```bash
cd ~/testtech/frontend

# تنزيل المكتبات
npm install

# إنشاء .env.local
nano .env.local
```

**الصق:**
```env
NEXT_PUBLIC_API_URL=http://ip-السيرفر-بتاعك:8000
```

احفظ: `Ctrl+X` → `Y` → `Enter`

```bash
# بناء النسخة النهائية
npm run build
```

---

## 6️⃣ تنزيل PM2 (لإدارة التطبيقات)

```bash
sudo npm install -g pm2
```

---

## 7️⃣ إنشاء ملف PM2 Configuration

```bash
cd ~/testtech
nano ecosystem.config.js
```

**الصق:**
```javascript
module.exports = {
  apps: [
    {
      name: 'techflow-backend',
      script: 'venv/bin/uvicorn',
      args: 'main:app --host 0.0.0.0 --port 8000',
      cwd: '/home/ubuntu/testtech/backend',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '1G',
      env: {
        NODE_ENV: 'production'
      }
    },
    {
      name: 'techflow-frontend',
      script: 'npm',
      args: 'start',
      cwd: '/home/ubuntu/testtech/frontend',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '1G',
      env: {
        NODE_ENV: 'production',
        PORT: 3000
      }
    }
  ]
};
```

احفظ: `Ctrl+X` → `Y` → `Enter`

---

## 8️⃣ تشغيل التطبيقات

```bash
cd ~/testtech

# تشغيل التطبيقات
pm2 start ecosystem.config.js

# حفظ قائمة التطبيقات
pm2 save

# تشغيل تلقائي عند إعادة تشغيل السيرفر
pm2 startup
```

**انسخ الأمر اللي هيظهر وشغله** (مثال):
```bash
sudo env PATH=$PATH:/usr/bin pm2 startup systemd -u ubuntu --hp /home/ubuntu
```

---

## 9️⃣ فتح المنافذ في AWS Security Group

روح **AWS Console → EC2 → Security Groups**

**أضف Inbound Rules:**
- **HTTP** (80) - Source: `0.0.0.0/0`
- **Custom TCP** (3000) - Source: `0.0.0.0/0` ← Frontend
- **Custom TCP** (8000) - Source: `0.0.0.0/0` ← Backend
- **SSH** (22) - Source: `Your IP Only` ← للأمان

---

## 🔟 تنزيل Chrome للـ Scraper

```bash
# تنزيل Chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb
sudo apt --fix-broken install -y

# التحقق
google-chrome --version
```

---

## 1️⃣1️⃣ جدولة الـ Scraper (كل 6 ساعات)

```bash
crontab -e
```

**أضف السطر ده:**
```cron
0 */6 * * * cd /home/ubuntu/testtech && /home/ubuntu/testtech/backend/venv/bin/python scraper.py --include-indeed --use-tinyurl >> /home/ubuntu/scraper.log 2>&1
```

احفظ واطلع.

---

## ✅ التحقق من التشغيل

```bash
# شوف التطبيقات الشغالة
pm2 status

# شوف اللوجز
pm2 logs

# اختبر Backend
curl http://localhost:8000/api/health

# اختبر Frontend
curl http://localhost:3000
```

**افتح التطبيق:**
- **Frontend**: `http://ip-سيرفرك:3000`
- **Backend API**: `http://ip-سيرفرك:8000/api`
- **API Docs**: `http://ip-سيرفرك:8000/docs`

---

## 📊 أوامر PM2 المفيدة

```bash
pm2 list                      # عرض كل التطبيقات
pm2 logs                      # عرض كل اللوجز
pm2 logs techflow-backend     # لوج Backend فقط
pm2 logs techflow-frontend    # لوج Frontend فقط
pm2 restart all               # إعادة تشغيل الكل
pm2 stop all                  # إيقاف الكل
pm2 delete all                # حذف الكل
pm2 monit                     # مراقبة مباشرة
pm2 reload all                # تحديث بدون توقف
```

---

## 🔄 تحديث التطبيق (مستقبلاً)

```bash
cd ~/testtech
git pull                # سحب التحديثات
pm2 restart all        # إعادة تشغيل
```

---

## 🐛 حل المشاكل

**Backend مش شغال:**
```bash
cd ~/testtech/backend
source venv/bin/activate
python main.py  # شوف الخطأ
pm2 logs techflow-backend
```

**Frontend مش شغال:**
```bash
cd ~/testtech/frontend
npm run build  # أعد البناء
pm2 logs techflow-frontend
```

**تحقق من المنافذ:**
```bash
sudo netstat -tulpn | grep 3000
sudo netstat -tulpn | grep 8000
```

**إعادة التشغيل:**
```bash
pm2 restart all
pm2 save
```

**مسح اللوجز:**
```bash
pm2 flush
```

---

## 🎯 تهانينا!

تطبيق TechFlow بتاعك دلوقتي شغال 24/7 على AWS EC2! 🚀

**الروابط:**
- **الواجهة**: `http://ip-سيرفرك:3000`
- **API**: `http://ip-سيرفرك:8000`
- **الوثائق**: `http://ip-سيرفرك:8000/docs`

---

## 🔒 نصائح الأمان

1. **غير المنفذ 22 (SSH)** لمنفذ مخصص
2. **استخدم SSL** مع Let's Encrypt (اختياري)
3. **فعّل Firewall:**
   ```bash
   sudo ufw allow 22
   sudo ufw allow 3000
   sudo ufw allow 8000
   sudo ufw enable
   ```

---

## 📝 ملاحظات مهمة

- السيرفر لازم يكون شغال 24/7
- الـ Scraper هيشتغل تلقائي كل 6 ساعات
- لو عايز تغير الوقت، عدل الـ crontab
- EC2 Free Tier بيدعم t2.micro (750 ساعة/شهر)
- لو عايز performance أحسن استخدم t2.small

**تكلفة تقريبية:**
- t2.small: ~$17/شهر
- Storage (20GB): ~$2/شهر
- **المجموع**: ~$19/شهر

---

**بالتوفيق! 🎉**
