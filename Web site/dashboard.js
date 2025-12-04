/* dashboard.js: handles node list and embedding into iframe */
async function refreshNodes() {
  const container = document.getElementById('nodes-list');
  const lastEl = document.getElementById('nodes-last-refresh');
  if (!container) return;
  try {
    const nodes = await apiFetch('/api/nodes');
    container.innerHTML = '';
    nodes.forEach(n => {
      const el = document.createElement('div');
      el.className = 'node-card';
      const statusClass = (n.status && n.status.toLowerCase() !== 'ok' && n.status.toLowerCase() !== 'up') ? 'status-down' : 'status-up';
      el.innerHTML = `
        <div><strong>${n.name}</strong> <small>(${n.role})</small></div>
        <div>Host: ${n.host}:${n.port}</div>
        <div>Status: <span class="${statusClass}">${n.status || 'unknown'}</span></div>
        <div>Uptime: ${n.uptime || '-'}</div>
        <div style="margin-top:8px;">
          <button class="open-btn">Open</button>
          <button class="embed-btn">Embed</button>
          <button class="metrics-btn">Metrics</button>
        </div>
        <div class="metrics" style="display:none; margin-top:8px;"></div>
      `;
      // button handlers
      el.querySelector('.open-btn').addEventListener('click', () => {
        const url = (n.scheme || 'http://') + n.host + (n.port ? ':' + n.port : '');
        openNodeSite(url, '_blank');
      });
      el.querySelector('.embed-btn').addEventListener('click', () => {
        const url = (n.scheme || 'http://') + n.host + (n.port ? ':' + n.port : '');
        const iframe = document.getElementById('node-monitor');
        iframe.src = url;
      });
      el.querySelector('.metrics-btn').addEventListener('click', async () => {
        const mEl = el.querySelector('.metrics');
        if (mEl.style.display === 'none') {
          // fetch metrics
          try {
            const metrics = await apiFetch('/api/node/' + encodeURIComponent(n.id) + '/status');
            mEl.style.display = 'block';
            mEl.innerHTML = '<pre>' + JSON.stringify(metrics, null, 2) + '</pre>';
          } catch (e) {
            mEl.style.display = 'block';
            mEl.innerHTML = '<em>Could not fetch metrics: ' + e.message + '</em>';
          }
        } else {
          mEl.style.display = 'none';
        }
      });
      container.appendChild(el);
    });
    if (lastEl) lastEl.textContent = 'Last updated: ' + new Date().toLocaleTimeString();
  } catch (err) {
    console.error('refreshNodes failed', err);
    container.innerHTML = '<div style="color:red">Could not load nodes: ' + err.message + '</div>';
  }
}

document.getElementById('refresh-nodes').addEventListener('click', refreshNodes);
window.addEventListener('load', refreshNodes);

// Optionally, refresh periodically:
setInterval(refreshNodes, 15000);