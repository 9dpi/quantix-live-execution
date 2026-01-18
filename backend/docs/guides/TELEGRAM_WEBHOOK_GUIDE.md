# 🤖 Telegram Bot Webhook Setup Guide

## 🎯 Quick Fix Checklist

### ✅ Step 1: Verify Bot Token
```bash
# Check environment variable
echo $TELEGRAM_BOT_TOKEN

# Should output: 8371104272:AAFlp0NA8wz-HEKOqtsbyGR1_m8C3pzZO2c
```

### ✅ Step 2: Set Webhook URL

**Option A: Using Script (Recommended)**
```bash
cd backend
python set_webhook.py set
```

**Option B: Using cURL**
```bash
curl -X POST "https://api.telegram.org/bot8371104272:AAFlp0NA8wz-HEKOqtsbyGR1_m8C3pzZO2c/setWebhook" \
  -d "url=https://signalgeniusai-production.up.railway.app/telegram/webhook"
```

### ✅ Step 3: Verify Webhook
```bash
# Using script
python set_webhook.py info

# Using cURL
curl "https://api.telegram.org/bot8371104272:AAFlp0NA8wz-HEKOqtsbyGR1_m8C3pzZO2c/getWebhookInfo"
```

**Expected Output:**
```json
{
  "ok": true,
  "result": {
    "url": "https://signalgeniusai-production.up.railway.app/telegram/webhook",
    "has_custom_certificate": false,
    "pending_update_count": 0
  }
}
```

## 🧪 Testing

### Test Commands
1. Open Telegram
2. Find your bot: `@signal_genius_ai_bot`
3. Send: `/start`

**Expected Response:**
```
🤖 Signal Genius AI

Bot đã hoạt động!

Commands:
/signal - Get latest signal
/stats - View performance
/help - Show this message
```

### Available Commands

| Command | Description |
|---------|-------------|
| `/start` | Welcome message |
| `/signal` | Get latest trading signal |
| `/stats` | View performance statistics |
| `/help` | Show command list |

## 🔍 Troubleshooting

### Bot Not Responding

**Check 1: Webhook Status**
```bash
python set_webhook.py info
```

If `url` is empty:
```bash
python set_webhook.py set
```

**Check 2: Railway Logs**
```bash
# In Railway dashboard, check logs
# Should see: "📥 Telegram Update: {...}"
```

**Check 3: Endpoint Exists**
```bash
curl https://signalgeniusai-production.up.railway.app/health
# Should return: {"status":"ok"}
```

### Webhook Errors

**Error: "Webhook URL is not valid"**
- Ensure Railway app is deployed
- URL must be HTTPS
- URL must be publicly accessible

**Error: "Pending updates"**
```bash
# Delete webhook and reset
python set_webhook.py delete
python set_webhook.py set
```

### Message Not Sending

**Check Railway Environment Variables:**
```
TELEGRAM_BOT_TOKEN=8371104272:AAFlp0NA8wz-HEKOqtsbyGR1_m8C3pzZO2c
```

**Check Logs for Errors:**
```
❌ TELEGRAM_BOT_TOKEN not set
❌ Failed to send Telegram message: ...
```

## 📝 Environment Variables

### Required
```env
TELEGRAM_BOT_TOKEN=8371104272:AAFlp0NA8wz-HEKOqtsbyGR1_m8C3pzZO2c
```

### Optional
```env
WEBHOOK_URL=https://signalgeniusai-production.up.railway.app/telegram/webhook
```

## 🚀 Deployment Checklist

- [ ] Bot token set in Railway variables
- [ ] Backend deployed to Railway
- [ ] Webhook URL set via script or cURL
- [ ] Webhook verified (pending_update_count = 0)
- [ ] Test /start command works
- [ ] Test /signal command works

## 📊 Monitoring

### Check Webhook Status
```bash
# Every few hours
python set_webhook.py info
```

### Expected Output
```
📊 Webhook Info:
   URL: https://signalgeniusai-production.up.railway.app/telegram/webhook
   Pending updates: 0
   Last error: None
```

### If Pending Updates > 0
```bash
# Bot is receiving messages but not processing
# Check Railway logs for errors
```

## 🔧 Advanced

### Delete Webhook (Testing Only)
```bash
python set_webhook.py delete
```

### Manual Webhook Test
```bash
curl -X POST "https://signalgeniusai-production.up.railway.app/telegram/webhook" \
  -H "Content-Type: application/json" \
  -d '{
    "message": {
      "chat": {"id": 123456789},
      "text": "/start"
    }
  }'
```

## 📞 Support

If bot still not working after all checks:

1. **Verify bot token is correct**
   ```bash
   curl "https://api.telegram.org/bot<TOKEN>/getMe"
   ```

2. **Check Railway deployment status**
   - App should be "Active"
   - No build errors

3. **Verify endpoint is accessible**
   ```bash
   curl https://signalgeniusai-production.up.railway.app/health
   ```

4. **Check Railway logs for webhook calls**
   - Should see "📥 Telegram Update" when you send messages

---

**Remember**: Webhook must be set AFTER deploying to Railway. If you redeploy, webhook persists (no need to reset).
