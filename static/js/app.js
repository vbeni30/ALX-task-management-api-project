/* app.js — shared API client, auth helpers, and UI utilities */

/* ── AUTH ──────────────────────────────────────────────── */
const Auth = {
  getToken()    { return localStorage.getItem('tm_access'); },
  getRefresh()  { return localStorage.getItem('tm_refresh'); },
  getUsername() { return localStorage.getItem('tm_user') || 'User'; },

  set(access, refresh, username) {
    localStorage.setItem('tm_access', access);
    if (refresh)  localStorage.setItem('tm_refresh', refresh);
    if (username) localStorage.setItem('tm_user', username);
  },

  clear() {
    ['tm_access','tm_refresh','tm_user'].forEach(k => localStorage.removeItem(k));
  },

  ok() { return !!this.getToken(); },

  async tryRefresh() {
    const r = this.getRefresh();
    if (!r) return false;
    try {
      const res = await fetch('/api/token/refresh/', {
        method:'POST', headers:{'Content-Type':'application/json'},
        body: JSON.stringify({refresh: r}),
      });
      if (!res.ok) { this.clear(); return false; }
      const d = await res.json();
      this.set(d.access, d.refresh || r);
      return true;
    } catch { this.clear(); return false; }
  },

  logout() { this.clear(); window.location.href = '/'; },
};

/* ── API CLIENT ────────────────────────────────────────── */
const API = {
  async req(path, opts = {}) {
    const h = {'Content-Type':'application/json', ...opts.headers};
    if (Auth.ok()) h['Authorization'] = 'Bearer ' + Auth.getToken();

    let res = await fetch(path, {...opts, headers: h});

    if (res.status === 401 && Auth.getRefresh()) {
      if (await Auth.tryRefresh()) {
        h['Authorization'] = 'Bearer ' + Auth.getToken();
        res = await fetch(path, {...opts, headers: h});
      } else { window.location.href = '/'; return; }
    }

    if (res.status === 204) return null;
    const data = await res.json();
    if (!res.ok) throw {status: res.status, data};
    return data;
  },

  get(path, params = {}) {
    const qs = new URLSearchParams(
      Object.fromEntries(Object.entries(params).filter(([,v]) => v !== '' && v != null))
    ).toString();
    return this.req(path + (qs ? '?' + qs : ''), {method:'GET'});
  },
  post(path, body)   { return this.req(path, {method:'POST',  body: JSON.stringify(body)}); },
  patch(path, body)  { return this.req(path, {method:'PATCH', body: JSON.stringify(body)}); },
  put(path, body)    { return this.req(path, {method:'PUT',   body: JSON.stringify(body)}); },
  del(path)          { return this.req(path, {method:'DELETE'}); },
};

/* ── UI HELPERS ────────────────────────────────────────── */
const UI = {
  _wrap: null,
  _getWrap() {
    if (!this._wrap) {
      this._wrap = document.createElement('div');
      this._wrap.className = 'toast-wrap';
      document.body.appendChild(this._wrap);
    }
    return this._wrap;
  },

  toast(msg, type = 'info', ms = 3500) {
    const icons = {
      success: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>',
      error:   '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>',
      info:    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>',
    };
    const el = Object.assign(document.createElement('div'), {className: `toast ${type}`});
    el.innerHTML = `<span class="toast-icon">${icons[type]||icons.info}</span><span>${msg}</span>`;
    this._getWrap().appendChild(el);
    setTimeout(() => { el.style.opacity='0'; el.style.transform='translateX(16px)'; el.style.transition='.2s'; setTimeout(()=>el.remove(),200); }, ms);
  },

  open(id)  { document.getElementById(id)?.classList.add('open');    document.body.style.overflow='hidden'; },
  close(id) { document.getElementById(id)?.classList.remove('open'); document.body.style.overflow=''; },

  loading(btn, on) {
    if (on)  { btn._h = btn.innerHTML; btn.disabled=true;  btn.innerHTML='<span class="spinner"></span>'; }
    else     { btn.disabled=false; btn.innerHTML=btn._h||btn.innerHTML; }
  },
};

/* ── ERROR PARSER ──────────────────────────────────────── */
function apiErr(e) {
  if (!e.data) return 'Unexpected error.';
  const d = e.data;
  if (typeof d==='string') return d;
  if (d.detail) return d.detail;
  if (d.non_field_errors) return d.non_field_errors.join(' ');
  return Object.entries(d).map(([f,v]) => `${f}: ${[].concat(v).join(' ')}`).join('\n') || 'Validation error.';
}

/* ── GUARDS ────────────────────────────────────────────── */
function requireAuth() { if (!Auth.ok()) { window.location.href='/'; return false; } return true; }
function guestOnly()   { if (Auth.ok())  { window.location.href='/dashboard/'; return true; } return false; }

/* ── FORMAT HELPERS ────────────────────────────────────── */
function fmtDate(s) {
  if (!s) return '';
  const d = new Date(s + 'T00:00:00'), t = new Date(); t.setHours(0,0,0,0);
  const diff = Math.round((d-t)/86400000);
  if (diff===0) return 'Today'; if (diff===1) return 'Tomorrow'; if (diff===-1) return 'Yesterday';
  return d.toLocaleDateString('en-US',{month:'short',day:'numeric'});
}
function isOverdue(s) { if (!s) return false; const d=new Date(s+'T00:00:00'),t=new Date(); t.setHours(0,0,0,0); return d<t; }

/* ── SVG ICON STRINGS ──────────────────────────────────── */
const IC = {
  edit:   '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>',
  trash:  '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14H6L5 6"/><path d="M10 11v6"/><path d="M14 11v6"/><path d="M9 6V4h6v2"/></svg>',
  plus:   '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>',
  search: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>',
  logout: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>',
  check:  '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>',
  close:  '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>',
  task:   '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><polyline points="9 11 12 14 22 4"/></svg>',
  grid:   '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>',
  tag:    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"/><line x1="7" y1="7" x2="7.01" y2="7"/></svg>',
  logo:   '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>',
};

/* ── SIDEBAR INIT ──────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  // Populate user info in sidebar
  const nameEl   = document.getElementById('sb-username');
  const avatarEl = document.getElementById('sb-avatar');
  if (nameEl)   nameEl.textContent   = Auth.getUsername();
  if (avatarEl) avatarEl.textContent = Auth.getUsername().charAt(0).toUpperCase();

  // Close modals when clicking backdrop
  document.querySelectorAll('.modal-overlay').forEach(el => {
    el.addEventListener('click', e => { if (e.target===el) UI.close(el.id); });
  });

  // Logout buttons
  document.querySelectorAll('.js-logout').forEach(btn => {
    btn.addEventListener('click', () => Auth.logout());
  });
});
