// Sidebar toggle
const sidebar = document.getElementById('sidebar');
const overlay = document.getElementById('sidebarOverlay');
const toggleBtn = document.getElementById('sidebarToggle');
const closeBtn  = document.getElementById('sidebarClose');

function openSidebar()  { sidebar?.classList.add('open');  overlay?.classList.add('show'); }
function closeSidebar() { sidebar?.classList.remove('open'); overlay?.classList.remove('show'); }

toggleBtn?.addEventListener('click', openSidebar);
closeBtn?.addEventListener('click', closeSidebar);
overlay?.addEventListener('click', closeSidebar);

// Auto-dismiss flash messages after 4s
document.querySelectorAll('.alert.fade.show').forEach(el => {
  setTimeout(() => bootstrap.Alert.getOrCreateInstance(el)?.close(), 4000);
});

// PWA install prompt
let deferredPrompt = null;
window.addEventListener('beforeinstallprompt', e => {
  e.preventDefault();
  deferredPrompt = e;
  showInstallBanner();
});

function showInstallBanner() {
  if (document.getElementById('installBanner')) return;
  const banner = document.createElement('div');
  banner.id = 'installBanner';
  banner.innerHTML = `
    <i class="bi bi-phone"></i>
    <span>Installer LabStock sur votre appareil</span>
    <button onclick="installPWA()">Installer</button>
    <button class="dismiss" onclick="dismissBanner()">✕</button>
  `;
  document.body.appendChild(banner);
}

async function installPWA() {
  if (!deferredPrompt) return;
  deferredPrompt.prompt();
  await deferredPrompt.userChoice;
  deferredPrompt = null;
  dismissBanner();
}

function dismissBanner() {
  document.getElementById('installBanner')?.remove();
}

// Register service worker
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/static/sw.js').catch(() => {});
  });
}

// Poll alert count every 60s and update badge
setInterval(async () => {
  try {
    const res = await fetch('/api/alerts/count');
    const data = await res.json();
    document.querySelectorAll('.alert-badge').forEach(el => {
      el.textContent = data.count;
      el.style.display = data.count > 0 ? 'inline' : 'none';
    });
  } catch (_) {}
}, 60000);
