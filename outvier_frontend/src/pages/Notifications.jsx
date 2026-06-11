import React, { useEffect, useState } from 'react';
import {
  HiOutlineBell,
  HiOutlineChatBubbleLeftRight,
  HiOutlineCheck,
  HiOutlineCheckCircle,
  HiOutlineChevronLeft,
  HiOutlineClock,
  HiOutlineExclamationTriangle,
} from 'react-icons/hi2';
import { useNavigate } from 'react-router-dom';
import { getNotifications, markNotificationRead } from '../api';
import './Notifications.css';

const NOTIF_ICON = {
  status_change: HiOutlineBell,
  doc_verified: HiOutlineCheckCircle,
  deadline: HiOutlineClock,
  doc_pending: HiOutlineExclamationTriangle,
  default: HiOutlineChatBubbleLeftRight,
};

function inferIconKey(message) {
  const m = message.toLowerCase();
  if (m.includes('status')) return 'status_change';
  if (m.includes('verified') || m.includes('approved')) return 'doc_verified';
  if (m.includes('deadline') || m.includes('approaching')) return 'deadline';
  if (m.includes('pending') || m.includes('missing')) return 'doc_pending';
  return 'default';
}

function inferTitle(message) {
  const m = message.toLowerCase();
  if (m.includes('status changed') || m.includes('status change')) return 'Application Status Changed';
  if (m.includes('verified')) return 'New Document Verified';
  if (m.includes('deadline')) return 'Deadline Approaching';
  if (m.includes('pending')) return 'Document Pending';
  if (m.includes('missing')) return 'Document Missing';
  // Use first sentence as title
  const dot = message.indexOf(':');
  return dot > 0 ? message.substring(0, dot) : message.substring(0, 40);
}

function inferBody(message) {
  const dot = message.indexOf(':');
  if (dot > 0 && dot < message.length - 1) return message.substring(dot + 1).trim();
  return message;
}

function NotificationIcon({ message }) {
  const Icon = NOTIF_ICON[inferIconKey(message)] || HiOutlineChatBubbleLeftRight;
  return <Icon />;
}

export default function Notifications() {
  const [notifs, setNotifs] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    getNotifications()
      .then(setNotifs)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  async function handleRead(id) {
    try {
      await markNotificationRead(id);
      setNotifs(prev => prev.map(n => (n.id === id ? { ...n, is_read: true } : n)));
    } catch { /* ignore */ }
  }

  if (loading) return <div className="page-loading">Loading…</div>;

  return (
    <div className="mobile-shell">
      {/* ── Header ── */}
      <div className="screen-header">
        <button className="back-icon" onClick={() => navigate('/dashboard')}><HiOutlineChevronLeft /></button>
        <span className="screen-title">NOTIFICATIONS</span>
        <span style={{ width: 32 }} />
      </div>

      <div className="screen-body">
        {notifs.length === 0 ? (
          <div className="notif-empty">
            <HiOutlineBell className="notif-empty-icon" />
            <p>No notifications yet. You'll see alerts here when your status changes.</p>
          </div>
        ) : (
          <div className="notif-list">
            {notifs.map(n => (
              <div key={n.id} className={`notif-row ${n.is_read ? 'notif-read' : 'notif-unread'}`}>
                <div className={`notif-dot ${n.is_read ? 'notif-dot-read' : ''}`}>
                  <NotificationIcon message={n.message} />
                </div>
                <div className="notif-content">
                  <span className="notif-title">{inferTitle(n.message)}</span>
                  <span className="notif-body">{inferBody(n.message)}</span>
                  <span className="notif-time">{new Date(n.sent_at).toLocaleString('en-AU')}</span>
                </div>
                {!n.is_read && (
                  <button className="notif-mark-btn" onClick={() => handleRead(n.id)}>
                    <HiOutlineCheck />
                  </button>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
