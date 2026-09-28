import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Printer, FileText, Calendar, Clock, Loader2, ChevronDown, ChevronUp } from 'lucide-react';
import { useAnalysis } from '../hooks/useAnalysis';
import StatusBadge from '../components/StatusBadge';
import ClinicalReport from '../components/ClinicalReport';
import ErrorMessage from '../components/ErrorMessage';
import { formatDate, formatDuration } from '../utils/formatters';

export default function ReportDetails() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { currentReport, loading, error, setError, fetchReportById } = useAnalysis();
  const [showRawText, setShowRawText] = useState(false);

  useEffect(() => {
    if (id) {
      fetchReportById(id);
    }
  }, [id, fetchReportById]);

  const handlePrint = () => {
    window.print();
  };

  if (loading && !currentReport) {
    return (
      <div style={{ textAlign: 'center', padding: '4rem 1.5rem' }}>
        <Loader2 size={36} style={{ animation: 'spin 1s linear infinite', color: 'var(--primary-600)', margin: '0 auto' }} />
        <p style={{ color: 'var(--neutral-500)', marginTop: '0.85rem' }}>Loading clinical report...</p>
      </div>
    );
  }

  return (
    <div>
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '1.25rem',
          flexWrap: 'wrap',
          gap: '0.75rem',
        }}
      >
        <button
          type="button"
          onClick={() => navigate('/history')}
          className="btn btn-secondary"
          style={{ padding: '0.5rem 0.85rem', fontSize: '0.85rem' }}
        >
          <ArrowLeft size={16} />
          <span>Back to History</span>
        </button>

        <div className="btn-group">
          <button
            type="button"
            onClick={handlePrint}
            className="btn btn-secondary"
            style={{ padding: '0.5rem 0.85rem', fontSize: '0.85rem' }}
          >
            <Printer size={16} />
            <span>Print Report</span>
          </button>
        </div>
      </div>

      <ErrorMessage message={error} onDismiss={() => setError(null)} />

      {currentReport && (
        <>
          {/* Metadata Banner */}
          <div className="report-header-banner">
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
                <h2 style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--neutral-900)' }}>
                  Clinical Document Review
                </h2>
                <StatusBadge status={currentReport.status} />
              </div>
              <div style={{ fontSize: '0.85rem', color: 'var(--neutral-500)', display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
                <span><strong>Report ID:</strong> <span style={{ fontFamily: 'monospace' }}>{currentReport.id}</span></span>
                {currentReport.original_filename && (
                  <span><strong>Filename:</strong> {currentReport.original_filename}</span>
                )}
              </div>
            </div>

            <div className="report-meta-grid">
              <div className="report-meta-item">
                <span className="report-meta-label">Input Type</span>
                <span className="report-meta-value">{currentReport.input_type?.toUpperCase()}</span>
              </div>
              <div className="report-meta-item">
                <span className="report-meta-label">Processed Date/Time</span>
                <span className="report-meta-value" style={{ display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                  <Calendar size={13} color="var(--neutral-400)" />
                  {formatDate(currentReport.created_at)}
                </span>
              </div>
              <div className="report-meta-item">
                <span className="report-meta-label">Processing Time</span>
                <span className="report-meta-value" style={{ display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                  <Clock size={13} color="var(--neutral-400)" />
                  {formatDuration(currentReport.processing_time)}
                </span>
              </div>
            </div>
          </div>

          {/* If analysis status is FAILED, display prominent failure card */}
          {currentReport.status === 'FAILED' ? (
            <div className="card" style={{ borderColor: 'var(--danger-600)', background: 'var(--danger-50)' }}>
              <div style={{ display: 'flex', alignItems: 'flex-start', gap: '0.75rem' }}>
                <div style={{ color: 'var(--danger-600)', marginTop: '2px' }}>
                  <StatusBadge status="FAILED" />
                </div>
                <div>
                  <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--danger-700)', marginBottom: '0.4rem' }}>
                    Clinical Analysis Could Not Be Completed
                  </h3>
                  <p style={{ fontSize: '0.9rem', color: 'var(--neutral-700)', marginBottom: '0.75rem' }}>
                    <strong>Reason:</strong> {currentReport.error_message || 'An error occurred during extraction or review.'}
                  </p>
                  <p style={{ fontSize: '0.825rem', color: 'var(--neutral-500)' }}>
                    Please check the source document quality, ensure proper configuration, or submit another document.
                  </p>
                </div>
              </div>
            </div>
          ) : (
            /* Structured Clinical Report */
            <ClinicalReport analysis={currentReport} />
          )}

          {/* Raw Extracted Text Drawer (for clinician audit transparency) */}
          {currentReport.raw_text && (
            <div className="card" style={{ marginTop: '1.5rem', background: '#fafbfc' }}>
              <div
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  cursor: 'pointer',
                }}
                onClick={() => setShowRawText(!showRawText)}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontWeight: 600, fontSize: '0.95rem', color: 'var(--neutral-700)' }}>
                  <FileText size={18} />
                  <span>Source Extracted Document Text (Audit Log)</span>
                </div>
                <button
                  type="button"
                  style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--neutral-500)' }}
                >
                  {showRawText ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
                </button>
              </div>

              {showRawText && (
                <div style={{ marginTop: '1rem', paddingTop: '1rem', borderTop: '1px solid var(--neutral-200)' }}>
                  <pre
                    style={{
                      whiteSpace: 'pre-wrap',
                      wordBreak: 'break-word',
                      fontFamily: 'monospace',
                      fontSize: '0.825rem',
                      background: '#ffffff',
                      padding: '1rem',
                      borderRadius: 'var(--radius-sm)',
                      border: '1px solid var(--neutral-200)',
                      maxHeight: '300px',
                      overflowY: 'auto',
                    }}
                  >
                    {currentReport.raw_text}
                  </pre>
                </div>
              )}
            </div>
          )}
        </>
      )}
    </div>
  );
}
