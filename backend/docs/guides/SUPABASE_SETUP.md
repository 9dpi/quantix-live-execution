# 🗄️ Supabase Database Setup Guide

Complete guide to setup Supabase database for Signal Genius AI.

---

## 📋 Overview

Supabase database sẽ lưu trữ:
- ✅ **Signals**: Tất cả trading signals
- ✅ **Signal History**: Archive cho analytics
- ✅ **Telegram Subscribers**: Users/groups nhận signals
- ✅ **Signal Deliveries**: Tracking delivery status
- ✅ **Analytics**: Performance metrics
- ✅ **API Logs**: Monitoring và debugging

---

## 🚀 Bước 1: Tạo Supabase Project

### 1.1. Đăng ký/Đăng nhập Supabase

1. Truy cập: https://supabase.com/
2. Click **Start your project**
3. Đăng nhập bằng GitHub (recommended) hoặc email

### 1.2. Tạo Project mới

1. Click **New Project**
2. Điền thông tin:
   - **Name**: `signal-genius-ai`
   - **Database Password**: Tạo password mạnh (lưu lại!)
   - **Region**: Chọn gần nhất (e.g., `Southeast Asia (Singapore)`)
   - **Pricing Plan**: Free tier (đủ cho MVP)
3. Click **Create new project**
4. Đợi 2-3 phút để Supabase provision database

---

## 🗄️ Bước 2: Chạy Database Schema

### 2.1. Mở SQL Editor

1. Trong Supabase Dashboard, click **SQL Editor** (sidebar bên trái)
2. Click **New query**

### 2.2. Copy và Run Schema

1. Mở file: `database/schema.sql` (đã tạo sẵn)
2. Copy toàn bộ nội dung
3. Paste vào SQL Editor
4. Click **Run** (hoặc Ctrl+Enter)
5. Đợi vài giây để schema được tạo

### 2.3. Verify Tables

1. Click **Table Editor** (sidebar)
2. Bạn sẽ thấy các tables:
   - ✅ `signals`
   - ✅ `signal_history`
   - ✅ `telegram_subscribers`
   - ✅ `signal_deliveries`
   - ✅ `analytics`
   - ✅ `api_logs`

---

## 🔑 Bước 3: Lấy API Credentials

### 3.1. Lấy Project URL

1. Click **Settings** → **API**
2. Copy **Project URL**
   - Format: `https://xxxxxxxxxxxxx.supabase.co`
3. Lưu lại để dùng sau

### 3.2. Lấy API Keys

Trong cùng trang **Settings** → **API**:

1. **anon/public key** (Project API keys)
   - Dùng cho client-side (frontend)
   - Copy và lưu lại

2. **service_role key** (Service role secret)
   - Dùng cho server-side (backend, bot)
   - **QUAN TRỌNG**: Giữ bí mật!
   - Copy và lưu lại

---

## 🔐 Bước 4: Cấu hình Environment Variables

### 4.1. Update `.env` local

```bash
# Supabase Configuration
SUPABASE_URL=https://xxxxxxxxxxxxx.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 4.2. Update Railway Variables

Khi deploy bot lên Railway, thêm:

```
SUPABASE_URL = https://xxxxxxxxxxxxx.supabase.co
SUPABASE_SERVICE_KEY = eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Lưu ý**: Dùng `SUPABASE_SERVICE_KEY` cho backend/bot, không dùng anon key.

---

## 📊 Bước 5: Test Database Connection

### 5.1. Tạo Python Test Script

Tạo file `database/test_connection.py`:

```python
import os
from supabase import create_client, Client

# Load credentials
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_KEY')

# Create client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Test connection
try:
    # Query sample signal
    response = supabase.table('signals').select('*').limit(1).execute()
    print("✅ Connection successful!")
    print(f"📊 Found {len(response.data)} signal(s)")
    if response.data:
        print(f"Sample signal: {response.data[0]}")
except Exception as e:
    print(f"❌ Connection failed: {e}")
```

### 5.2. Install Supabase Client

```bash
pip install supabase
```

### 5.3. Run Test

```bash
# Set environment variables
export SUPABASE_URL=your_url
export SUPABASE_SERVICE_KEY=your_key

# Run test
python database/test_connection.py
```

**Expected output**:
```
✅ Connection successful!
📊 Found 1 signal(s)
Sample signal: {'id': '...', 'asset': 'EUR/USD', ...}
```

---

## 🔧 Bước 6: Integrate với Telegram Bot

### 6.1. Update `telegram/bot.py`

Thêm Supabase integration:

```python
from supabase import create_client, Client
import os

# Initialize Supabase
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_KEY')
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

async def save_signal_to_db(signal: Dict):
    """Save signal to Supabase"""
    try:
        response = supabase.table('signals').insert({
            'asset': signal['asset'],
            'direction': signal['direction'],
            'direction_icon': signal['direction_icon'],
            'timeframe': signal['timeframe'],
            'session': signal['session'],
            'price_levels': signal['price_levels'],
            'trade_details': signal['trade_details'],
            'trade_type': signal['trade_type'],
            'confidence': signal['confidence'],
            'posted_at_utc': signal['posted_at_utc'],
            'expiry_rules': signal['expiry_rules']
        }).execute()
        
        print(f"✅ Signal saved to database: {response.data[0]['id']}")
        return response.data[0]['id']
    except Exception as e:
        print(f"❌ Failed to save signal: {e}")
        return None

async def log_delivery(signal_id: str, subscriber_id: str, status: str):
    """Log signal delivery"""
    try:
        supabase.table('signal_deliveries').insert({
            'signal_id': signal_id,
            'subscriber_id': subscriber_id,
            'delivery_status': status
        }).execute()
    except Exception as e:
        print(f"❌ Failed to log delivery: {e}")
```

### 6.2. Update Requirements

Add to `telegram/requirements.txt`:

```
supabase==2.3.0
```

---

## 📈 Bước 7: Useful Queries

### Get active signals

```sql
SELECT * FROM active_signals;
```

### Get performance summary

```sql
SELECT * FROM performance_summary;
```

### Get recent deliveries

```sql
SELECT * FROM recent_deliveries LIMIT 10;
```

### Get signals by confidence

```sql
SELECT asset, direction, confidence, posted_at_utc
FROM signals
WHERE confidence >= 95
ORDER BY posted_at_utc DESC;
```

### Get win rate by asset

```sql
SELECT 
    asset,
    COUNT(*) as total,
    COUNT(CASE WHEN result = 'win' THEN 1 END) as wins,
    ROUND(
        COUNT(CASE WHEN result = 'win' THEN 1 END)::DECIMAL / 
        NULLIF(COUNT(*), 0) * 100, 
        2
    ) as win_rate
FROM signals
WHERE result IS NOT NULL
GROUP BY asset;
```

---

## 🛡️ Bước 8: Security Best Practices

### 8.1. Row Level Security (RLS)

Enable RLS for production:

```sql
-- Enable RLS
ALTER TABLE signals ENABLE ROW LEVEL SECURITY;

-- Create policy for public read of active signals
CREATE POLICY "Public read active signals" ON signals
    FOR SELECT USING (status = 'active');

-- Create policy for service role full access
CREATE POLICY "Service role full access" ON signals
    FOR ALL USING (auth.role() = 'service_role');
```

### 8.2. API Key Rotation

- Rotate service_role key định kỳ (3-6 tháng)
- Không commit keys vào Git
- Dùng environment variables

### 8.3. Backup

Supabase tự động backup daily (Free tier: 7 days retention)

Manual backup:
1. **Database** → **Backups**
2. Click **Create backup**

---

## 📊 Bước 9: Monitoring

### 9.1. Database Usage

Check trong **Settings** → **Usage**:
- Database size
- API requests
- Bandwidth

### 9.2. Logs

Check trong **Logs** → **Database**:
- Query performance
- Errors
- Slow queries

---

## 🎯 Checklist

- [ ] Supabase project created
- [ ] Database schema executed
- [ ] Tables verified in Table Editor
- [ ] API credentials copied
- [ ] Environment variables configured
- [ ] Test connection successful
- [ ] Supabase client installed
- [ ] Bot integrated with database
- [ ] Sample signal inserted
- [ ] Queries tested

---

## 🐛 Troubleshooting

### Connection failed

**Problem**: `supabase.create_client()` fails

**Solutions**:
1. Check SUPABASE_URL is correct
2. Check SUPABASE_KEY is service_role key (not anon key)
3. Verify project is active in Supabase dashboard

### Insert failed

**Problem**: Cannot insert signal

**Solutions**:
1. Check schema matches data structure
2. Verify JSONB fields are valid JSON
3. Check constraints (e.g., confidence 0-100)

### Slow queries

**Problem**: Queries taking too long

**Solutions**:
1. Check indexes are created
2. Use `EXPLAIN ANALYZE` to debug
3. Add more indexes if needed

---

## 📞 Support

- **Supabase Docs**: https://supabase.com/docs
- **Supabase Discord**: https://discord.supabase.com/
- **SQL Reference**: https://www.postgresql.org/docs/

---

## 🎉 Next Steps

After setup:
1. ✅ Integrate Supabase with Telegram bot
2. ✅ Test signal saving
3. ✅ Monitor database usage
4. ✅ Setup analytics dashboard
5. ✅ Configure backups

---

**Database ready! 🚀**
