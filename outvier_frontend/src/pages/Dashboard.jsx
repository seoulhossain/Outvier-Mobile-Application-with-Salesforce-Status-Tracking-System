import React, { useEffect, useState } from 'react';
import {
  HiOutlineArrowPath,
  HiOutlineArrowRightOnRectangle,
  HiOutlineBell,
  HiOutlineChevronRight,
  HiOutlineClipboardDocumentList,
  HiOutlineCog6Tooth,
  HiOutlineDocumentText,
  HiOutlineExclamationTriangle,
  HiOutlineUsers,
} from 'react-icons/hi2';
import { Link } from 'react-router-dom';
import { getApplications, getNotifications, getProfile, logout } from '../api';
import './Dashboard.css';

const STATUS_COLOR = {
  submitted: '#2196f3',
  under_review: '#ff9800',
  conditional_offer: '#9c27b0',
  document_missing: '#f44336',
  unconditional_offer: '#4caf50',
  enrolled: '#1a237e',
  rejected: '#757575',
};

const STATUS_LABEL = {
  submitted: 'Submitted',
  under_review: 'Under Review',
  conditional_offer: 'Conditional Offer',
  document_missing: 'Document Missing',
  unconditional_offer: 'Unconditional Offer',
  enrolled: 'Enrolled',
  rejected: 'Rejected',
};

function getRole() {
  try {
    const token = localStorage.getItem('access_token');
    if (!token) return null;
    const payload = JSON.parse(atob(token.split('.')[1]));
    return payload.role || null;
  } catch { return null; }
}

/* ─────────────────────────────────────────────────────── */
/*  ADMIN DASHBOARD                                        */
/* ─────────────────────────────────────────────────────── */
function AdminDashboard({ profile, applications, notifications }) {
  const unreadCount = notifications.filter(n => !n.is_read).length;

  // Group applications by status for quick stats
  const total = applications.length;
  const pending = applications.filter(a =>
    ['submitted', 'under_review', 'conditional_offer'].includes(a.status)
  ).length;
  const enrolled = applications.filter(a => a.status === 'enrolled').length;
  const needsDocs = applications.filter(a => a.status === 'document_missing').length;

  return (
    <div className="mobile-shell admin-shell">
      {/* ── Admin Header ── */}
      <div className="dash-header admin-header">
        <div>
          <div className="dash-title">Admin Dashboard</div>
          <div className="dash-subtitle admin-subtitle">Outvier Administration</div>
        </div>
        <div className="dash-header-right">
          <button className="dash-logout-btn admin-logout-btn" onClick={logout} title="Sign out">
            <HiOutlineArrowRightOnRectangle />
            <span>Sign out</span>
          </button>
        </div>
      </div>

      {/* ── Admin Role Banner ── */}
      <div className="admin-role-banner">
        <div className="admin-role-left">
          <div className="admin-role-badge">
            <HiOutlineCog6Tooth />
            <span>Administrator</span>
          </div>
          <div className="admin-welcome-name">
            Welcome, {profile?.first_name || profile?.username}
          </div>
        </div>
        <div className="admin-role-right">
          You have full access to all student records and system tools.
        </div>
      </div>

      {/* ── Admin Stats Row ── */}
      <div className="dash-summary-row" style={{ margin: '14px 16px 0' }}>
        <div className="dash-summary-card admin-stat">
          <span className="dash-summary-value admin-val">{total}</span>
          <span className="dash-summary-label">Total Applications</span>
        </div>
        <div className="dash-summary-card admin-stat">
          <span className="dash-summary-value admin-val">{pending}</span>
          <span className="dash-summary-label">In Progress</span>
        </div>
        <div className="dash-summary-card admin-stat">
          <span className="dash-summary-value admin-val">{enrolled}</span>
          <span className="dash-summary-label">Enrolled</span>
        </div>
        <div className="dash-summary-card admin-stat admin-stat--warn">
          <span className="dash-summary-value admin-val-warn">{needsDocs}</span>
          <span className="dash-summary-label">Docs Missing</span>
        </div>
      </div>

      {/* ── Admin Tools ── */}
      <div className="dash-section-label">Admin Tools</div>
      <div className="dash-list">
        <Link to="/admin/sync-logs" className="dash-list-item">
          <HiOutlineArrowPath className="dash-list-icon admin-icon" />
          <div className="dash-list-body">
            <span className="dash-list-title">Salesforce Sync Logs</span>
            <span className="dash-list-meta">View all background sync history and errors</span>
          </div>
          <HiOutlineChevronRight className="dash-list-arrow" />
        </Link>
        <a
          href="http://localhost:8000/admin"
          target="_blank"
          rel="noopener noreferrer"
          className="dash-list-item"
        >
          <HiOutlineCog6Tooth className="dash-list-icon admin-icon" />
          <div className="dash-list-body">
            <span className="dash-list-title">Django Admin Panel</span>
            <span className="dash-list-meta">Manage users, trigger status changes, edit records</span>
          </div>
          <HiOutlineChevronRight className="dash-list-arrow" />
        </a>
        <Link to="/notifications" className="dash-list-item">
          <HiOutlineBell className="dash-list-icon admin-icon" />
          <div className="dash-list-body">
            <span className="dash-list-title">Notifications</span>
            <span className="dash-list-meta">System alerts and application updates</span>
          </div>
          {unreadCount > 0 && <span className="dash-list-alert">{unreadCount}</span>}
          <HiOutlineChevronRight className="dash-list-arrow" />
        </Link>
      </div>

      {/* ── What admins can do — info box ── */}
      <div className="admin-info-box">
        <div className="admin-info-title">
          <HiOutlineCog6Tooth /> What you can do as Admin
        </div>
        <ul className="admin-info-list">
          <li>View and manage <strong>all student applications</strong></li>
          <li>Change application status via <strong>Django Admin → Applications</strong></li>
          <li>Add / edit documents, offer details, communication logs</li>
          <li>Create or edit student user accounts</li>
          <li>Monitor Salesforce sync runs and errors in Sync Logs</li>
          <li>Status changes automatically trigger notifications to students</li>
        </ul>
      </div>

      {/* ── All Applications ── */}
      <div className="dash-section-label">
        All Student Applications ({total})
      </div>
      <div className="dash-list">
        {applications.length === 0 ? (
          <div className="dash-list-item">
            <HiOutlineClipboardDocumentList className="dash-list-icon" />
            <span className="dash-list-text">No applications in the system.</span>
          </div>
        ) : (
          applications.map(app => {
            const missing = app.documents?.filter(d => d.verification_status === 'missing').length || 0;
            return (
              <Link to={`/applications/${app.id}`} key={app.id} className="dash-list-item">
                <HiOutlineDocumentText className="dash-list-icon admin-icon" />
                <div className="dash-list-body">
                  <span className="dash-list-title">{app.program}</span>
                  <span className="dash-list-meta admin-student-name">
                    <HiOutlineUsers style={{ display: 'inline', verticalAlign: 'middle', marginRight: 3 }} />
                    {app.student_name || app.student_username || `Student #${app.student}`}
                  </span>
                  <span className="dash-list-meta">{app.salesforce_id || `App #${app.id}`}</span>
                  <span
                    className="dash-list-status"
                    style={{ background: STATUS_COLOR[app.status] || '#888' }}
                  >
                    {STATUS_LABEL[app.status] || app.status}
                  </span>
                </div>
                {missing > 0 && <span className="dash-list-alert">{missing}</span>}
                <HiOutlineChevronRight className="dash-list-arrow" />
              </Link>
            );
          })
        )}
      </div>
    </div>
  );
}

/* ─────────────────────────────────────────────────────── */
/*  STUDENT DASHBOARD                                      */
/* ─────────────────────────────────────────────────────── */
function StudentDashboard({ profile, applications, notifications }) {
  const unreadCount = notifications.filter(n => !n.is_read).length;
  const missingDocsTotal = applications.reduce(
    (sum, app) => sum + (app.documents?.filter(d => d.verification_status === 'missing').length || 0), 0
  );

  return (
    <div className="mobile-shell">
      {/* ── Student Header ── */}
      <div className="dash-header">
        <div>
          <div className="dash-title">Dashboard</div>
          <div className="dash-subtitle">Outvier Student Portal</div>
        </div>
        <div className="dash-header-right">
          <button className="dash-logout-btn" onClick={logout} title="Sign out">
            <HiOutlineArrowRightOnRectangle />
            <span>Sign out</span>
          </button>
        </div>
      </div>

      {/* ── Welcome Banner ── */}
      <div className="dash-welcome">
        <div className="dash-welcome-top">
          <div>
            <p className="dash-welcome-label">Signed in as</p>
            <h1 className="dash-welcome-name">{profile?.first_name || profile?.username}</h1>
          </div>
          {missingDocsTotal > 0 && (
            <div className="dash-warning-pill">
              <HiOutlineExclamationTriangle />
              <span>{missingDocsTotal} missing doc{missingDocsTotal === 1 ? '' : 's'}</span>
            </div>
          )}
        </div>
        <p className="dash-welcome-text">
          Track your application status, documents, and notifications below.
        </p>
        <div className="dash-summary-row">
          <div className="dash-summary-card">
            <span className="dash-summary-value">{applications.length}</span>
            <span className="dash-summary-label">Applications</span>
          </div>
          <div className="dash-summary-card">
            <span className="dash-summary-value">{unreadCount}</span>
            <span className="dash-summary-label">Unread Notifications</span>
          </div>
        </div>
      </div>

      {/* ── What students can see — info box ── */}
      <div className="student-info-box">
        <div className="student-info-title">What you can view</div>
        <ul className="student-info-list">
          <li>Your application status and full timeline</li>
          <li>Document checklist — Verified / Pending / Missing</li>
          <li>Offer details — type, deadline, and remarks</li>
          <li>Communication history logged by admissions staff</li>
          <li>Notifications when your status or documents change</li>
        </ul>
      </div>

      {/* ── Applications ── */}
      <div className="dash-section-label">Your Applications</div>
      <div className="dash-list">
        {applications.length === 0 ? (
          <div className="dash-list-item">
            <HiOutlineClipboardDocumentList className="dash-list-icon" />
            <span className="dash-list-text">No applications yet.</span>
          </div>
        ) : (
          applications.map(app => {
            const missing = app.documents?.filter(d => d.verification_status === 'missing').length || 0;
            return (
              <Link to={`/applications/${app.id}`} key={app.id} className="dash-list-item">
                <HiOutlineDocumentText className="dash-list-icon" />
                <div className="dash-list-body">
                  <span className="dash-list-title">{app.program}</span>
                  <span className="dash-list-meta">{app.salesforce_id || `Application #${app.id}`}</span>
                  <span
                    className="dash-list-status"
                    style={{ background: STATUS_COLOR[app.status] || '#888' }}
                  >
                    {STATUS_LABEL[app.status] || app.status}
                  </span>
                </div>
                {missing > 0 && <span className="dash-list-alert">{missing}</span>}
                <HiOutlineChevronRight className="dash-list-arrow" />
              </Link>
            );
          })
        )}
      </div>

      {/* ── Shortcuts ── */}
      <div className="dash-section-label">Shortcuts</div>
      <div className="dash-list">
        <Link to="/notifications" className="dash-list-item">
          <HiOutlineBell className="dash-list-icon" />
          <div className="dash-list-body">
            <span className="dash-list-title">Notifications</span>
            <span className="dash-list-meta">Read your latest updates</span>
          </div>
          {unreadCount > 0 && <span className="dash-list-alert">{unreadCount}</span>}
          <HiOutlineChevronRight className="dash-list-arrow" />
        </Link>
      </div>
    </div>
  );
}

/* ─────────────────────────────────────────────────────── */
/*  ROOT — picks the right dashboard                       */
/* ─────────────────────────────────────────────────────── */
export default function Dashboard() {
  const [profile, setProfile] = useState(null);
  const [applications, setApplications] = useState([]);
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const isAdmin = getRole() === 'administrator';

  useEffect(() => {
    Promise.all([getProfile(), getApplications(), getNotifications()])
      .then(([p, apps, notifs]) => {
        setProfile(p);
        setApplications(apps);
        setNotifications(notifs);
      })
      .catch(() => setError('Unable to load dashboard data right now.'))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="page-loading">Loading…</div>;
  if (error)   return <div className="page-loading" style={{ color: '#b42318' }}>{error}</div>;

  if (isAdmin) {
    return <AdminDashboard profile={profile} applications={applications} notifications={notifications} />;
  }
  return <StudentDashboard profile={profile} applications={applications} notifications={notifications} />;
}

