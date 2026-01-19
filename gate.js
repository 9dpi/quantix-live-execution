(function () {
    const PASSCODE = "1111"; // bạn có thể đổi
    const key = "quantix_access_granted";

    if (sessionStorage.getItem(key) === "true") return;

    const input = prompt("Enter access code:");
    if (input === PASSCODE) {
        sessionStorage.setItem(key, "true");
    } else {
        document.body.innerHTML = `
      <div style="
        height:100vh;
        display:flex;
        flex-direction:column;
        align-items:center;
        justify-content:center;
        background:#f8fafc;
        color:#0f172a;
        font-family:sans-serif;
        text-align:center;
        padding: 20px;
      ">
        <div style="background: white; padding: 40px; border-radius: 20px; box-shadow: 0 10px 25px rgba(0,0,0,0.05); border: 1px solid #e2e8f0;">
          <h2 style="margin-bottom: 10px;">🛡️ Live Validation Mode</h2>
          <p style="color: #64748b;">Access is restricted while signals are being verified by Quantix AI Core.</p>
          <button onclick="location.reload()" style="margin-top: 20px; padding: 10px 20px; background: #0891b2; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: 600;">Try Again</button>
        </div>
      </div>
    `;
    }
})();
