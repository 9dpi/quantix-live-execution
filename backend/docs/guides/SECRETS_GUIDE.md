# 🔐 Secrets Configuration Guide

## ⚠️ QUAN TRỌNG: Bảo mật API Keys và Tokens

File này hướng dẫn cách cấu hình **Secrets** cho Signal Genius AI một cách an toàn.

**KHÔNG BAO GIỜ** commit các giá trị thực vào Git. Luôn sử dụng environment variables.

---

## 📋 Danh sách Secrets cần thiết

### 1. Telegram Bot (Bắt buộc cho Bot)

```bash
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=-1001234567890
```

**Cách lấy**:
- **Bot Token**: Nhắn tin với [@BotFather](https://t.me/botfather) → `/newbot`
- **Chat ID**: 
  - Personal: Nhắn tin với bot → Visit `https://api.telegram.org/bot<TOKEN>/getUpdates`
  - Group: Thêm bot vào group → Visit URL trên → Tìm `"chat":{"id":-XXXXX}`

### 2. Backend API (Khi có Backend)

```bash
API_ENDPOINT=https://your-backend.railway.app/api/v1/lab/market-reference
```

### 3. Database (Khi tích hợp Supabase)

```bash
SUPABASE_URL=https://xxxxxxxxxxxxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Cách lấy**:
- Vào Supabase Dashboard → Settings → API
- Copy **Project URL** và **anon/public key**

### 4. Market Data API (Khi tích hợp dữ liệu thực)

```bash
MARKET_DATA_API_KEY=your_dukascopy_or_other_api_key
```

### 5. Monitoring (Optional)

```bash
SENTRY_DSN=https://xxxxx@sentry.io/xxxxx
```

---

## 🚀 Cấu hình Secrets trên các Platform

### GitHub Secrets (cho GitHub Actions)

1. Vào repository trên GitHub
2. **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Thêm từng secret:
   - Name: `TELEGRAM_BOT_TOKEN`
   - Value: `your_actual_token`
5. Lặp lại cho tất cả secrets

### Railway Secrets

#### Option 1: Railway Dashboard (Recommended)

1. Vào Railway project
2. Click vào service (bot hoặc backend)
3. Tab **Variables**
4. Click **New Variable**
5. Thêm từng cặp key-value:
   ```
   TELEGRAM_BOT_TOKEN = your_actual_token
   TELEGRAM_CHAT_ID = your_actual_chat_id
   API_ENDPOINT = your_api_url
   ```
6. Click **Deploy** để apply changes

#### Option 2: Railway CLI

```bash
# Login
railway login

# Link to project
railway link

# Set secrets
railway variables set TELEGRAM_BOT_TOKEN=your_token
railway variables set TELEGRAM_CHAT_ID=your_chat_id
railway variables set API_ENDPOINT=your_api_url
```

### Fly.io Secrets

```bash
# Set secrets
fly secrets set TELEGRAM_BOT_TOKEN=your_token
fly secrets set TELEGRAM_CHAT_ID=your_chat_id
fly secrets set API_ENDPOINT=your_api_url

# List secrets (values are hidden)
fly secrets list
```

### Local Development

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` với editor:
   ```bash
   notepad .env
   # hoặc
   code .env
   ```

3. Điền giá trị thực:
   ```bash
   TELEGRAM_BOT_TOKEN=your_actual_token_here
   TELEGRAM_CHAT_ID=your_actual_chat_id_here
   API_ENDPOINT=http://localhost:8000/api/v1/lab/market-reference
   ```

4. **QUAN TRỌNG**: Đảm bảo `.env` đã có trong `.gitignore`
   ```bash
   # Kiểm tra
   cat .gitignore | grep .env
   ```

---

## ✅ Checklist Bảo mật

Trước khi push lên GitHub:

- [ ] File `.env` đã được thêm vào `.gitignore`
- [ ] Không có token/key nào trong code
- [ ] Tất cả secrets đều dùng environment variables
- [ ] File `.env.example` chỉ chứa placeholder
- [ ] Đã test local với `.env` thật
- [ ] Repository GitHub được set **Private** (recommended)
- [ ] Đã chuẩn bị sẵn list secrets để nhập vào Railway

---

## 🔍 Kiểm tra trước khi Push

```bash
# Kiểm tra xem có file nhạy cảm nào sẽ bị commit không
git status

# Kiểm tra nội dung sẽ được commit
git diff --cached

# Tìm kiếm token/key trong code (không nên có kết quả)
grep -r "TELEGRAM_BOT_TOKEN.*=" --include="*.py" --include="*.js"
```

---

## 🚨 Nếu đã commit nhầm Secret

### Nếu chưa push:

```bash
# Xóa commit cuối
git reset HEAD~1

# Hoặc sửa commit cuối
git commit --amend
```

### Nếu đã push:

1. **NGAY LẬP TỨC** revoke token/key cũ
2. Generate token/key mới
3. Xóa lịch sử Git (cẩn thận!):
   ```bash
   git filter-branch --force --index-filter \
   "git rm --cached --ignore-unmatch path/to/secret/file" \
   --prune-empty --tag-name-filter cat -- --all
   
   git push origin --force --all
   ```
4. Cập nhật token/key mới vào secrets

---

## 📊 Mô hình luồng Secrets

```
Local Development:
  .env (local only, gitignored)
    ↓
  Code reads from environment variables
    ↓
  Test locally

Production Deployment:
  GitHub Repository (no secrets in code)
    ↓
  Railway/Fly.io (secrets in platform variables)
    ↓
  Code reads from environment variables
    ↓
  Production running
```

---

## 🎯 Best Practices

1. **Separation of Concerns**
   - Development: `.env` local
   - Staging: Railway/Fly variables
   - Production: Railway/Fly variables (different values)

2. **Rotation**
   - Rotate tokens/keys định kỳ (3-6 tháng)
   - Revoke ngay nếu nghi ngờ bị lộ

3. **Access Control**
   - Chỉ share secrets với người cần thiết
   - Dùng password manager (1Password, Bitwarden)
   - Không gửi qua email/chat

4. **Monitoring**
   - Set up alerts cho unauthorized access
   - Review access logs định kỳ

---

## 📞 Hỗ trợ

Nếu gặp vấn đề về secrets:

1. Kiểm tra `.gitignore` đã đúng chưa
2. Verify environment variables đã set đúng
3. Check logs để xem có lỗi authentication không
4. Regenerate token/key nếu cần

---

**Luôn nhớ**: Bảo mật là ưu tiên hàng đầu! 🔒
