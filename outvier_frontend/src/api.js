const BASE = '/api';

function getToken() {
  return localStorage.getItem('access_token');
}

async function request(path, options = {}) {
  const headers = { 'Content-Type': 'application/json', ...(options.headers || {}) };
  const token = getToken();
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const res = await fetch(`${BASE}${path}`, { ...options, headers });

  if (res.status === 401) {
    // Try refreshing
    const refresh = localStorage.getItem('refresh_token');
    if (refresh) {
      const r = await fetch(`${BASE}/auth/refresh/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh }),
      });
      if (r.ok) {
        const data = await r.json();
        localStorage.setItem('access_token', data.access);
        headers['Authorization'] = `Bearer ${data.access}`;
        return fetch(`${BASE}${path}`, { ...options, headers });
      }
    }
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    window.location.href = '/login';
    throw new Error('Unauthorized');
  }
  return res;
}

export async function login(username, password) {
  const res = await fetch(`${BASE}/auth/login/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  });
  if (!res.ok) throw new Error('Invalid credentials');
  const data = await res.json();
  localStorage.setItem('access_token', data.access);
  localStorage.setItem('refresh_token', data.refresh);
  return data;
}

export async function register(data) {
  const res = await fetch(`${BASE}/auth/register/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const err = await res.json();
    throw err;
  }
  return res.json();
}

export function logout() {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  window.location.href = '/login';
}

export async function getProfile() {
  const res = await request('/auth/profile/');
  if (!res.ok) throw new Error('Failed to load profile');
  return res.json();
}

export async function getApplications() {
  const res = await request('/applications/');
  if (!res.ok) throw new Error('Failed to load applications');
  return res.json();
}

export async function getApplication(id) {
  const res = await request(`/applications/${id}/`);
  if (!res.ok) throw new Error('Failed to load application');
  return res.json();
}

export async function getNotifications() {
  const res = await request('/notifications/');
  if (!res.ok) throw new Error('Failed to load notifications');
  return res.json();
}

export async function markNotificationRead(id) {
  const res = await request(`/notifications/${id}/read/`, { method: 'PATCH' });
  if (!res.ok) throw new Error('Failed to mark notification read');
  return res.json();
}
