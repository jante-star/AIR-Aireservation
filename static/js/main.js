document.addEventListener('DOMContentLoaded', function () {
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }

    // Auto-dismiss flash messages after 4 seconds
    const flashes = document.querySelectorAll('[data-flash]');
    flashes.forEach(el => setTimeout(() => el.remove(), 4000));

    // Toggle AI config visibility on listing creation form
    const aiCheckbox = document.getElementById('ai_enabled');
    const aiConfig = document.getElementById('ai_config');
    if (aiCheckbox && aiConfig) {
        aiCheckbox.addEventListener('change', () => {
            aiConfig.classList.toggle('hidden');
        });
    }

    // ── Theme management ──────────────────────────────────────────────────────
    const html = document.documentElement;
    const mq = window.matchMedia('(prefers-color-scheme: dark)');

    function applyTheme(choice) {
        const dark = choice === 'dark' || (choice === 'system' && mq.matches);
        if (dark) {
            html.setAttribute('data-theme', 'dark');
        } else {
            html.removeAttribute('data-theme');
        }
        updateToggleIcon(dark);
    }

    function updateToggleIcon(isDark) {
        const btn = document.getElementById('theme-toggle-btn');
        if (!btn) return;
        const sunIcon = btn.querySelector('.dark-hide');
        const moonIcon = btn.querySelector('.light-hide');
        if (sunIcon) sunIcon.classList.toggle('hidden', isDark);
        if (moonIcon) moonIcon.classList.toggle('hidden', !isDark);
    }

    // Expose so the settings page can call it
    window.AirTheme = { apply: applyTheme };

    // Apply on load
    const saved = localStorage.getItem('air-theme') || 'system';
    applyTheme(saved);

    // Re-apply when system preference changes (for 'system' mode)
    mq.addEventListener('change', () => {
        const current = localStorage.getItem('air-theme') || 'system';
        if (current === 'system') applyTheme('system');
    });

    // Navbar quick-toggle cycles: light → dark → system → light
    const toggleBtn = document.getElementById('theme-toggle-btn');
    if (toggleBtn) {
        toggleBtn.addEventListener('click', () => {
            const current = localStorage.getItem('air-theme') || 'system';
            const next = current === 'light' ? 'dark' : current === 'dark' ? 'system' : 'light';
            localStorage.setItem('air-theme', next);
            applyTheme(next);
        });
    }
});
