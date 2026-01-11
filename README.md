# TechFlow - Automated Job Scraper

Complete web application for scraping tech jobs from Wuzzuf and Indeed Egypt, with automated posting to Blogger and messaging via Telegram/WhatsApp.

## 🏗️ Architecture

- **Frontend**: Next.js 14 + Tailwind CSS (Deploy on Netlify)
- **Backend**: FastAPI + Python (Deploy on Railway)
- **Database**: Supabase PostgreSQL
- **Scheduler**: GitHub Actions (cron jobs)
- **Storage**: Supabase Storage

## 📁 Project Structure

```
TechFlow/
├── backend/                    # FastAPI backend
│   ├── main.py                # API endpoints
│   ├── supabase_helper.py     # Database operations
│   ├── supabase_schema.sql    # Database schema
│   ├── requirements.txt       # Python dependencies
│   ├── Procfile              # Railway deployment
│   └── README.md
├── frontend/                  # Next.js frontend
│   ├── app/                  # App router pages
│   ├── components/           # React components
│   ├── lib/                  # Utilities (Supabase, API)
│   ├── styles/               # CSS files
│   ├── package.json
│   └── README.md
├── .github/workflows/        # GitHub Actions
│   └── scheduled-scraping.yml
├── scraper.py               # Original scraper (to be integrated)
├── templates/               # Email/blog templates
└── README.md               # This file
```

## 🚀 Quick Start

### 1. Setup Supabase

1. Create account at [supabase.com](https://supabase.com)
2. Create new project
3. Run SQL from `backend/supabase_schema.sql` in SQL Editor
4. Get URL and API keys from Settings > API

### 2. Setup Backend

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your credentials
uvicorn main:app --reload
```

Backend runs at `http://localhost:8000`

### 3. Setup Frontend

```bash
cd frontend
npm install
cp .env.local.example .env.local
# Edit .env.local with your credentials
npm run dev
```

Frontend runs at `http://localhost:3000`

## 📦 Deployment

### Deploy Backend to Railway

1. Create Railway account
2. New Project → Deploy from GitHub
3. Select `TechFlow` repository
4. Set root directory to `backend`
5. Add environment variables:
   - `SUPABASE_URL`
   - `SUPABASE_KEY`
   - `SUPABASE_SERVICE_KEY`
   - `API_SECRET_KEY`
   - `ENCRYPTION_KEY`
6. Deploy!

### Deploy Frontend to Netlify

1. Create Netlify account
2. New Site → Import from Git
3. Select `TechFlow` repository
4. Build settings:
   - Base directory: `frontend`
   - Build command: `npm run build`
   - Publish directory: `frontend/.next`
5. Add environment variables:
   - `NEXT_PUBLIC_SUPABASE_URL`
   - `NEXT_PUBLIC_SUPABASE_ANON_KEY`
   - `NEXT_PUBLIC_API_URL` (Railway URL)
   - `NEXT_PUBLIC_API_KEY`
6. Deploy!

### Setup GitHub Actions Scheduler

1. Go to GitHub repository Settings → Secrets
2. Add secrets:
   - `RAILWAY_API_URL` (your Railway backend URL)
   - `API_SECRET_KEY` (same as backend)
3. Workflow will run every 6 hours automatically
4. Manually trigger from Actions tab

## 🔑 Environment Variables

### Backend (.env)
```env
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-key
API_SECRET_KEY=random-secret
ENCRYPTION_KEY=fernet-key
```

### Frontend (.env.local)
```env
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
NEXT_PUBLIC_API_URL=https://your-app.railway.app
NEXT_PUBLIC_API_KEY=random-secret
```

## 🎯 Features

### Current Features
- ✅ Scrape jobs from Wuzzuf
- ✅ Scrape jobs from Indeed Egypt (Selenium + Cloudflare bypass)
- ✅ Save to Supabase database
- ✅ Web dashboard with real-time stats
- ✅ Control panel for manual scraping
- ✅ FastAPI backend with authentication
- ✅ Supabase real-time updates
- ✅ GitHub Actions scheduling

### Coming Soon
- 🔄 Jobs listing page
- 🔄 Settings management UI
- 🔄 Live logs viewer
- 🔄 Blogger API integration
- 🔄 Telegram/WhatsApp sending
- 🔄 Schedule configuration UI
- 🔄 Job editing and approval
- 🔄 Company blacklist management

## 💰 Cost Breakdown

- **Supabase**: FREE (500MB DB + 1GB Storage + 2GB Bandwidth)
- **Railway**: FREE ($5 credit/month = ~500 hours)
- **Netlify**: FREE (100GB bandwidth + 300 build minutes)
- **GitHub Actions**: FREE (2000 minutes/month)
- **Total**: $0/month ✨

## 📚 Tech Stack

- **Frontend**: Next.js 14, React 18, TypeScript, Tailwind CSS
- **Backend**: FastAPI, Python 3.11, Uvicorn
- **Database**: Supabase (PostgreSQL)
- **Scraping**: BeautifulSoup4, Selenium, undetected-chromedriver
- **APIs**: Google Blogger, Telegram Bot, WhatsApp Cloud, TinyURL
- **Deployment**: Railway, Netlify, GitHub Actions

## 🔒 Security

- API key authentication for backend endpoints
- Encrypted API keys storage in Supabase
- CORS configured for Netlify domain only
- Environment variables for sensitive data
- Row Level Security (RLS) on Supabase tables

## 📖 Documentation

- [Backend API Docs](backend/README.md)
- [Frontend Setup](frontend/README.md)
- [Supabase Schema](backend/supabase_schema.sql)
- [GitHub Actions](.github/workflows/scheduled-scraping.yml)

## 🤝 Contributing

This is a personal project, but feel free to fork and customize!

## 📝 License

MIT License - do whatever you want with it!

---

Built with ❤️ for automating job hunting in Egypt 🇪🇬
