# 🚀 Quick Start - Push to GitHub

## Step-by-Step Guide

### 1️⃣ Create GitHub Repository

1. Go to: https://github.com/new
2. Fill in:
   - **Repository name**: `signal-genius-ai`
   - **Description**: `Professional EUR/USD Forex Trading Signals powered by AI`
   - **Visibility**: Public
   - **DO NOT** check "Initialize with README"
3. Click **Create repository**

### 2️⃣ Copy Your Repository URL

After creating, you'll see a URL like:
```
https://github.com/YOUR_USERNAME/signal-genius-ai.git
```

Copy this URL!

### 3️⃣ Push Code to GitHub

Open PowerShell in the project directory and run:

```powershell
# Navigate to project (if not already there)
cd d:/Automator_Prj/Quantix_MPV/Signal_Genius_AI

# Add GitHub remote (replace YOUR_USERNAME with your actual GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/signal-genius-ai.git

# Rename branch to main
git branch -M main

# Push to GitHub
git push -u origin main
```

### 4️⃣ Enable GitHub Pages

1. Go to your repository on GitHub
2. Click **Settings** (top menu)
3. Scroll down and click **Pages** (left sidebar)
4. Under **Source**:
   - Branch: `main`
   - Folder: `/frontend`
5. Click **Save**
6. Wait 1-2 minutes

### 5️⃣ Access Your Live Site

Your site will be available at:
```
https://YOUR_USERNAME.github.io/signal-genius-ai/
```

### 6️⃣ Verify Everything Works

Visit your site and check:
- ✅ Logo displays
- ✅ Signal card shows
- ✅ Auto-refresh indicator works
- ✅ Mobile responsive
- ✅ All info cards visible

---

## 🎉 Done!

Your Signal Genius AI MVP is now live!

### Next Steps:

1. **Share the link** with potential users
2. **Setup Telegram bot** (see `telegram/README.md`)
3. **Build the backend** when ready
4. **Collect feedback** and iterate

---

## 📝 Quick Commands Reference

```powershell
# Check Git status
git status

# View commit history
git log --oneline

# Make changes and commit
git add .
git commit -m "Your commit message"
git push

# View remote URL
git remote -v
```

---

## ❓ Troubleshooting

**Problem**: `git push` asks for username/password

**Solution**: Use Personal Access Token instead of password
1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Generate new token (classic)
3. Use token as password when prompted

**Problem**: GitHub Pages shows 404

**Solution**: 
1. Check Settings → Pages is configured correctly
2. Ensure branch is `main` and folder is `/frontend`
3. Wait a few minutes and refresh
4. Check repository is public

**Problem**: Site loads but no styling

**Solution**:
1. Check browser console for errors
2. Verify all files are in `/frontend` folder
3. Check file paths in `index.html`

---

**Need help?** Check `DEPLOYMENT.md` for detailed instructions!
