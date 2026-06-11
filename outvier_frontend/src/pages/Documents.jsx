import React, { useEffect, useState } from 'react';
import {
  HiOutlineBell,
  HiOutlineChevronLeft,
  HiOutlineClipboardDocumentList,
  HiOutlineDocumentText,
  HiOutlineFolderOpen,
  HiOutlineHome,
} from 'react-icons/hi2';
import { useParams, useNavigate } from 'react-router-dom';
import { getApplication } from '../api';
import './Documents.css';

const DOC_STATUS_COLOR = { verified: '#4caf50', pending: '#ff9800', missing: '#f44336' };
const DOC_STATUS_LABEL = { verified: 'Verified', pending: 'Pending', missing: 'Missing' };

export default function Documents() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [app, setApp] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getApplication(id)
      .then(setApp)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) return <div className="page-loading">Loading…</div>;
  if (!app) return null;

  const docs = app.documents || [];

  return (
    <div className="mobile-shell">
      {/* ── Header ── */}
      <div className="screen-header">
        <button className="back-icon" onClick={() => navigate(`/applications/${id}`)}><HiOutlineChevronLeft /></button>
        <span className="screen-title">DOCUMENTS</span>
        <span style={{ width: 32 }} />
      </div>

      <div className="screen-body">
        <div className="section-box">
          <h3 className="section-heading">Required Documents</h3>
          {docs.length === 0 ? (
            <p style={{ color: '#aaa', textAlign: 'center', padding: '20px 0' }}>
              No documents on record.
            </p>
          ) : (
            <div className="doc-list">
              {docs.map(doc => (
                <div key={doc.id} className="doc-row">
                  <HiOutlineDocumentText className="doc-file-icon" />
                  <span className="doc-name">{doc.doc_type}</span>
                  <span
                    className="doc-badge"
                    style={{ background: DOC_STATUS_COLOR[doc.verification_status] || '#888' }}
                  >
                    {DOC_STATUS_LABEL[doc.verification_status] || doc.verification_status_display}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* ── Bottom nav ── */}
      <div className="dash-bottom-nav">
        <button className="nav-item" onClick={() => navigate('/dashboard')}><HiOutlineHome /></button>
        <button className="nav-item" onClick={() => navigate(`/applications/${id}`)}><HiOutlineClipboardDocumentList /></button>
        <button className="nav-item active"><HiOutlineFolderOpen /></button>
        <button className="nav-item" onClick={() => navigate('/notifications')}><HiOutlineBell /></button>
      </div>
    </div>
  );
}
