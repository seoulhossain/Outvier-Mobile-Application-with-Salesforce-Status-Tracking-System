import React, { useEffect, useState } from 'react';
import {
  HiOutlineBell,
  HiOutlineChevronLeft,
  HiOutlineClipboardDocumentList,
  HiOutlineFolderOpen,
  HiOutlineHome,
} from 'react-icons/hi2';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { getApplication } from '../api';
import './StatusDetail.css';

const STATUS_ORDER = [
  'submitted',
  'under_review',
  'conditional_offer',
  'document_missing',
  'unconditional_offer',
  'enrolled',
];

const STATUS_LABEL = {
  submitted: 'Submitted',
  under_review: 'Under Review',
  conditional_offer: 'Conditional Offer',
  document_missing: 'Document Missing',
  unconditional_offer: 'Unconditional Offer',
  enrolled: 'Enrolled',
  rejected: 'Rejected',
};

function fmt(dt) {
  if (!dt) return '';
  return new Date(dt).toLocaleDateString('en-AU', { day: 'numeric', month: 'short', year: 'numeric' });
}

export default function StatusDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [app, setApp] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    getApplication(id)
      .then(setApp)
      .catch(() => setError('Failed to load application.'))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) return <div className="page-loading">Loading…</div>;
  if (error) return <div className="page-error">{error}</div>;
  if (!app) return null;

  const isRejected = app.status === 'rejected';
  const currentIdx = isRejected ? -1 : STATUS_ORDER.indexOf(app.status);

  // Map history by status for dates
  const historyByStatus = {};
  (app.status_history || []).forEach(h => { historyByStatus[h.status] = h; });

  const stepsToShow = isRejected ? ['submitted', 'under_review', 'rejected'] : STATUS_ORDER;

  return (
    <div className="mobile-shell">
      {/* ── Header ── */}
      <div className="screen-header">
        <button className="back-icon" onClick={() => navigate('/dashboard')}><HiOutlineChevronLeft /></button>
        <span className="screen-title">STATUS</span>
        <span style={{ width: 32 }} />
      </div>

      <div className="screen-body">
        {/* Program badge */}
        <div className="program-row">
          <span className="program-name">{app.program || 'Application'}</span>
          <span className="program-id">{app.salesforce_id || `#${app.id}`}</span>
        </div>

        {/* ── Progress timeline ── */}
        <div className="section-box">
          <h3 className="section-heading">Progress</h3>
          <div className="timeline-v">
            {stepsToShow.map((s, idx) => {
              const done = !isRejected && idx <= currentIdx;
              const active = !isRejected && idx === currentIdx;
              const hist = historyByStatus[s];
              return (
                <div key={s} className="tl-row">
                  <div className="tl-col-left">
                    <div className={`tl-dot ${done ? 'tl-dot-done' : ''} ${active ? 'tl-dot-active' : ''}`}>
                      {done ? '●' : '○'}
                    </div>
                    {idx < stepsToShow.length - 1 && (
                      <div className={`tl-line ${done && idx < currentIdx ? 'tl-line-done' : ''}`} />
                    )}
                  </div>
                  <div className="tl-col-right">
                    <span className={`tl-label ${active ? 'tl-label-active' : ''}`}>{STATUS_LABEL[s]}</span>
                    {hist && <span className="tl-date">{fmt(hist.changed_at)}</span>}
                    {active && app.offer_detail && (
                      <span className="tl-hint">Your offer has been issued, see details below.</span>
                    )}
                    {active && !app.offer_detail && hist?.notes && (
                      <span className="tl-hint">{hist.notes}</span>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* ── Offer Details ── */}
        {app.offer_detail && (
          <div className="section-box offer-box">
            <div className="offer-row"><span className="offer-key">Application ID</span><span className="offer-val">{app.salesforce_id}</span></div>
            <div className="offer-row"><span className="offer-key">Program</span><span className="offer-val">{app.program}</span></div>
            <div className="offer-row"><span className="offer-key">Deadline</span><span className="offer-val">{fmt(app.offer_detail.deadline)}</span></div>
            {app.offer_detail.remarks && (
              <div className="offer-row offer-row-block">
                <span className="offer-key">Requirements</span>
                <span className="offer-val">{app.offer_detail.remarks}</span>
              </div>
            )}
          </div>
        )}

        {/* ── Documents link ── */}
        {app.documents?.length > 0 && (
          <Link to={`/applications/${app.id}/documents`} className="btn-full">
            <HiOutlineFolderOpen />
            <span>View Document Status ({app.documents.length} documents)</span>
          </Link>
        )}
      </div>

      {/* ── Bottom nav ── */}
      <div className="dash-bottom-nav">
        <button className="nav-item" onClick={() => navigate('/dashboard')}><HiOutlineHome /></button>
        <button className="nav-item active"><HiOutlineClipboardDocumentList /></button>
        <button className="nav-item" onClick={() => navigate(`/applications/${id}/documents`)}><HiOutlineFolderOpen /></button>
        <button className="nav-item" onClick={() => navigate('/notifications')}><HiOutlineBell /></button>
      </div>
    </div>
  );
}
