[T0] Live Market Data
(continuous feed via Twelve Data API)
      ↓
[T0 + Δ] Quantix AI Core - The Brain
   - Market analysis runs every **120 seconds**
   - Continuously evaluates structural conditions (BOS/Liquidity)
   - Detects highest-confidence moment (> 75%)
   - CREATE signal candidate (Visible in Quantix Lab)
   - LOCK signal with timestamp (Once daily criteria met)
   - Frequency rule:
      • Analysis: every **120 seconds**
      • Signal creation (LOCK): max **1 signal per day**
      ↓
[T1] Backend - The Vault
   Immutable Record (Supabase)
   (append-only, source of truth for all layers)
      ↓
-----------------------------------------------------------
      ↓                                   ↓
[T2] Web MPV (Signal Genius)         [T2] Telegram Bot
   Read-only snapshot                 Read-only snapshot
   Shows:                             Shows:
      - Signal details                   - Signal details
      - Creation time                    - Direction & Confidence
      - Validity status                  - Entry / TP / SL
      - Frequency note                   - 1:1 Mapping with Web
      ↓
[T3] Execution Layer - The Arm
   Manual / AUTO v0 (quantix-live-execution)
   - Read-only consumption from [T1]
   - Daily execution cap: **1/day** enforced
      ↓
[T4] Market Outcome
   TP / SL / Manual close detection
