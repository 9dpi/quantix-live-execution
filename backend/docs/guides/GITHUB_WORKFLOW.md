# 🚀 Quy trình 4 bước đưa MVP lên GitHub

Hướng dẫn chuyên nghiệp và an toàn để đưa Signal Genius AI lên GitHub.

---

## ✅ Bước 1: Khởi tạo Git và tập tin quan trọng

### 1.1. Kiểm tra Git đã được khởi tạo

```bash
cd d:/Automator_Prj/Quantix_MPV/Signal_Genius_AI
git status
```

✅ **Đã hoàn thành**: Git repository đã được khởi tạo.

### 1.2. Kiểm tra file .gitignore

File `.gitignore` **CỰC KỲ QUAN TRỌNG** để không làm lộ mật khẩu (API Keys, Token) lên môi trường công cộng.

✅ **Đã hoàn thành**: File `.gitignore` đã được tạo với nội dung:

```
.env
.env.local
.env.*.local
__pycache__/
node_modules/
*.log
.DS_Store
telegram/.env
telegram/config.json
```

### 1.3. Verify không có file nhạy cảm

```bash
# Kiểm tra xem có file .env nào sẽ bị commit không
git status | grep .env

# Nếu có .env trong danh sách, DỪNG NGAY và xóa nó khỏi staging
git rm --cached .env
```

---

## ✅ Bước 2: Kết nối với GitHub Remote

### 2.1. Tạo Repository trên GitHub

1. Truy cập: https://github.com/new
2. Điền thông tin:
   - **Repository name**: `signal-genius-ai`
   - **Description**: `Professional EUR/USD Forex Trading Signals powered by AI - MVP for Client`
   - **Visibility**: **🔒 Private** (Khuyến nghị - đây là tài sản trí tuệ của bạn và Irfan)
   - **❌ KHÔNG** check "Initialize this repository with a README"
3. Click **Create repository**

### 2.2. Kết nối Local với GitHub

Sau khi tạo repo, GitHub sẽ hiển thị URL. Copy URL đó và chạy:

```bash
# Thay YOUR_USERNAME bằng GitHub username thực của bạn
git remote add origin https://github.com/YOUR_USERNAME/signal-genius-ai.git

# Đổi tên branch thành main (chuẩn hiện đại)
git branch -M main

# Verify remote đã được thêm
git remote -v
```

**Kết quả mong đợi**:
```
origin  https://github.com/YOUR_USERNAME/signal-genius-ai.git (fetch)
origin  https://github.com/YOUR_USERNAME/signal-genius-ai.git (push)
```

---

## ✅ Bước 3: Commit và Push bản đầu tiên

### 3.1. Kiểm tra trạng thái

```bash
# Xem các file sẽ được commit
git status

# Xem chi tiết thay đổi
git diff
```

### 3.2. Stage tất cả files

```bash
git add .
```

### 3.3. Commit với message chuẩn

```bash
git commit -m "feat: initial mvp structure for signal genius ai"
```

**Giải thích commit message**:
- `feat:` - Feature mới (theo Conventional Commits)
- Message rõ ràng, lowercase, không dấu chấm cuối

### 3.4. Push lên GitHub

```bash
# Push lần đầu với -u để set upstream
git push -u origin main
```

**Nếu gặp lỗi authentication**:
- GitHub không còn hỗ trợ password
- Cần dùng **Personal Access Token** (PAT)
- Hướng dẫn tạo PAT:
  1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
  2. Generate new token
  3. Chọn scopes: `repo` (full control)
  4. Copy token và dùng làm password khi push

### 3.5. Verify trên GitHub

1. Truy cập: `https://github.com/YOUR_USERNAME/signal-genius-ai`
2. Kiểm tra:
   - ✅ Tất cả files đã được push
   - ✅ **KHÔNG** có file `.env`
   - ✅ README.md hiển thị đẹp
   - ✅ Cấu trúc thư mục đúng

---

## ✅ Bước 4: Cấu hình "Secrets" cho Deployment

Vì chúng ta đã chặn file `.env` (chứa Token/Key), bạn cần chuẩn bị sẵn các giá trị này để nhập vào platform deployment.

### 4.1. Chuẩn bị danh sách Secrets

Tạo file **local** (KHÔNG commit) để lưu secrets:

```bash
# Tạo file secrets.txt (đã có trong .gitignore)
notepad secrets.txt
```

Nội dung mẫu:

```
=== SIGNAL GENIUS AI SECRETS ===
(File này CHỈ lưu local, KHÔNG push lên Git)

[Telegram Bot]
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=-1001234567890

[Backend API]
API_ENDPOINT=https://signal-genius-backend.railway.app/api/v1/lab/market-reference

[Database - Supabase]
SUPABASE_URL=https://xxxxxxxxxxxxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

[Market Data]
MARKET_DATA_API_KEY=your_api_key_here

[Monitoring]
SENTRY_DSN=https://xxxxx@sentry.io/xxxxx
```

### 4.2. Cấu hình Secrets trên GitHub (cho GitHub Actions)

1. Vào repository: `https://github.com/YOUR_USERNAME/signal-genius-ai`
2. **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Thêm từng secret:

| Name | Value |
|------|-------|
| `TELEGRAM_BOT_TOKEN` | `your_actual_token` |
| `TELEGRAM_CHAT_ID` | `your_actual_chat_id` |
| `API_ENDPOINT` | `your_api_url` |
| `SUPABASE_URL` | `your_supabase_url` |
| `SUPABASE_KEY` | `your_supabase_key` |

### 4.3. Cấu hình Secrets trên Railway

#### Khi deploy Telegram Bot:

1. Vào Railway Dashboard: https://railway.app/
2. Click **New Project** → **Deploy from GitHub repo**
3. Chọn repository `signal-genius-ai`
4. Railway sẽ auto-detect Python
5. Click vào service → Tab **Variables**
6. Thêm variables:

```
TELEGRAM_BOT_TOKEN = your_actual_token
TELEGRAM_CHAT_ID = your_actual_chat_id
API_ENDPOINT = https://your-backend-url/api/v1/lab/market-reference
```

7. Click **Deploy**

#### Khi deploy Backend (sau này):

Tương tự, thêm:
```
SUPABASE_URL = your_supabase_url
SUPABASE_KEY = your_supabase_key
MARKET_DATA_API_KEY = your_api_key
```

---

## 📊 Mô hình luồng dữ liệu sau khi Push lên GitHub

```
┌─────────────────────────────────────────────────────────────┐
│                         DEVELOPER                            │
│                                                              │
│  Local Code → git push → GitHub Repository (Private)        │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                          GITHUB                              │
│                                                              │
│  • Lưu trữ code (KHÔNG có secrets)                          │
│  • Trigger webhook khi có push mới                          │
│  • GitHub Actions (CI/CD) - Optional                        │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    RAILWAY (Auto-Deploy)                     │
│                                                              │
│  • Nhận webhook từ GitHub                                   │
│  • Pull code mới nhất                                       │
│  • Build: pip install -r requirements.txt                   │
│  • Inject secrets từ Variables                              │
│  • Deploy: python telegram/bot.py                           │
│  • Bot chạy 24/7                                            │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                         SUPABASE                             │
│                                                              │
│  • Nhận kết nối từ Railway                                  │
│  • Lưu signal history                                       │
│  • Lưu user data, analytics                                 │
│  • Real-time sync                                           │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                      END USERS                               │
│                                                              │
│  • Web: GitHub Pages (frontend)                             │
│  • Telegram: Nhận signals từ Bot                            │
└─────────────────────────────────────────────────────────────┘
```

### Luồng tự động hóa:

1. **Developer** push code → GitHub
2. **GitHub** trigger webhook → Railway
3. **Railway** auto-deploy bot mới
4. **Bot** kết nối Supabase, gửi signals
5. **Users** nhận signals qua Telegram/Web

**Lợi ích**:
- ✅ Mỗi lần `git push` → Auto-deploy
- ✅ Không cần SSH vào server
- ✅ Rollback dễ dàng nếu có lỗi
- ✅ Logs tập trung trên Railway
- ✅ Scaling tự động khi cần

---

## ✅ Checklist hoàn thành

- [ ] **Bước 1**: Git initialized, `.gitignore` đã có
- [ ] **Bước 2**: GitHub repo created (Private), remote added
- [ ] **Bước 3**: Code đã push lên GitHub
- [ ] **Bước 4**: Secrets đã chuẩn bị, sẵn sàng nhập vào Railway
- [ ] **Verify**: Không có `.env` trên GitHub
- [ ] **Verify**: README hiển thị đẹp trên GitHub
- [ ] **Next**: Deploy Telegram bot lên Railway

---

## 🎯 Commands tổng hợp

```bash
# Bước 1: Verify Git
cd d:/Automator_Prj/Quantix_MPV/Signal_Genius_AI
git status

# Bước 2: Add remote
git remote add origin https://github.com/YOUR_USERNAME/signal-genius-ai.git
git branch -M main

# Bước 3: Push
git add .
git commit -m "feat: initial mvp structure for signal genius ai"
git push -u origin main

# Bước 4: Chuẩn bị secrets (local file, không commit)
notepad secrets.txt
```

---

## 🚨 Troubleshooting

### Lỗi: "remote origin already exists"

```bash
# Xóa remote cũ
git remote remove origin

# Thêm lại
git remote add origin https://github.com/YOUR_USERNAME/signal-genius-ai.git
```

### Lỗi: Authentication failed

- Dùng Personal Access Token thay vì password
- Hoặc setup SSH key

### Lỗi: "Updates were rejected"

```bash
# Pull trước khi push
git pull origin main --rebase
git push origin main
```

---

## 📞 Hỗ trợ

Nếu gặp vấn đề:
1. Đọc kỹ error message
2. Check `.gitignore` đã đúng chưa
3. Verify remote URL
4. Xem `SECRETS_GUIDE.md` để cấu hình secrets

---

**Chúc bạn deploy thành công! 🚀**
