# 🔍 HOW TO FIND YOUR RAILWAY URL

## Step 1: Go to Railway Dashboard

Open: https://railway.app/dashboard

## Step 2: Find Your Project

Look for project named:
- `signal-genius-ai`
- or similar name you created

## Step 3: Click on the Project

You'll see the deployment overview

## Step 4: Find the Domain

Look for one of these sections:
- **"Domains"** tab
- **"Settings"** → "Domains"
- **Deployment** → "Domain"

## Step 5: Copy the URL

It will look like:
```
https://signal-genius-ai-production.up.railway.app
```

or

```
https://[random-name].railway.app
```

## Step 6: Test It

### Option A: Browser
Open the URL in your browser:
```
https://your-app.railway.app/health
```

You should see:
```json
{
  "status": "ok",
  "service": "signal-genius-ai-mvp"
}
```

### Option B: PowerShell (Windows)
```powershell
$url = "https://your-app.railway.app"
Invoke-RestMethod -Uri "$url/health"
```

### Option C: curl (if available)
```bash
curl https://your-app.railway.app/health
```

## ✅ SUCCESS INDICATORS

**Deployment is working if:**
- ✅ URL is accessible (not 404)
- ✅ `/health` returns JSON
- ✅ Status code is 200
- ✅ Response time < 2 seconds

## ❌ TROUBLESHOOTING

### Issue: 404 Not Found
**Possible causes:**
- Deployment not finished yet (wait 2-5 min)
- Build failed (check Railway logs)
- Wrong URL

**Solution:**
1. Check Railway deployment status
2. Look for "Deployment successful" message
3. Verify URL is correct

### Issue: 502 Bad Gateway
**Possible causes:**
- App is starting up (wait 30 seconds)
- App crashed (check logs)

**Solution:**
1. Wait 30 seconds and retry
2. Check Railway logs for errors
3. Verify `Procfile` is correct

### Issue: Timeout
**Possible causes:**
- App is sleeping (Railway free tier)
- Network issue

**Solution:**
1. Retry request (first request may be slow)
2. Check Railway app status

## 📊 NEXT STEPS AFTER URL FOUND

1. ✅ Test `/health` endpoint
2. ✅ Test `/api/v1/signal/latest` endpoint
3. ✅ Update frontend with this URL
4. ✅ Test end-to-end flow

---

**Need help?** Check Railway logs or documentation.
