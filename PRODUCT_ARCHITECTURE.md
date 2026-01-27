[T0] Live Market Data
(continuous feed via Twelve Data API)
      ↓
[T0 + Δ] Quantix AI Core - The Brain
   - Repo: https://github.com/9dpi/quantix-ai-core
   - Market analysis runs every **15 seconds**
   - Continuously evaluates structural conditions (BOS/Liquidity)
   - Detects highest-confidence moment (> 75%)
   - CREATE signal candidate (Visible in Quantix Lab)
   - LOCK signal with timestamp (Once daily criteria met)
   - Frequency rule:
      • Analysis: every **15 seconds**
      • Signal creation (LOCK): max **1 signal per day**
      ↓
[T1] Backend - The Vault
   Immutable Record (Supabase)
   (append-only, source of truth for all layers)
      ↓
-----------------------------------------------------------
      ↓                                   ↓
[T2] Web MPV (Signal Genius)         [T2] Telegram Bot
   - Domain: https://signalgeniusai.com
   - Repo: https://github.com/9dpi/quantix-live-execution
   - Read-only snapshot from [T1]
   - Shows: Signal details, Creation time, Validity, Frequency note
      ↓
[T3] Execution Layer - The Arm
   Manual / AUTO v0 (quantix-live-execution)
   - Repo: https://github.com/9dpi/quantix-live-execution
   - Read-only consumption from [T1]
   - Daily execution cap: **1/day** enforced
      ↓
[T4] Market Outcome
   TP / SL / Manual close detection

