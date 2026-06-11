import React, { useEffect, useState } from 'react';
import {
  HiOutlineAcademicCap,
  HiOutlineArrowPath,
  HiOutlineCheckCircle,
  HiOutlineXCircle,
} from 'react-icons/hi2';
import { Link } from 'react-router-dom';
import { logout } from '../api';
import './SyncLogs.css';

async function getSyncLogs() {
  const token = localStorage.getItem('access_token');
  const res = await fetch('/api/admin/sync-logs/', {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (res.status === 403) throw new Error('forbidden');
  if (!res.ok) throw new Error('Failed to load sync logs');
  return res.json();
}

const STATUS_COLOR = { success: '#4caf50', failed: '#f44336', in_progress: '#ff9800' };
const STATUS_ICON = { success: HiOutlineCheckCircle, failed: HiOutlineXCircle, in_progress: HiOutlineArrowPath };

export default function SyncLogs() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    getSyncLogs()
      .then(setLogs)
      .catch(e => setError(e.message === 'forbidden'
        ? 'Access denied. Administrator role required.'
        : 'Failed to load sync logs.'))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="page">
      <header className="app-header">
        <div className="header-left">
          <span className="header-logo"><HiOutlineAcademicCap /></span>
          <span className="header-title">Outvier — Admin</span>
        </div>
        <div className="header-right">
          <Link to="/dashboard" className="btn-logout" style={{ textDecoration: 'none' }}>Dashboard</Link>
          <button onClick={logout} className="btn-logout">Sign Out</button>
        </div>
      </header>

      <main className="main-content">
        <h2 className="page-title">Salesforce Sync Logs</h2>
        <p className="page-sub">Each row = one Celery sync cycle (FR-10, UC-04)</p>

        {loading && <div className="log-loading">Loading…</div>}
        {error && <div className="log-error">{error}</div>}

        {!loading && !error && logs.length === 0 && (
          <div className="empty-state">
            <span className="empty-state-icon"><HiOutlineArrowPath /></span>
            <p>No sync cycles recorded yet. Start the Celery worker to begin syncing.</p>
          </div>
        )}

        {!loading && !error && logs.length > 0 && (
          <div className="logs-table-wrapper">
            <table className="logs-table">
              <thead>
                <tr>
                  <th>Status</th>
                  <th>Sync Time</th>
                  <th>Records Updated</th>
                  <th>Error</th>
                </tr>
              </thead>
              <tbody>
                {logs.map(log => {
                  const Icon = STATUS_ICON[log.status] || HiOutlineArrowPath;
                  return (
                  <tr key={log.id}>
                    <td>
                      <span className="log-status" style={{ color: STATUS_COLOR[log.status] || '#888' }}>
                        <Icon className="log-status-icon" /> {log.status}
                      </span>
                    </td>
                    <td className="log-time">
                      {new Date(log.sync_time).toLocaleString()}
                    </td>
                    <td className="log-count">{log.records_updated}</td>
                    <td className="log-error-msg">{log.error_message || '—'}</td>
                  </tr>
                )})}
              </tbody>
            </table>
          </div>
        )}
      </main>
    </div>
  );
}
