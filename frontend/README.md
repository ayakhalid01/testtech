# TechFlow Frontend

Next.js frontend for TechFlow job scraper dashboard.

## Setup

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Configure Environment Variables

Copy `.env.local.example` to `.env.local`:

```bash
cp .env.local.example .env.local
```

Edit `.env.local` with your credentials:
```env
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_API_KEY=your-secret-key
```

### 3. Run Development Server

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

## Features

- ✅ Dashboard with real-time statistics
- ✅ Scraping control panel
- ✅ Jobs listing (coming soon)
- ✅ Settings management (coming soon)
- ✅ Live logs viewer (coming soon)
- ✅ Scheduler configuration (coming soon)

## Deploy to Netlify

### Option 1: Connect GitHub Repository

1. Push code to GitHub
2. Go to [Netlify](https://netlify.com)
3. Click "Add new site" → "Import from Git"
4. Select your repository
5. Build settings:
   - Build command: `npm run build`
   - Publish directory: `.next`
6. Add environment variables in Netlify dashboard
7. Deploy!

### Option 2: Deploy with Netlify CLI

```bash
npm install -g netlify-cli
netlify login
netlify init
netlify deploy --prod
```

## Technologies

- Next.js 14 (App Router)
- React 18
- TypeScript
- Tailwind CSS
- Supabase JS Client
- Axios
- React Icons
