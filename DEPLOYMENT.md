# 🚀 TechFlow Deployment Guide - EC2 Ubuntu

## 📋 Prerequisites
- AWS EC2 Ubuntu instance (t2.small or larger)
- SSH key (.pem file)
- GitHub repository: https://github.com/ayakhalid01/testtech.git

---

## 1️⃣ Connect to EC2

```bash
ssh -i your-key.pem ubuntu@your-ec2-ip
```

---

## 2️⃣ Update System & Install Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install essential tools
sudo apt install -y git curl wget build-essential

# Install Python 3.11+
sudo apt install -y python3 python3-pip python3-venv
python3 --version

# Install Node.js 20
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs
node --version
npm --version
```

---

## 3️⃣ Clone Repository

```bash
cd ~
git clone https://github.com/ayakhalid01/testtech.git
cd testtech
```

---

## 4️⃣ Setup Backend (FastAPI)

```bash
cd ~/testtech/backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
nano .env
```

**Paste your environment variables:**
```env
SUPABASE_URL=https://zxoostjcukaritjzxmwh.supabase.co
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_SERVICE_KEY=your_service_key
API_SECRET_KEY=your_secret_key
ENCRYPTION_KEY=generate-with-fernet-key
```

Save: `Ctrl+X` → `Y` → `Enter`

---

## 5️⃣ Setup Frontend (Next.js)

```bash
cd ~/testtech/frontend

# Install dependencies
npm install

# Create .env.local
nano .env.local
```

**Paste:**
```env
NEXT_PUBLIC_API_URL=http://your-ec2-ip:8000
```

Save: `Ctrl+X` → `Y` → `Enter`

```bash
# Build production
npm run build
```

---

## 6️⃣ Install PM2 (Process Manager)

```bash
sudo npm install -g pm2
```

---

## 7️⃣ Create PM2 Ecosystem File

```bash
cd ~/testtech
nano ecosystem.config.js
```

**Paste:**
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

Save: `Ctrl+X` → `Y` → `Enter`

---

## 8️⃣ Start Applications

```bash
cd ~/testtech

# Start both apps
pm2 start ecosystem.config.js

# Save PM2 process list
pm2 save

# Auto-start on server reboot
pm2 startup
```

**Copy the command shown and run it** (will look like):
```bash
sudo env PATH=$PATH:/usr/bin pm2 startup systemd -u ubuntu --hp /home/ubuntu
```

---

## 9️⃣ Configure AWS Security Group

Go to **AWS Console → EC2 → Security Groups**

**Add Inbound Rules:**
- **HTTP** (80) - Source: `0.0.0.0/0`
- **Custom TCP** (3000) - Source: `0.0.0.0/0` ← Frontend
- **Custom TCP** (8000) - Source: `0.0.0.0/0` ← Backend API
- **SSH** (22) - Source: `Your IP Only`

---

## 🔟 Install Chrome for Selenium (Scraper)

```bash
# Install Chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb
sudo apt --fix-broken install -y

# Verify
google-chrome --version
```

---

## 1️⃣1️⃣ Setup Scraper Cron Job

```bash
crontab -e
```

**Add this line** (runs every 6 hours):
```cron
0 */6 * * * cd /home/ubuntu/testtech && /home/ubuntu/testtech/backend/venv/bin/python scraper.py --include-indeed --use-tinyurl >> /home/ubuntu/scraper.log 2>&1
```

Save and exit.

---

## ✅ Verify Deployment

```bash
# Check PM2 processes
pm2 status

# Check logs
pm2 logs

# Test backend
curl http://localhost:8000/api/health

# Test frontend
curl http://localhost:3000
```

**Access your app:**
- **Frontend**: `http://your-ec2-ip:3000`
- **Backend API**: `http://your-ec2-ip:8000/api`

---

## 📊 Useful PM2 Commands

```bash
pm2 list                      # Show all processes
pm2 logs                      # View all logs
pm2 logs techflow-backend     # View backend logs only
pm2 logs techflow-frontend    # View frontend logs only
pm2 restart all               # Restart all apps
pm2 stop all                  # Stop all apps
pm2 delete all                # Delete all apps
pm2 monit                     # Real-time monitoring
```

---

## 🔄 Update Application (Future)

```bash
cd ~/testtech
git pull
pm2 restart all
```

---

## 🐛 Troubleshooting

**Backend not starting:**
```bash
cd ~/testtech/backend
source venv/bin/activate
python main.py  # See the error
pm2 logs techflow-backend
```

**Frontend not starting:**
```bash
cd ~/testtech/frontend
npm run build  # Rebuild
pm2 logs techflow-frontend
```

**Check ports:**
```bash
sudo netstat -tulpn | grep 3000
sudo netstat -tulpn | grep 8000
```

**Restart services:**
```bash
pm2 restart all
pm2 save
```

---

## 🎯 Success!

Your TechFlow application is now running 24/7 on AWS EC2! 🚀

**Access URLs:**
- Frontend: `http://your-ec2-ip:3000`
- Backend: `http://your-ec2-ip:8000`
- API Docs: `http://your-ec2-ip:8000/docs`
