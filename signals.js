export function renderRow(data) {
  return `
    <tr>
      <td>${data.asset}</td>
      <td>${data.direction}</td>
      <td>${data.entry}</td>
      <td>${data.tp}</td>
      <td>${data.sl}</td>
      <td>${data.confidence}%</td>
    </tr>
  `;
}

export function renderStats(data) {
  return `
    <div class="stat">
      <strong>Strategy:</strong> ${data.strategy}
    </div>
  `;
}
