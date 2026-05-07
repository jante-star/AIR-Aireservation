document.addEventListener('DOMContentLoaded', function () {
    const btn = document.getElementById('ai-call-btn');
    if (!btn) return;

    btn.addEventListener('click', async function () {
        const listingId = this.dataset.listingId;
        const agentId = this.dataset.agentId;
        const statusEl = document.getElementById('call-status');

        if (statusEl) statusEl.textContent = 'Connecting...';
        btn.disabled = true;

        try {
            const res = await fetch('/bookings/api/ai/start-call', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ listing_id: listingId, agent_id: agentId })
            });
            const data = await res.json();

            if (data.access_token && window.RetellWebClient) {
                const client = new window.RetellWebClient();
                client.startCall({ accessToken: data.access_token });
                if (statusEl) statusEl.textContent = 'Connected — speak now';
                client.on('call_ended', () => {
                    if (statusEl) statusEl.textContent = 'Call ended';
                    btn.disabled = false;
                });
            } else {
                if (statusEl) statusEl.textContent = 'AI voice not available right now';
                btn.disabled = false;
            }
        } catch (err) {
            console.error('AI call error:', err);
            if (statusEl) statusEl.textContent = 'Could not connect';
            btn.disabled = false;
        }
    });
});
