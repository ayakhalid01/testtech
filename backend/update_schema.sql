-- إضافة عمود company_logo و tiny_url للجدول jobs الموجود
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS company_logo TEXT;
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS tiny_url TEXT;
