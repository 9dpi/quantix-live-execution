// Quantix Global Configuration (v3.2)
window.CONFIG = {
    API_BASE: "https://quantixaicore-production.up.railway.app",
    SUPABASE_URL: "https://wttsaprezgvircanthbk.supabase.co",
    SUPABASE_KEY: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Ind0dHNhcHJlemd2aXJjYW50aGJrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2ODM2ODA3MCwiZXhwIjoyMDgzOTQ0MDcwfQ.QGewz8bDfBC6vJce6g4-sHA164bL1y0u71d6HH7PYVk",

    // Feature Flags & Settings
    USE_SUPABASE_FALLBACK: true,
    DEFAULT_LOOKBACK_DAYS: 7,
    PAGE_SIZE: 50,

    // API Paths
    get AI_CORE_API() { return `${this.API_BASE}/api/v1`; },
    get SUPABASE_REST() { return `${this.SUPABASE_URL}/rest/v1`; }
};

console.log("🚀 Quantix Config Loaded:", window.CONFIG.API_BASE);
