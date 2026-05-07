document.addEventListener('DOMContentLoaded', function () {
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }

    // Auto-dismiss flash messages after 4 seconds
    const flashes = document.querySelectorAll('[data-flash]');
    flashes.forEach(el => setTimeout(() => el.remove(), 4000));

    // Toggle AI config visibility
    const aiCheckbox = document.getElementById('ai_enabled');
    const aiConfig = document.getElementById('ai_config');
    if (aiCheckbox && aiConfig) {
        aiCheckbox.addEventListener('change', () => {
            aiConfig.classList.toggle('hidden');
        });
    }
});
