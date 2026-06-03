/* ============================================================
   Тонкая обёртка над Fetch API: автоматически добавляет JWT,
   парсит JSON, нормализует ошибки.
   ============================================================ */

const API = (() => {
    const TOKEN_KEY = 'sportclub_token';
    const USER_KEY  = 'sportclub_user';

    const getToken = () => localStorage.getItem(TOKEN_KEY);
    const setToken = (t) => localStorage.setItem(TOKEN_KEY, t);

    const getUser = () => {
        try { return JSON.parse(localStorage.getItem(USER_KEY) || 'null'); }
        catch { return null; }
    };
    const setUser = (u) => localStorage.setItem(USER_KEY, JSON.stringify(u));

    const clear = () => {
        localStorage.removeItem(TOKEN_KEY);
        localStorage.removeItem(USER_KEY);
    };

    async function request(method, path, body) {
        const headers = { 'Content-Type': 'application/json' };
        const token = getToken();
        if (token) headers['Authorization'] = `Bearer ${token}`;

        const res = await fetch(path, {
            method,
            headers,
            body: body ? JSON.stringify(body) : undefined,
        });

        if (res.status === 204) return null;

        const data = await res.json().catch(() => ({}));
        if (!res.ok) {
            const message = data.detail || `Ошибка ${res.status}`;
            throw new Error(typeof message === 'string' ? message : JSON.stringify(message));
        }
        return data;
    }

    return {
        getToken, setToken, getUser, setUser, clear,
        get:    (p)    => request('GET',    p),
        post:   (p, b) => request('POST',   p, b),
        put:    (p, b) => request('PUT',    p, b),
        delete: (p)    => request('DELETE', p),
    };
})();
