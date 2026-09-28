import React from 'react';
import { useNavigate } from 'react-router-dom';
import { FileText, Calendar, Clock, Trash2, ArrowRight, File } from 'lucide-react';
import StatusBadge from './StatusBadge';
import { formatDate, formatDuration } from '../utils/formatters';

export default function ReportCard({ item, onDelete }) {
  const navigate = useNavigate();

  const handleCardClick = () => {
    navigate(`/reports/${item.id}`);
  };

  const handleDelete = (e) => {
    e.stopPropagation();
    if (window.confirm('Are you sure you want to delete this clinical report?')) {
      onDelete(item.id);
    }
  };

  return (
    <div
      className="card"
      onClick={handleCardClick}
      style={{
        cursor: 'pointer',
        transition: 'transform 0.15s ease, box-shadow 0.15s ease',
        marginBottom: '1rem',
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.transform = 'translateY(-2px)';
        e.currentTarget.style.boxShadow = 'var(--shadow-md)';
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.transform = 'none';
        e.currentTarget.style.boxShadow = 'var(--shadow-sm)';
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.75rem' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.35rem' }}>
            <span style={{ fontSize: '0.8rem', fontFamily: 'monospace', color: 'var(--neutral-500)', background: 'var(--neutral-100)', padding: '0.15rem 0.45rem', borderRadius: 'var(--radius-sm)' }}>
              ID: {item.id.slice(0, 8)}...
            </span>
            <span className="badge badge-neutral" style={{ fontSize: '0.7rem' }}>
              {item.input_type?.toUpperCase()}
            </span>
            {item.original_filename && (
              <span style={{ fontSize: '0.8rem', color: 'var(--neutral-600)', display: 'inline-flex', alignItems: 'center', gap: '0.25rem' }}>
                <File size={13} />
                {item.original_filename}
              </span>
            )}
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', fontSize: '0.775rem', color: 'var(--neutral-400)' }}>
            <span style={{ display: 'inline-flex', alignItems: 'center', gap: '0.3rem' }}>
              <Calendar size={13} />
              {formatDate(item.created_at)}
            </span>
            {item.processing_time != null && (
              <span style={{ display: 'inline-flex', alignItems: 'center', gap: '0.3rem' }}>
                <Clock size={13} />
                {formatDuration(item.processing_time)}
              </span>
            )}
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <StatusBadge status={item.status} />
          <button
            type="button"
            className="btn btn-outline-danger"
            onClick={handleDelete}
            style={{ padding: '0.3rem 0.5rem', fontSize: '0.75rem' }}
            title="Delete report"
          >
            <Trash2 size={13} />
          </button>
        </div>
      </div>

      <p style={{ fontSize: '0.875rem', color: 'var(--neutral-700)', lineHeight: '1.5', marginBottom: '0.75rem' }}>
        {item.report_summary
          ? (item.report_summary.length > 200 ? `${item.report_summary.slice(0, 200)}...` : item.report_summary)
          : 'Report processing pending or no summary recorded.'}
      </p>

      <div style={{ display: 'flex', justifyContent: 'flex-end', alignItems: 'center', fontSize: '0.825rem', fontWeight: 600, color: 'var(--primary-600)' }}>
        <span>View Full Clinical Report</span>
        <ArrowRight size={14} style={{ marginLeft: '0.3rem' }} />
      </div>
    </div>
  );
}
