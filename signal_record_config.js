// Quantix Global Configuration (v3.2)
window.CONFIG = {
    API_BASE: "https://quantixaicore-production.up.railway.app",
    SUPABASE_URL: "https://wttsaprezgvircanthbk.supabase.co",
    SUPABASE_KEY: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Ind0dHNhcHJlemd2aXJjYW50aGJrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjgzNjgwNzAsImV4cCI6MjA4Mzk0NDA3MH0.Ql8pjXH-43_miOVTTWZYgiNOfNtBQVISViYOBrh6vfM",

    // Feature Flags & Settings
    USE_SUPABASE_FALLBACK: true,
    DEFAULT_LOOKBACK_DAYS: 7,
    PAGE_SIZE: 50,

    // API Paths
    get AI_CORE_API() { return `${this.API_BASE}/api/v1`; },
    get SUPABASE_REST() { return `${this.SUPABASE_URL}/rest/v1`; }
};

console.log("🚀 Quantix Config Loaded:", window.CONFIG.API_BASE);
