
// copy-on-click and dynamic year for all pages
document.querySelectorAll('.copy').forEach(el => {
    el.addEventListener('click', () => {
        const text = el.getAttribute('data-copy') || el.textContent;
        navigator.clipboard.writeText(text.trim()).then(() => {
            el.style.outline = '2px solid var(--brand)'; setTimeout(() => el.style.outline = 'none', 600);
        });
    });
    el.title = 'Click to copy';
});
document.querySelectorAll('#year').forEach(el => el.textContent = new Date().getFullYear());


// --- GitHub repo counts ---
(function () {
    const repo = 'kieukhang185/opsbox';
    fetch(`https://api.github.com/repos/${repo}`)
        .then(r => r.json())
        .then(data => {
            const stars = (data.stargazers_count != null) ? data.stargazers_count : '—';
            const forks = (data.forks_count != null) ? data.forks_count : '—';
            document.querySelectorAll('[data-gh=stars]').forEach(el => el.textContent = stars);
            document.querySelectorAll('[data-gh=forks]').forEach(el => el.textContent = forks);
        })
        .catch(() => {
            document.querySelectorAll('[data-gh]').forEach(el => el.textContent = '—');
        });
})();

// --- Theme toggle ---
(function () {
    const KEY = "opsbox_theme";
    const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
    const saved = localStorage.getItem(KEY);
    const initial = saved || 'light';
    function applyTheme(t) {
        document.documentElement.setAttribute('data-theme', t);
        const btn = document.getElementById('themeToggle');
        if (btn) {
            if (t === 'dark') { btn.textContent = '☀️ Light'; }
            else { btn.textContent = '🌙 Dark'; }
        }
    }
    applyTheme(initial);
    window.addEventListener('DOMContentLoaded', () => {
        const btn = document.getElementById('themeToggle');
        if (btn) {
            btn.addEventListener('click', () => {
                const current = document.documentElement.getAttribute('data-theme') || 'light';
                const next = current === 'light' ? 'dark' : 'light';
                localStorage.setItem(KEY, next);
                applyTheme(next);
            });
            // ensure correct label in case DOM loaded before initial apply
            const current = document.documentElement.getAttribute('data-theme') || 'light';
            if (current === 'dark') { btn.textContent = '☀️ Light'; } else { btn.textContent = '🌙 Dark'; }
        }
    });
})();
