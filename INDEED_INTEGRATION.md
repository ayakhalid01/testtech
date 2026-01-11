# Indeed Integration Guide

تم إضافة دعم **Indeed Egypt** للسكرابر!

## 🎯 الميزات

- **سحب الوظائف من Indeed Egypt** بجانب Wuzzuf
- **نفس الفلاتر**: Keywords, 24 hours, Egypt only
- **تكامل كامل**: البوست يروح Blogger, WhatsApp, Telegram
- **استخدام Selenium**: عشان Cloudflare WAF

## 📝 طريقة الاستخدام

### 1. تشغيل Indeed + Wuzzuf معًا

```bash
python scraper.py --include-indeed --max-jobs 6
```

### 2. مع WhatsApp و Telegram

```bash
python scraper.py --include-indeed --send-whatsapp --send-telegram --max-jobs 10
```

### 3. مع Selenium Skills

```bash
python scraper.py --include-indeed --selenium-skills
```

### 4. رفع على Blogger

```bash
python scraper.py --include-indeed --upload
```

## ⚙️ كيف بيشتغل

1. **Indeed يشتغل الأول**: بيسحب نص العدد المطلوب من Indeed
   - Example: `--max-jobs 6` → Indeed بيحاول يجيب 3 وظائف
   
2. **بعدين Wuzzuf**: بيكمّل الباقي من Wuzzuf
   - Example: لو Indeed جاب 1، Wuzzuf هيجيب 5

3. **الفلاتر**: نفس الفلاتر بتتطبق على المصدرين
   - ✅ Keywords matching
   - ✅ 24 hours only
   - ✅ Egypt only
   
4. **التكامل**: كل الوظائف بتتبعت على:
   - Blogger (with `--upload`)
   - WhatsApp (with `--send-whatsapp`)
   - Telegram (with `--send-telegram`)

## 🔍 الفرق بين Indeed و Wuzzuf

| Feature | Wuzzuf | Indeed |
|---------|--------|--------|
| **Description** | ✅ Full details | ⚠️ Snippet only |
| **Requirements** | ✅ Full list | ❌ Not in cards |
| **Skills** | ✅ With Selenium | ❌ Not available |
| **Salary** | ✅ Usually shown | ⚠️ Sometimes |
| **Speed** | 🚀 Fast (requests) | 🐢 Slower (Selenium) |

## 📊 مثال على النتيجة

```
🔍 Fetching jobs from Indeed Egypt...
Searching Indeed for: IT...
   ✅ Indeed job: Senior Frontend Developer (Vodafone)
✅ Scraped 1 jobs from Indeed

🔍 Searching Wuzzuf for jobs in categories: Backend, QA, Flutter...
   ✅ Recent job: Backend Developer (Orange)
   ✅ Recent job: QA Engineer (Etisalat)
✅ Scraped 2 jobs from Wuzzuf

Total: 3 jobs (1 from Indeed + 2 from Wuzzuf)
```

## ⚠️ ملاحظات

1. **Selenium مطلوب**: Indeed محتاج Selenium عشان Cloudflare
   ```bash
   pip install selenium
   ```

2. **Indeed نتايج أقل**: Indeed Egypt مش دايمًا فيه وظائف كتير خلال 24 ساعة

3. **البيانات محدودة**: Indeed مش بيوفر Requirements أو Skills في الكروت

4. **السرعة**: Indeed أبطأ من Wuzzuf عشان بيستخدم Selenium

## 🎨 تخصيص Indeed

لو عايز تغيّر الـ keywords بتاعة Indeed، روح سطر **817** في `scraper.py`:

```python
search_queries = ["IT", "Software", "Developer", "Backend", "Frontend"]
```

ممكن تضيف أو تشيل كلمات:

```python
search_queries = ["IT", "Software", "Python", "Flutter", "QA"]
```

## 🚀 Best Practices

1. **استخدم `--include-indeed` لما تحتاج نتايج أكتر**:
   ```bash
   python scraper.py --include-indeed --max-jobs 10
   ```

2. **Wuzzuf لوحده للسرعة**:
   ```bash
   python scraper.py --max-jobs 6
   ```

3. **Indeed + Wuzzuf للتنوع**:
   ```bash
   python scraper.py --include-indeed --selenium-skills --max-jobs 8
   ```

## 📝 ملف Indeed المستقل

لو عايز تجرب Indeed لوحده، استخدم:

```bash
python indeed_scraper.py
```

هيجيب 3 وظائف من Indeed بس ويطبع النتيجة.
