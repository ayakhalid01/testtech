# Schedule Save Troubleshooting Guide

## Important: There is NO "schedule" table!

The schedule is saved in the **`settings` table** with `key = "schedule"`.

## Database Schema

Run this SQL in Supabase SQL Editor to ensure the table exists:

```sql
-- Create settings table if it doesn't exist
CREATE TABLE IF NOT EXISTS settings (
    id BIGSERIAL PRIMARY KEY,
    key TEXT UNIQUE NOT NULL,
    value JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index on key for faster lookups
CREATE INDEX IF NOT EXISTS idx_settings_key ON settings(key);
```

## Check Schedule Data

Run this SQL to view your saved schedule:

```sql
-- View schedule data
SELECT * FROM settings WHERE key = 'schedule';

-- View all settings
SELECT * FROM settings;
```

## Testing Steps

### 1. Check Backend is Running
```bash
cd d:/TechFlow/backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Test API Directly
```bash
cd d:/TechFlow
python test_schedule_save.py
```

This will:
- Send a test schedule to the API
- Show the response
- Retrieve the schedule back
- Display detailed logs

### 3. Check Backend Logs

When you save a schedule, you should see logs like:
```
💾 Saving schedule to database: {'enabled': True, 'time': '14:30', ...}
✅ Schedule saved successfully: enabled=True, time=14:30, frequency=daily
📊 Database result: [{'id': 1, 'key': 'schedule', 'value': {...}}]
```

### 4. Test from Frontend

1. Open: http://localhost:3000/schedule
2. Configure schedule settings
3. Click "Save Schedule"
4. Check browser console (F12) for any errors
5. Check backend terminal for logs

## Common Issues

### Issue 1: Settings table doesn't exist
**Solution:** Run the CREATE TABLE SQL above in Supabase

### Issue 2: Backend not running
**Solution:** Start backend: `cd d:/TechFlow/backend && python -m uvicorn main:app --reload`

### Issue 3: CORS errors in frontend
**Solution:** Make sure frontend is calling http://localhost:8000

### Issue 4: Data saves but doesn't appear
**Check:**
- Supabase connection in .env file
- SQL query uses correct key: `WHERE key = 'schedule'`
- Not looking at wrong table

## API Endpoints

### Save Schedule
```
POST http://localhost:8000/api/schedule
Body: {
  "enabled": true,
  "time": "14:30",
  "frequency": "daily",
  "max_jobs": 6,
  "sources": ["wuzzuf", "indeed"],
  "upload_to_blogger": true,
  "send_to_telegram": true,
  "send_to_whatsapp": false
}
```

### Get Schedule
```
GET http://localhost:8000/api/schedule
```

## Verification Checklist

- [ ] Backend server is running on port 8000
- [ ] Supabase credentials are correct in .env
- [ ] Settings table exists in database
- [ ] test_schedule_save.py runs successfully
- [ ] Backend logs show save operation
- [ ] SQL query returns schedule data
- [ ] Frontend can load and save schedule
