document.getElementById('login-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const fd = new FormData(e.target);
    const errEl = document.getElementById('login-error');
    errEl.hidden = true;

    try {
        const res = await fetch('/api/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                login: fd.get('login'),
                password: fd.get('password'),
            }),
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || 'Не удалось войти');

        localStorage.setItem('sportclub_token', data.access_token);
        localStorage.setItem('sportclub_user', JSON.stringify({
            id: data.user_id,
            full_name: data.full_name,
            role: data.role,
        }));
        window.location.href = '/dashboard';
    } catch (err) {
        errEl.textContent = err.message;
        errEl.hidden = false;
    }
});
