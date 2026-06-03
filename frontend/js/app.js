/* ============================================================
   Главный модуль приложения. Управляет переключением видов,
   подгружает данные через API и рендерит интерфейс.
   ============================================================ */

const ROLE_LABELS = {
    admin: 'Администратор',
    manager: 'Менеджер',
    receptionist: 'Ресепшн',
};

const VIEW_TITLES = {
    schedule:      'Расписание',
    clients:       'Клиенты',
    subscriptions: 'Абонементы',
    attendance:    'Журнал посещений',
    trainers:      'Тренеры',
    tariffs:       'Тарифы',
};

const STATE = {
    weekStart: getMondayOf(new Date()),
    refs: { class_types: [], halls: [], trainers: [], tariffs: [], clients: [] },
};

/* ---------- Утилиты дат ---------- */

function getMondayOf(d) {
    const date = new Date(d);
    const day = date.getDay() || 7;
    if (day !== 1) date.setDate(date.getDate() - (day - 1));
    date.setHours(0, 0, 0, 0);
    return date;
}
function addDays(d, n) { const x = new Date(d); x.setDate(x.getDate() + n); return x; }
function fmtDateISO(d) { return d.toISOString().slice(0, 10); }
function fmtDateRU(d)  { return d.toLocaleDateString('ru-RU', { day: '2-digit', month: '2-digit' }); }
function fmtDateLong(d){ return d.toLocaleDateString('ru-RU', { day: '2-digit', month: 'long', year: 'numeric' }); }

/* ---------- Стартовая инициализация ---------- */

(async function init() {
    const user = API.getUser();
    if (!user || !API.getToken()) { window.location.href = '/'; return; }
    document.body.classList.add('role-' + user.role);

    document.getElementById('user-name').textContent  = user.full_name;
    document.getElementById('user-role').textContent  = ROLE_LABELS[user.role] || user.role;
    document.getElementById('user-initials').textContent =
        user.full_name.split(' ').slice(0, 2).map(p => p[0]).join('').toUpperCase();

    document.getElementById('logout-btn').addEventListener('click', () => {
        API.clear();
        window.location.href = '/';
    });

    document.querySelectorAll('.nav-item').forEach(btn => {
        btn.addEventListener('click', () => switchView(btn.dataset.view));
    });

    document.getElementById('action-btn').addEventListener('click', onActionClick);
    document.getElementById('modal-close').addEventListener('click', closeModal);
    document.getElementById('modal-overlay').addEventListener('click', (e) => {
        if (e.target.id === 'modal-overlay') closeModal();
    });

    document.getElementById('week-prev').addEventListener('click', () => shiftWeek(-7));
    document.getElementById('week-next').addEventListener('click', () => shiftWeek(+7));

    await preloadReferences();
    await switchView('schedule');
})();

async function preloadReferences() {
    try {
        const [classTypes, halls, trainers, tariffs, clients] = await Promise.all([
            API.get('/api/class_types'),
            API.get('/api/halls'),
            API.get('/api/trainers'),
            API.get('/api/subscription_types'),
            API.get('/api/clients'),
        ]);
        STATE.refs = { class_types: classTypes, halls, trainers, tariffs, clients };
    } catch (err) {
        toast('Не удалось загрузить справочники: ' + err.message, 'error');
    }
}

/* ---------- Навигация между видами ---------- */

async function switchView(view) {
    document.querySelectorAll('.nav-item').forEach(b => b.classList.toggle('is-active', b.dataset.view === view));
    document.querySelectorAll('.view').forEach(v => v.hidden = (v.id !== 'view-' + view));
    document.getElementById('view-title').textContent = VIEW_TITLES[view];

    const actionBtn = document.getElementById('action-btn');
    const role = API.getUser().role;
    const adminOrManager = role === 'admin' || role === 'manager';

    const actions = {
        schedule:      { show: adminOrManager, label: '+ Добавить занятие',  fn: openClassModal },
        clients:       { show: adminOrManager, label: '+ Новый клиент',      fn: openClientModal },
        subscriptions: { show: adminOrManager, label: '+ Продать абонемент', fn: openSellSubModal },
        attendance:    { show: true,           label: '+ Зафиксировать визит', fn: openAttendanceModal },
        trainers:      { show: role === 'admin', label: '+ Новый тренер',    fn: openTrainerModal },
        tariffs:       { show: role === 'admin', label: '+ Новый тариф',     fn: openTariffModal },
    };
    const cfg = actions[view];
    actionBtn.hidden = !cfg || !cfg.show;
    if (cfg) { actionBtn.textContent = cfg.label; actionBtn.dataset.action = view; }

    const loaders = {
        schedule:      renderSchedule,
        clients:       renderClients,
        subscriptions: renderSubscriptions,
        attendance:    renderAttendance,
        trainers:      renderTrainers,
        tariffs:       renderTariffs,
    };
    await loaders[view]();
}

function onActionClick() {
    const view = document.getElementById('action-btn').dataset.action;
    const handlers = {
        schedule: openClassModal,
        clients: openClientModal,
        subscriptions: openSellSubModal,
        attendance: openAttendanceModal,
        trainers: openTrainerModal,
        tariffs: openTariffModal,
    };
    if (handlers[view]) handlers[view]();
}

/* ---------- Расписание ---------- */

function shiftWeek(days) {
    STATE.weekStart = addDays(STATE.weekStart, days);
    renderSchedule();
}

async function renderSchedule() {
    const ws = STATE.weekStart;
    const we = addDays(ws, 6);
    document.getElementById('week-label').textContent =
        `${fmtDateLong(ws)} – ${fmtDateLong(we)}`;

    const classes = await API.get(`/api/classes?date_from=${fmtDateISO(ws)}&date_to=${fmtDateISO(we)}`);
    const grid = document.getElementById('schedule-grid');
    grid.innerHTML = '';

    const HOURS = ['08:00','09:00','10:00','11:00','12:00','13:00','14:00','15:00','16:00','17:00','18:00','19:00'];
    const DAYS = ['Пн','Вт','Ср','Чт','Пт','Сб','Вс'];

    // Заголовок
    grid.appendChild(headerCell(''));
    for (let i = 0; i < 7; i++) {
        const d = addDays(ws, i);
        grid.appendChild(headerCell(`${DAYS[i]} ${fmtDateRU(d)}`));
    }

    // Строки часов
    HOURS.forEach(hour => {
        const timeCell = document.createElement('div');
        timeCell.className = 'schedule__cell schedule__time';
        timeCell.textContent = hour;
        grid.appendChild(timeCell);

        for (let i = 0; i < 7; i++) {
            const cell = document.createElement('div');
            cell.className = 'schedule__cell';
            const dayISO = fmtDateISO(addDays(ws, i));
            const lesson = classes.find(c => c.scheduled_date === dayISO && c.start_time === hour);
            if (lesson) cell.appendChild(lessonCard(lesson));
            grid.appendChild(cell);
        }
    });
}

function headerCell(text) {
    const el = document.createElement('div');
    el.className = 'schedule__cell schedule__head';
    el.textContent = text;
    return el;
}

function lessonCard(lesson) {
    const card = document.createElement('div');
    card.className = 'lesson-card';
    card.style.background = lesson.class_type_color;
    card.innerHTML = `
        <div class="lesson-card__title">${lesson.class_type_name}</div>
        <div class="lesson-card__meta">
            ${lesson.trainer_full_name.split(' ').slice(0, 2).join(' ')}<br>
            ${lesson.hall_name} · ${lesson.attendees_count}/${lesson.max_participants}
        </div>`;
    card.addEventListener('click', () => openClassDetail(lesson));
    return card;
}

async function openClassDetail(lesson) {
    const attendees = await API.get(`/api/attendance?class_id=${lesson.id}`);
    const role = API.getUser().role;
    const adminOrManager = role === 'admin' || role === 'manager';

    const list = attendees.map(a => `
        <tr>
            <td>${a.client_full_name}</td>
            <td>${new Date(a.check_in_time).toLocaleString('ru-RU')}</td>
        </tr>
    `).join('') || '<tr><td colspan="2" style="text-align:center;color:#888">Посещений ещё нет</td></tr>';

    openModal(
        `${lesson.class_type_name} · ${lesson.scheduled_date} ${lesson.start_time}`,
        `
        <div class="form" style="gap:18px">
            <div><strong>Тренер:</strong> ${lesson.trainer_full_name}</div>
            <div><strong>Зал:</strong> ${lesson.hall_name}</div>
            <div><strong>Запись:</strong> ${lesson.attendees_count}/${lesson.max_participants}</div>
            <table class="data-table" style="margin-top:6px"><thead><tr><th>Клиент</th><th>Время отметки</th></tr></thead>
                <tbody>${list}</tbody>
            </table>
            ${adminOrManager ? `<button class="btn btn--danger" id="cancel-class-btn">Отменить занятие</button>` : ''}
        </div>`,
    );
    const cancelBtn = document.getElementById('cancel-class-btn');
    if (cancelBtn) cancelBtn.addEventListener('click', async () => {
        if (!confirm('Отменить занятие?')) return;
        try {
            await API.delete('/api/classes/' + lesson.id);
            toast('Занятие отменено', 'success');
            closeModal();
            renderSchedule();
        } catch (e) { toast(e.message, 'error'); }
    });
}

/* ---------- Клиенты ---------- */

async function renderClients() {
    const clients = await API.get('/api/clients');
    STATE.refs.clients = clients;
    const tbody = document.getElementById('clients-tbody');
    tbody.innerHTML = clients.map(c => `
        <tr>
            <td>${c.full_name}</td>
            <td>${c.birth_date || '—'}</td>
            <td>${c.phone || '—'}</td>
            <td>${c.email || '—'}</td>
            <td>${c.registration_date}</td>
            <td style="text-align:right">
                <button class="btn btn--ghost btn--small" data-act="sub" data-id="${c.id}">Абонементы</button>
            </td>
        </tr>
    `).join('');
    tbody.querySelectorAll('[data-act="sub"]').forEach(b => {
        b.addEventListener('click', () => { STATE.filterClientId = +b.dataset.id; switchView('subscriptions'); });
    });
}

/* ---------- Абонементы ---------- */

async function renderSubscriptions() {
    let url = '/api/subscriptions';
    if (STATE.filterClientId) url += '?client_id=' + STATE.filterClientId;
    STATE.filterClientId = null;
    const subs = await API.get(url);
    const role = API.getUser().role;
    const adminOrManager = role === 'admin' || role === 'manager';

    document.getElementById('subs-tbody').innerHTML = subs.map(s => `
        <tr>
            <td>${s.client_full_name}</td>
            <td>${s.subscription_name}</td>
            <td>${s.purchase_date}</td>
            <td>${s.end_date}</td>
            <td>${s.lessons_left === null ? '∞' : s.lessons_left}</td>
            <td><span class="badge badge--${s.status}">${s.status}</span></td>
            <td style="text-align:right">
                ${adminOrManager && s.status === 'active'
                    ? `<button class="btn btn--ghost btn--small" data-act="freeze" data-id="${s.id}">Заморозить</button>`
                    : ''}
                ${adminOrManager && s.status === 'frozen'
                    ? `<button class="btn btn--ghost btn--small" data-act="resume" data-id="${s.id}">Возобновить</button>`
                    : ''}
            </td>
        </tr>
    `).join('');

    document.querySelectorAll('[data-act="freeze"]').forEach(b => b.addEventListener('click', async () => {
        try { await API.post(`/api/subscriptions/${b.dataset.id}/freeze`); toast('Заморожен', 'success'); renderSubscriptions(); }
        catch (e) { toast(e.message, 'error'); }
    }));
    document.querySelectorAll('[data-act="resume"]').forEach(b => b.addEventListener('click', async () => {
        try { await API.post(`/api/subscriptions/${b.dataset.id}/resume`); toast('Возобновлён', 'success'); renderSubscriptions(); }
        catch (e) { toast(e.message, 'error'); }
    }));
}

/* ---------- Журнал посещений ---------- */

async function renderAttendance() {
    const items = await API.get('/api/attendance');
    const role = API.getUser().role;

    document.getElementById('att-tbody').innerHTML = items.map(a => `
        <tr>
            <td>${a.scheduled_date}</td>
            <td>${a.start_time}</td>
            <td>${a.class_type_name}</td>
            <td>${a.client_full_name}</td>
            <td>${a.recorded_by}</td>
            <td style="text-align:right">
                <button class="btn btn--ghost btn--small" data-act="revoke" data-id="${a.id}">Отменить</button>
            </td>
        </tr>
    `).join('') || '<tr><td colspan="6" style="text-align:center;color:#888">Записей нет</td></tr>';

    document.querySelectorAll('[data-act="revoke"]').forEach(b => b.addEventListener('click', async () => {
        if (!confirm('Отменить отметку посещения?')) return;
        try { await API.delete('/api/attendance/' + b.dataset.id); toast('Отметка снята', 'success'); renderAttendance(); }
        catch (e) { toast(e.message, 'error'); }
    }));
}

/* ---------- Тренеры ---------- */

async function renderTrainers() {
    const trainers = await API.get('/api/trainers');
    document.getElementById('trainers-tbody').innerHTML = trainers.map(t => `
        <tr>
            <td>${t.full_name}</td>
            <td>${t.specialization || '—'}</td>
            <td>${t.phone || '—'}</td>
            <td>${t.hire_date}</td>
        </tr>
    `).join('');
}

/* ---------- Тарифы ---------- */

async function renderTariffs() {
    const tariffs = await API.get('/api/subscription_types');
    document.getElementById('tariffs-tbody').innerHTML = tariffs.map(t => `
        <tr>
            <td>${t.name}</td>
            <td>${t.duration_days}</td>
            <td>${t.lessons_count === null ? 'без лимита' : t.lessons_count}</td>
            <td>${(+t.price).toLocaleString('ru-RU')}</td>
        </tr>
    `).join('');
}

/* ---------- Модальные формы создания ---------- */

function openClientModal() {
    openModal('Новый клиент', `
        <form id="client-form" class="form">
            <label class="field"><span>ФИО *</span><input name="full_name" required></label>
            <label class="field"><span>Дата рождения</span><input name="birth_date" type="date"></label>
            <label class="field"><span>Пол</span>
                <select name="gender">
                    <option value="">—</option>
                    <option value="М">Мужской</option>
                    <option value="Ж">Женский</option>
                </select>
            </label>
            <label class="field"><span>Телефон</span><input name="phone" placeholder="+996..."></label>
            <label class="field"><span>Email</span><input name="email" type="email"></label>
            <button type="submit" class="btn btn--primary btn--block">Добавить</button>
        </form>`);
    document.getElementById('client-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const fd = Object.fromEntries(new FormData(e.target));
        Object.keys(fd).forEach(k => { if (fd[k] === '') fd[k] = null; });
        try { await API.post('/api/clients', fd); toast('Клиент добавлен', 'success'); closeModal(); renderClients(); preloadReferences(); }
        catch (err) { toast(err.message, 'error'); }
    });
}

function openTrainerModal() {
    openModal('Новый тренер', `
        <form id="trainer-form" class="form">
            <label class="field"><span>ФИО *</span><input name="full_name" required></label>
            <label class="field"><span>Специализация</span><input name="specialization"></label>
            <label class="field"><span>Телефон</span><input name="phone"></label>
            <label class="field"><span>Email</span><input name="email" type="email"></label>
            <label class="field"><span>Дата приёма *</span><input name="hire_date" type="date" required></label>
            <button type="submit" class="btn btn--primary btn--block">Добавить</button>
        </form>`);
    document.getElementById('trainer-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const fd = Object.fromEntries(new FormData(e.target));
        Object.keys(fd).forEach(k => { if (fd[k] === '') fd[k] = null; });
        try { await API.post('/api/trainers', fd); toast('Тренер добавлен', 'success'); closeModal(); renderTrainers(); preloadReferences(); }
        catch (err) { toast(err.message, 'error'); }
    });
}

function openTariffModal() {
    openModal('Новый тариф', `
        <form id="tariff-form" class="form">
            <label class="field"><span>Название *</span><input name="name" required></label>
            <label class="field"><span>Описание</span><textarea name="description" rows="2"></textarea></label>
            <label class="field"><span>Срок (дней) *</span><input name="duration_days" type="number" min="1" required></label>
            <label class="field"><span>Количество занятий (пусто = безлимит)</span><input name="lessons_count" type="number" min="1"></label>
            <label class="field"><span>Цена (сом) *</span><input name="price" type="number" min="0" step="50" required></label>
            <button type="submit" class="btn btn--primary btn--block">Сохранить</button>
        </form>`);
    document.getElementById('tariff-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const fd = Object.fromEntries(new FormData(e.target));
        Object.keys(fd).forEach(k => { if (fd[k] === '') fd[k] = null; });
        fd.duration_days = +fd.duration_days;
        if (fd.lessons_count) fd.lessons_count = +fd.lessons_count;
        fd.price = +fd.price;
        try { await API.post('/api/subscription_types', fd); toast('Тариф создан', 'success'); closeModal(); renderTariffs(); preloadReferences(); }
        catch (err) { toast(err.message, 'error'); }
    });
}

function openSellSubModal() {
    const clients  = STATE.refs.clients.map(c => `<option value="${c.id}">${c.full_name}</option>`).join('');
    const tariffs  = STATE.refs.tariffs.map(t => `<option value="${t.id}">${t.name} — ${t.price} сом</option>`).join('');
    openModal('Продажа абонемента', `
        <form id="sell-form" class="form">
            <label class="field"><span>Клиент *</span><select name="client_id" required>${clients}</select></label>
            <label class="field"><span>Тариф *</span><select name="subscription_type_id" required>${tariffs}</select></label>
            <label class="field"><span>Дата начала *</span><input name="start_date" type="date" required value="${fmtDateISO(new Date())}"></label>
            <button type="submit" class="btn btn--primary btn--block">Оформить</button>
        </form>`);
    document.getElementById('sell-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const fd = Object.fromEntries(new FormData(e.target));
        fd.client_id = +fd.client_id;
        fd.subscription_type_id = +fd.subscription_type_id;
        try { await API.post('/api/subscriptions', fd); toast('Абонемент оформлен', 'success'); closeModal(); renderSubscriptions(); }
        catch (err) { toast(err.message, 'error'); }
    });
}

function openClassModal() {
    const ct = STATE.refs.class_types.map(c => `<option value="${c.id}">${c.name}</option>`).join('');
    const tr = STATE.refs.trainers.map(t => `<option value="${t.id}">${t.full_name}</option>`).join('');
    const hl = STATE.refs.halls.map(h => `<option value="${h.id}">${h.name} (${h.capacity})</option>`).join('');
    openModal('Новое занятие', `
        <form id="class-form" class="form">
            <label class="field"><span>Тип занятия *</span><select name="class_type_id" required>${ct}</select></label>
            <label class="field"><span>Тренер *</span><select name="trainer_id" required>${tr}</select></label>
            <label class="field"><span>Зал *</span><select name="hall_id" required>${hl}</select></label>
            <label class="field"><span>Дата *</span><input name="scheduled_date" type="date" required></label>
            <label class="field"><span>Начало *</span><input name="start_time" type="time" required></label>
            <label class="field"><span>Окончание *</span><input name="end_time" type="time" required></label>
            <label class="field"><span>Макс. участников *</span><input name="max_participants" type="number" min="1" value="20" required></label>
            <button type="submit" class="btn btn--primary btn--block">Создать</button>
        </form>`);
    document.getElementById('class-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const fd = Object.fromEntries(new FormData(e.target));
        ['class_type_id','trainer_id','hall_id','max_participants'].forEach(k => fd[k] = +fd[k]);
        try { await API.post('/api/classes', fd); toast('Занятие создано', 'success'); closeModal(); renderSchedule(); }
        catch (err) { toast(err.message, 'error'); }
    });
}

async function openAttendanceModal() {
    const today = fmtDateISO(new Date());
    const classes = await API.get(`/api/classes?date_from=${today}&date_to=${fmtDateISO(addDays(new Date(), 7))}`);
    const classOpts = classes.map(c =>
        `<option value="${c.id}">${c.scheduled_date} ${c.start_time} · ${c.class_type_name} (${c.trainer_full_name})</option>`
    ).join('');
    const clientOpts = STATE.refs.clients.map(c => `<option value="${c.id}">${c.full_name}</option>`).join('');

    openModal('Фиксация посещения', `
        <form id="att-form" class="form">
            <label class="field"><span>Клиент *</span><select name="client_id" required>${clientOpts}</select></label>
            <label class="field"><span>Занятие *</span><select name="class_id" required>${classOpts}</select></label>
            <button type="submit" class="btn btn--primary btn--block">Отметить визит</button>
            <p style="font-size:12px;color:#888;margin:6px 0 0">
                Подходящий действующий абонемент будет подобран автоматически.
                Остаток занятий уменьшится на 1.
            </p>
        </form>`);
    document.getElementById('att-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const fd = Object.fromEntries(new FormData(e.target));
        fd.client_id = +fd.client_id; fd.class_id = +fd.class_id;
        try { await API.post('/api/attendance', fd); toast('Посещение зафиксировано', 'success'); closeModal(); renderAttendance(); }
        catch (err) { toast(err.message, 'error'); }
    });
}

/* ---------- Модальное окно / уведомления ---------- */

function openModal(title, html) {
    document.getElementById('modal-title').textContent = title;
    document.getElementById('modal-body').innerHTML = html;
    document.getElementById('modal-overlay').hidden = false;
}
function closeModal() { document.getElementById('modal-overlay').hidden = true; }

function toast(message, kind = '') {
    const el = document.createElement('div');
    el.className = 'toast' + (kind ? ' toast--' + kind : '');
    el.textContent = message;
    document.getElementById('toast-stack').appendChild(el);
    setTimeout(() => el.remove(), 4500);
}
