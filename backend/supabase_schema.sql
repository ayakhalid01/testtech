-- TechFlow Supabase Database Schema

-- Table: jobs
-- Stores all scraped jobs
CREATE TABLE IF NOT EXISTS jobs (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    title TEXT NOT NULL,
    company TEXT,
    company_logo TEXT,
    location TEXT,
    salary TEXT,
    requirements JSONB,
    skills JSONB,
    description TEXT,
    link TEXT UNIQUE NOT NULL,
    tiny_url TEXT,
    source TEXT NOT NULL CHECK (source IN ('wuzzuf', 'indeed')),
    slug TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    posted_to_blogger BOOLEAN DEFAULT FALSE,
    sent_to_telegram BOOLEAN DEFAULT FALSE,
    sent_to_whatsapp BOOLEAN DEFAULT FALSE,
    blogger_url TEXT,
    html_content TEXT
);

-- Index for faster queries
CREATE INDEX idx_jobs_source ON jobs(source);
CREATE INDEX idx_jobs_created_at ON jobs(created_at DESC);
CREATE INDEX idx_jobs_link ON jobs(link);

-- Table: settings
-- Stores application configuration
CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value JSONB NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Table: api_keys
-- Stores encrypted API keys
CREATE TABLE IF NOT EXISTS api_keys (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    service TEXT UNIQUE NOT NULL,
    key_encrypted TEXT NOT NULL,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Table: scraping_logs
-- Stores scraping execution logs
CREATE TABLE IF NOT EXISTS scraping_logs (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    level TEXT NOT NULL CHECK (level IN ('info', 'warning', 'error')),
    message TEXT NOT NULL,
    metadata JSONB
);

-- Index for logs
CREATE INDEX idx_logs_timestamp ON scraping_logs(timestamp DESC);
CREATE INDEX idx_logs_level ON scraping_logs(level);

-- Table: schedules
-- Stores scheduled scraping jobs
CREATE TABLE IF NOT EXISTS schedules (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name TEXT NOT NULL,
    cron_expression TEXT NOT NULL,
    enabled BOOLEAN DEFAULT TRUE,
    last_run TIMESTAMPTZ,
    next_run TIMESTAMPTZ,
    config JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Table: blacklisted_companies
-- Companies to exclude from scraping
CREATE TABLE IF NOT EXISTS blacklisted_companies (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    company_name TEXT UNIQUE NOT NULL,
    reason TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Insert default settings
INSERT INTO settings (key, value) VALUES
('scraper_config', '{
    "max_jobs": 6,
    "sources": ["wuzzuf", "indeed"],
    "upload_to_blogger": false,
    "send_to_telegram": false,
    "send_to_whatsapp": false,
    "use_tinyurl": true,
    "use_selenium_skills": false
}'::jsonb),
('keywords', '{
    "keywords": [
        "Flutter", "Backend", "Frontend", "Full Stack", "Data Scientist",
        "Machine Learning", "DevOps", "Cloud", "Python", "Java",
        "JavaScript", "React", "Angular", "Vue", "Node.js",
        "PHP", "Laravel", ".NET", "C#", "Mobile", "Android", "iOS",
        "QA", "Testing", "Security", "Cyber Security", "Network",
        "Database", "SQL", "MongoDB", "AI", "Blockchain",
        "Software Engineer", "IT", "Technical Support"
    ]
}'::jsonb),
('telegram_config', '{
    "bot_token": "",
    "channel_id": "@techflow_channel",
    "enabled": false
}'::jsonb),
('whatsapp_config', '{
    "api_token": "",
    "phone_number_id": "",
    "business_account_id": "",
    "enabled": false
}'::jsonb),
('blogger_config', '{
    "blog_id": "6949685611084082756",
    "blog_domain": "https://careerjobst01.blogspot.com",
    "enabled": false
}'::jsonb),
('tinyurl_config', '{
    "api_key": "",
    "enabled": true
}'::jsonb)
ON CONFLICT (key) DO NOTHING;

-- Enable Row Level Security (RLS) - Optional, disable if no auth
ALTER TABLE jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE api_keys ENABLE ROW LEVEL SECURITY;
ALTER TABLE scraping_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE schedules ENABLE ROW LEVEL SECURITY;
ALTER TABLE blacklisted_companies ENABLE ROW LEVEL SECURITY;

-- Create policies to allow all operations (since no auth)
CREATE POLICY "Allow all on jobs" ON jobs FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all on settings" ON settings FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all on api_keys" ON api_keys FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all on scraping_logs" ON scraping_logs FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all on schedules" ON schedules FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all on blacklisted_companies" ON blacklisted_companies FOR ALL USING (true) WITH CHECK (true);

-- Enable Realtime for jobs and logs tables
ALTER PUBLICATION supabase_realtime ADD TABLE jobs;
ALTER PUBLICATION supabase_realtime ADD TABLE scraping_logs;
