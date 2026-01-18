# 🔧 Railway Environment Variables Setup

## ⚠️ CRITICAL: Required Environment Variables

Your bot needs these environment variables to work properly:

### 1. TWELVE_DATA_API_KEY (Required for /signal)
```
TWELVE_DATA_API_KEY=4a64fb7beafc42e6a9d6b0576ce5cf9f
```

**Without this:**
- `/signal` command will fail
- Bot will use fallback signals only
- Error: "TWELVE_DATA_API_KEY not configured"

### 2. TELEGRAM_BOT_TOKEN (Required for bot)
```
TELEGRAM_BOT_TOKEN=8371104272:AAFlp0NA8wz-HEKOqtsbyGR1_m8C3pzZO2c
```

## 🚀 How to Set Variables in Railway

### Method 1: Railway Dashboard (Recommended)
1. Go to https://railway.app
2. Select your project: `signalgeniusai-production`
3. Click on your service
4. Go to **Variables** tab
5. Click **+ New Variable**
6. Add each variable:
   - Name: `TWELVE_DATA_API_KEY`
   - Value: `4a64fb7beafc42e6a9d6b0576ce5cf9f`
7. Click **+ New Variable** again
   - Name: `TELEGRAM_BOT_TOKEN`
   - Value: `8371104272:AAFlp0NA8wz-HEKOqtsbyGR1_m8C3pzZO2c`
8. **Deploy** will trigger automatically

### Method 2: Railway CLI
```bash
railway variables set TWELVE_DATA_API_KEY=4a64fb7beafc42e6a9d6b0576ce5cf9f
railway variables set TELEGRAM_BOT_TOKEN=8371104272:AAFlp0NA8wz-HEKOqtsbyGR1_m8C3pzZO2c
```

## ✅ Verify Variables Are Set

### Check Railway Logs
After deploying, check logs for:
```
✅ TwelveData API Key loaded: 4a64fb7bea...
```

If you see:
```
⚠️ WARNING: TWELVE_DATA_API_KEY not set in environment!
```
→ Variable not loaded, check Railway dashboard

### Test API Key Manually
```bash
curl "https://api.twelvedata.com/time_series?symbol=EUR/USD&interval=15min&outputsize=5&apikey=4a64fb7beafc42e6a9d6b0576ce5cf9f"
```

**Expected response:**
```json
{
  "meta": {...},
  "values": [...]
}
```

**If error:**
```json
{
  "code": 401,
  "message": "Invalid API key"
}
```
→ Check your API key

## 🧪 Test Bot After Setting Variables

1. **Redeploy** (Railway auto-deploys on variable change)
2. **Wait 1-2 minutes** for deployment
3. **Test in Telegram:**
   ```
   /signal
   ```

**Expected:**
```
📊 EUR/USD | M15
🟢 BUY

🎯 Entry: 1.0845
💰 TP: 1.0890
🛑 SL: 1.0810

⭐ Confidence: 88%
🧠 Strategy: EMA Trend + RSI + ATR
```

**If still error:**
```
⚠️ Signal temporarily unavailable
Reason: TWELVE_DATA_API_KEY not configured
```
→ Variables not loaded, restart deployment

## 🔍 Troubleshooting

### Problem: Bot says "API key not configured"
**Solution:**
1. Check Railway Variables tab
2. Ensure `TWELVE_DATA_API_KEY` exists
3. Click **Restart** on deployment
4. Wait 2 minutes
5. Test `/signal` again

### Problem: "Invalid API key" error
**Solution:**
1. Test API key manually (curl command above)
2. If invalid, get new key from https://twelvedata.com
3. Update Railway variable
4. Redeploy

### Problem: Variables set but still not working
**Solution:**
1. **Hard restart:**
   - Railway Dashboard → Service → Settings
   - Click **Restart**
2. Check logs for:
   ```
   ✅ TwelveData API Key loaded: 4a64fb7bea...
   ```
3. If not showing, variables not loaded properly

## 📊 Current Status Check

Run this in Railway logs to verify:
```
grep "TwelveData API Key" logs
```

Should show:
```
✅ TwelveData API Key loaded: 4a64fb7bea...
```

## 🎯 Quick Fix Checklist

- [ ] TWELVE_DATA_API_KEY set in Railway Variables
- [ ] TELEGRAM_BOT_TOKEN set in Railway Variables
- [ ] Deployment restarted after adding variables
- [ ] Logs show "✅ TwelveData API Key loaded"
- [ ] `/signal` command works in Telegram
- [ ] No "API key not configured" errors

---

**After setting variables, Railway will auto-deploy. Wait 1-2 minutes and test `/signal` in Telegram!**
