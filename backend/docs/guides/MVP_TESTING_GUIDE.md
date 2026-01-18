# 🧪 MVP v0 - TESTING GUIDE

## 📋 Overview

This guide helps you test the minimal MVP backend after Railway deployment.

---

## ⏳ STEP 1: Wait for Railway Deployment

1. Go to https://railway.app/dashboard
2. Find your "signal-genius-ai" project
3. Click on the deployment
4. Watch the build logs

**Expected logs:**
```
Building...
✅ Installing dependencies
✅ Successfully installed fastapi-0.109.0
✅ Successfully installed uvicorn-0.27.0
✅ Successfully installed httpx-0.25.2
✅ Successfully installed python-dotenv-1.0.0
Starting server...
✅ Application startup complete
✅ Uvicorn running on http://0.0.0.0:8000
```

**Deployment time:** ~2-5 minutes

---

## 🧪 STEP 2: Test Backend Endpoints

### Get Your Railway URL

In Railway dashboard:
- Click on your deployment
- Find "Domains" section
- Copy the URL (e.g., `https://signal-genius-ai-production.up.railway.app`)

### Test 1: Health Check

```bash
# Replace with your Railway URL
export API_URL="https://your-app.railway.app"

curl $API_URL/health
```

**Expected response:**
```json
{
  "status": "ok",
  "service": "signal-genius-ai-mvp"
}
```

✅ **Pass:** Status 200, JSON returned  
❌ **Fail:** Check Railway logs

### Test 2: Root Endpoint

```bash
curl $API_URL/
```

**Expected response:**
```json
{
  "name": "Signal Genius AI - MVP",
  "version": "0.1.0",
  "status": "operational",
  "endpoints": {
    "health": "/health",
    "latest_signal": "/api/v1/signal/latest"
  }
}
```

### Test 3: Latest Signal

```bash
curl $API_URL/api/v1/signal/latest
```

**Expected response:**
```json
{
  "status": "ok",
  "source": "external",
  "asset": "EUR/USD",
  "payload": {
    "asset": "EUR/USD",
    "direction": "BUY",
    "confidence": 96,
    "entry": [1.16710, 1.16750],
    "tp": 1.17080,
    "sl": 1.16480,
    "timeframe": "M15",
    "session": "London-NewYork",
    "source": "mock"
  }
}
```

**Note:** If Quantix API is unavailable, it returns mock data (this is expected and OK for MVP).

---

## 🌐 STEP 3: Test from Browser

Open browser and visit:

1. `https://your-app.railway.app/health`
2. `https://your-app.railway.app/api/v1/signal/latest`

You should see JSON responses in the browser.

---

## 🎨 STEP 4: Connect Frontend

### Update Frontend JavaScript

Find your frontend JavaScript file (e.g., `frontend/signals.js`) and update:

```javascript
// OLD (if you had this)
const API_URL = "http://localhost:8000";

// NEW
const API_URL = "https://your-app.railway.app";

// Fetch signal function
async function fetchLatestSignal() {
    try {
        const response = await fetch(`${API_URL}/api/v1/signal/latest`);
        const data = await response.json();
        
        console.log('Signal data:', data);
        
        // For MVP: Just display raw JSON
        document.getElementById('signal-data').innerHTML = 
            `<pre>${JSON.stringify(data, null, 2)}</pre>`;
            
        return data;
        
    } catch (error) {
        console.error('Error fetching signal:', error);
        document.getElementById('signal-data').innerHTML = 
            `<p style="color: red;">Error: ${error.message}</p>`;
    }
}

// Call on page load
document.addEventListener('DOMContentLoaded', () => {
    fetchLatestSignal();
    
    // Optional: Auto-refresh every 30 seconds
    setInterval(fetchLatestSignal, 30000);
});
```

### Add HTML Element

In your `index.html`:

```html
<div id="signal-data">
    <p>Loading signal data...</p>
</div>
```

---

## ✅ STEP 5: Verify MVP Works

### Backend Checklist

- [ ] `/health` returns 200 OK
- [ ] `/api/v1/signal/latest` returns JSON
- [ ] No CORS errors in browser console
- [ ] Response time < 2 seconds
- [ ] Railway deployment is stable

### Frontend Checklist

- [ ] Page loads without errors
- [ ] Signal data displays (even if raw JSON)
- [ ] No CORS errors in console
- [ ] Refresh button works
- [ ] Auto-refresh works (if implemented)

### Browser Console Check

Open browser DevTools (F12) and check:

```
✅ No red errors
✅ Network tab shows successful API calls
✅ Response is valid JSON
```

---

## 🎉 SUCCESS CRITERIA

**MVP is ALIVE when:**

1. ✅ Backend health check works
2. ✅ Backend returns signal data
3. ✅ Frontend displays data (even if ugly)
4. ✅ No CORS errors
5. ✅ Page reload works

**If all pass → Commit and tag:**

```bash
git add .
git commit -m "feat: frontend connected to MVP backend"
git tag mvp-v0
git push origin main --tags
```

---

## 🐛 TROUBLESHOOTING

### Issue: CORS Error

**Symptom:**
```
Access to fetch at 'https://...' from origin 'https://...' 
has been blocked by CORS policy
```

**Solution:**
- Check `main.py` has `allow_origins=["*"]`
- Redeploy if needed
- Clear browser cache

### Issue: 404 Not Found

**Check:**
- Railway URL is correct
- Endpoint path is correct (`/api/v1/signal/latest`)
- Railway deployment succeeded

### Issue: 500 Internal Server Error

**Check:**
- Railway logs for errors
- `external_client.py` is working
- Dependencies installed correctly

### Issue: Timeout

**Check:**
- Railway app is running (not sleeping)
- Network connection is stable
- Quantix API is accessible (or fallback to mock works)

---

## 📊 EXPECTED TIMELINE

| Step | Time | Status |
|------|------|--------|
| 1. Wait for Railway | 2-5 min | ⏳ In progress |
| 2. Test backend | 5 min | ⏳ Pending |
| 3. Test browser | 2 min | ⏳ Pending |
| 4. Connect frontend | 15 min | ⏳ Pending |
| 5. Verify MVP | 5 min | ⏳ Pending |
| **Total** | **~30 min** | **Per workflow** |

---

## 🎯 NEXT AFTER MVP WORKS

**Don't add features yet!** First:

1. ✅ Verify MVP is stable
2. ✅ Test on different browsers
3. ✅ Test on mobile
4. ✅ Monitor for 1 hour
5. ✅ Tag as `mvp-v0`

**Then, in order:**
1. Add confidence filter (backend)
2. Add warning label (frontend)
3. Add caching
4. Add database (optional)
5. Add Telegram (optional)

---

**Current Status:** 🟡 Waiting for Railway deployment  
**Next Action:** Test endpoints when deployment completes  
**ETA:** ~5 minutes

---

**Last Updated:** 2026-01-15 22:47 UTC+7
