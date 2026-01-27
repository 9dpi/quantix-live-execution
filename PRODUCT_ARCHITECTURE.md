# Quantix Hybrid Architecture (Home Miner Mode)

Due to Twelve Data's blocking of Cloud Center IPs (Railway/AWS), the Data Ingestion and Analysis layers have been moved to the Local Environment (Residential IP), while the Storage and Presentation layers remain Cloud-native.

[T0] Live Market Data
(continuous feed via Twelve Data API)
      ↓
[T0 + Δ] Quantix AI Core (HOME MINER) 🏠
   * Running Locally on Operator Machine *
   - Repo: https://github.com/9dpi/quantix-ai-core
   - Market analysis runs every **15 seconds**
   - Bypasses Cloud IP blocking (Residential IP)
   - Function:
      • Ingests Live Data
      • Analyzes Structure
      • PUSHES 'Locked' Signals to Supabase Cloud
   - Frequency: Max **1 signal per day**
      ↓
      (Secure Write / HTTPS)
      ↓
[T1] Backend - The Vault (CLOUD) ☁️
   Immutable Record (Supabase)
   - Append-only Log
   - Single Source of Truth for Web & Bot
      ↓
-----------------------------------------------------------
      ↓                                   ↓
[T2] Web MPV (Signal Genius)         [T2] Telegram Bot
   (Railway Hosted)                    (GitHub Actions)
   - Reads T1 (Supabase)               - Reads T1 (Supabase)
   - Displays Active Signal            - Notifies Users
      ↓
[T3] Execution Layer
   - Reads T1 (Supabase)
   - Executes trade (Demo/Live)
