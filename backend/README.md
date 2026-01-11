# TechFlow Backend API

FastAPI backend for TechFlow job scraper with Supabase integration.

## Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Setup Supabase

1. Create a free account at [supabase.com](https://supabase.com)
2. Create a new project
3. Go to SQL Editor and run the schema from `supabase_schema.sql`
4. Get your project URL and API keys from Settings > API

### 3. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Edit `.env`:
```env
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-role-key
API_SECRET_KEY=your-random-secret-key
ENCRYPTION_KEY=your-fernet-encryption-key
```

Generate encryption key:
```python
from cryptography.fernet import Fernet
print(Fernet.generate_key().decode())
```

### 4. Run the Server

```bash
uvicorn main:app --reload
```

API will be available at `http://localhost:8000`

## API Endpoints

### Health Check
- `GET /` - Service status
- `GET /api/health` - Database connection check

### Scraping
- `POST /api/scrape` - Start scraping (requires API key header)
  ```json
  {
    "max_jobs": 6,
    "sources": ["wuzzuf", "indeed"],
    "upload_to_blogger": false,
    "send_to_telegram": false,
    "send_to_whatsapp": false,
    "use_tinyurl": true,
    "use_selenium_skills": false
  }
  ```

### Jobs
- `GET /api/jobs?limit=50&offset=0&source=wuzzuf` - Get scraped jobs
- `GET /api/stats` - Get scraping statistics

### Settings
- `GET /api/settings` - Get all settings
- `POST /api/settings` - Update settings (requires API key)

### Logs
- `GET /api/logs?limit=100&level=info` - Get scraping logs

## Authentication

All write endpoints require `x-api-key` header:

```bash
curl -H "x-api-key: your-secret-key-here" -X POST http://localhost:8000/api/scrape
```

## Deploy to Railway

1. Create `Procfile`:
```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

2. Push to GitHub
3. Connect Railway to your repository
4. Add environment variables in Railway dashboard
5. Deploy!
