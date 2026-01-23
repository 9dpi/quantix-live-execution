# Quantix AI Core v1.0 – FROZEN SNAPSHOT

**Date:** 2026-01-23 16:50 (GMT+7)
**Status:** ❄️ FROZEN
**Purpose:** Baseline before Shadow Learning (Phase 1.5)

## 🔒 Frozen Components

### (A) AI Core (The Brain)
- `signal_engine.py`: Thừa hành việc tạo signal và tính confidence.
- `external_client.py`: Cổng nạp dữ liệu TwelveData.
- `main.py`: Core API và logic daily reset.

### (B) Config & Thresholds
- `LIVE_MODE`: Định nghĩa trong .env.
- `Confidence Rules`: 55-95 range (Randomized baseline in v1.0).
- `Symbol/TF`: EUR/USD | M15.

### (C) Gating Logic (The Guard)
- `auto_executor.py`: Chứa `DailyExecutionGate` (Max 1/day).
- `TTL`: 90 minutes.

### (D) Data Schema
- `auto_execution_log.jsonl`: Append-only, standard JSONL.
- `daily_gate_log.jsonl`: Ghi nhận mọi quyết định SKIP/EXECUTE.

---
**Restoration Guide:**
Current Git Tag: `quantix-core-v1.0-freeze`
Commit Hash: [To be updated after commit]
