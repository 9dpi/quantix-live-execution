# Deployment Guide - Signal Genius AI

Complete guide to deploy Signal Genius AI to production.

## 📋 Prerequisites

- GitHub account
- Git installed locally
- (Optional) Railway account for backend
- (Optional) Telegram Bot token for notifications

---

## 🌐 Deploy Frontend to GitHub Pages

### Step 1: Create GitHub Repository

1. Go to [GitHub](https://github.com/new)
2. Create new repository:
   - **Name**: `signal-genius-ai`
   - **Description**: Professional EUR/USD Forex Trading Signals powered by AI
   - **Visibility**: Public (or Private if you have Pro)
   - **DO NOT** initialize with README (we already have one)

### Step 2: Push Code to GitHub

```bash
# Navigate to project directory
cd d:/Automator_Prj/Quantix_MPV/Signal_Genius_AI

# Add remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/signal-genius-ai.git

# Push to GitHub
git branch -M main
git push -u origin main
```

### Step 3: Enable GitHub Pages

1. Go to repository **Settings**
2. Navigate to **Pages** (left sidebar)
3. Under **Source**:
   - Branch: `main`
   - Folder: `/frontend`
4. Click **Save**
5. Wait 1-2 minutes for deployment
6. Your site will be live at: `https://YOUR_USERNAME.github.io/signal-genius-ai/`

### Step 4: Verify Deployment

Visit your GitHub Pages URL and verify:
- ✅ Logo and branding display correctly
- ✅ Signal card shows mock data
- ✅ Auto-refresh indicator is working
- ✅ Mobile responsive design works
- ✅ All info cards are visible

---

## 🤖 Deploy Telegram Bot

### Option 1: Railway (Recommended)

#### Step 1: Prepare for Railway

Create `railway.json` in project root:

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "cd telegram && python bot.py",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

Create `Procfile` in project root:

```
worker: cd telegram && python bot.py
```

#### Step 2: Deploy to Railway

1. Go to [Railway](https://railway.app/)
2. Click **New Project** → **Deploy from GitHub repo**
3. Select your `signal-genius-ai` repository
4. Railway will auto-detect Python

#### Step 3: Add Environment Variables

In Railway dashboard, go to **Variables** and add:

```
TELEGRAM_BOT_TOKEN=your_actual_bot_token
TELEGRAM_CHAT_ID=your_actual_chat_id
API_ENDPOINT=https://your-backend-url/api/v1/lab/market-reference
```

#### Step 4: Deploy

- Click **Deploy**
- Monitor logs to ensure bot starts successfully
- Look for: `🤖 Signal Genius AI Telegram Bot started`

### Option 2: Fly.io

```bash
# Install flyctl
# Windows: iwr https://fly.io/install.ps1 -useb | iex

# Login
fly auth login

# Navigate to telegram directory
cd telegram

# Launch app
fly launch --name signal-genius-bot

# Set secrets
fly secrets set TELEGRAM_BOT_TOKEN=your_token
fly secrets set TELEGRAM_CHAT_ID=your_chat_id
fly secrets set API_ENDPOINT=your_api_url

# Deploy
fly deploy
```

### Option 3: Local/VPS

```bash
# Install dependencies
cd telegram
pip install -r requirements.txt

# Set environment variables
export TELEGRAM_BOT_TOKEN=your_token
export TELEGRAM_CHAT_ID=your_chat_id
export API_ENDPOINT=your_api_url

# Run with nohup (keeps running after logout)
nohup python bot.py > bot.log 2>&1 &

# Or use systemd service (recommended for production)
```

---

## 🔧 Deploy Backend API (Future)

When backend is ready, deploy to Railway:

### Step 1: Create Backend Service

```bash
# In Railway dashboard
# New Service → Deploy from GitHub → Select repo
# Set root directory to /backend (when created)
```

### Step 2: Environment Variables

```
DATABASE_URL=your_supabase_or_postgres_url
REDIS_URL=your_redis_url (optional)
ALLOWED_ORIGINS=https://YOUR_USERNAME.github.io
```

### Step 3: Update Frontend

Update `frontend/signals.js`:

```javascript
const CONFIG = {
  API_ENDPOINT: 'https://your-railway-backend.railway.app/api/v1/lab/market-reference',
  // ... rest of config
};
```

Commit and push changes to update GitHub Pages.

---

## 🔐 Security Checklist

Before going live:

- [ ] **Never commit** `.env` files with real tokens
- [ ] Use **environment variables** for all secrets
- [ ] Enable **branch protection** on main branch
- [ ] Add **CORS** restrictions on backend
- [ ] Use **HTTPS** for all API calls
- [ ] Implement **rate limiting** on API
- [ ] Add **monitoring** (Sentry, LogRocket, etc.)

---

## 📊 Monitoring

### Frontend (GitHub Pages)

- Check GitHub Actions for build status
- Use browser DevTools to check for errors
- Monitor with Google Analytics (optional)

### Telegram Bot

**Railway:**
- View logs in Railway dashboard
- Set up alerts for crashes
- Monitor resource usage

**Fly.io:**
```bash
fly logs
fly status
```

**Local/VPS:**
```bash
tail -f bot.log
```

### Health Checks

Create a simple health check endpoint:

```python
# In bot.py, add:
from datetime import datetime

def health_check():
    return {
        "status": "healthy",
        "last_check": datetime.now(timezone.utc).isoformat(),
        "signals_sent_today": len(sent_signals_today)
    }
```

---

## 🐛 Troubleshooting

### GitHub Pages not updating

```bash
# Clear cache and force push
git commit --allow-empty -m "Trigger rebuild"
git push
```

### Telegram bot not sending

1. Check bot token is correct
2. Verify chat ID is correct
3. Check API endpoint is accessible
4. Review bot logs for errors
5. Test API endpoint manually:
   ```bash
   curl "https://your-api/api/v1/lab/market-reference?symbol=EURUSD&tf=M15"
   ```

### Auto-refresh not working

1. Check browser console for errors
2. Verify `signals.js` is loaded
3. Check network tab for API calls
4. Ensure no CORS errors

---

## 📈 Post-Deployment

### Update README

Add your live URLs to README.md:

```markdown
## 🌐 Live Demo

- **Web App**: https://YOUR_USERNAME.github.io/signal-genius-ai/
- **Telegram Bot**: @YourBotUsername
```

### Share with Users

1. Test all features thoroughly
2. Create demo video/screenshots
3. Share on social media
4. Collect feedback
5. Iterate and improve

---

## 🎯 Success Metrics

Track these KPIs:

- **Web Traffic**: Daily/monthly visitors
- **Signal Quality**: Win rate, average pips
- **User Engagement**: Time on site, return visitors
- **Telegram Growth**: Subscriber count, engagement rate
- **System Health**: Uptime, response time, error rate

---

## 📞 Support

If you encounter issues:

1. Check this guide first
2. Review error logs
3. Search GitHub Issues
4. Create new issue with details
5. Contact support team

---

**Good luck with your deployment! 🚀**
