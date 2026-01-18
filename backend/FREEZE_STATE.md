## MVP Freeze – 2026-01-18

### Known Good State
Backend:
- Railway Project: signalgeniusai-production
- Health Check: `/health` -> `{"status": "ok"}`
- Signal API: `/signal/latest` -> Returns complete signal object (asset, direction, entry, tp, sl, strategy, etc.)
- Stability: No 502 Bad Gateway, no container crashes observed.

Frontend:
- GitHub Pages Deployment: Stable at `/signal-genius-ai/`
- Layout: 500px centered card + 500px history stack (Bento 2.0 ASCII-inspired).
- Feature Coverage: 1:1 format match with Telegram, 60s auto-refresh, TTL/Badge logic (LIVE/EXPIRED).
- State Persistence: Auto-refresh preserves scroll position, countdown in bottom indicator.

### Scope Control (FREEZE RULES)
**STRICTLY FROZEN (DO NOT TOUCH):**
- `main.py` (FastAPI core - moved to root)
- `signal_engine.py` (Engine logic - renamed to avoid conflict)
- `market.py` (Data fetching - moved to root)
- `telegram.py` (Alert formatting - moved to root)
- `requirements.txt` (Moved to root)
- `Dockerfile` (Root)
- Railway Service configuration (PORT, Start Command).

**OPEN FOR MODIFICATION:**
- `index.html` (Markup refinement)
- `signals.js` (Rendering logic)
- `payload.js` (Orchestration/Timer)
- `styles.css` (Visual polish)

### Restoration Procedure
If the system becomes unstable or logic drifts:
1. `git checkout mvp-freeze-2026-01-18`
2. `git push origin main --force` (Use with caution)

**DO NOT:**
- Modify backend logic.
- Add new endpoints.
- Change API response schema.
