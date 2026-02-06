// === Quantix v3 Architecture - Current Implementation ===
// NOTE: Railway services not yet deployed. Using direct Supabase for now.
// Future migration path:
//   1. Deploy Quantix AI Core → https://quantix-ai-core-production.up.railway.app
//   2. Deploy Quantix Watcher → https://quantix-watcher-production.up.railway.app
//   3. Update endpoints in this file

// Supabase Direct Connection (Current)
const SUPABASE_URL = "https://wttsaprezgvircanthbk.supabase.co";
const SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Ind0dHNhcHJlemd2aXJjYW50aGJrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2ODM2ODA3MCwiZXhwIjoyMDgzOTQ0MDcwfQ.QGewz8bDfBC6vJce6g4-sHA164bL1y0u71d6HH7PYVk";

// API Configuration
const API = {
    // Direct Supabase REST API
    supabaseRest: `${SUPABASE_URL}/rest/v1/fx_signals`,

    // Future Railway endpoints (uncomment when deployed)
    // aiCore: "https://quantix-ai-core-production.up.railway.app/api/signals/latest",
    // watcher: "https://quantix-watcher-production.up.railway.app/api/signals/history",
};

let historyOffset = 0;
const PAGE_SIZE = 50;
let pHistory = [];
let livePrice = null;
let prevPrice = 0;
