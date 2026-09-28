import React from 'react';
import { Activity, AlertCircle, AlertTriangle, HelpCircle, ShieldAlert } from 'lucide-react';

export default function ReportSummary({ report }) {
  if (!report) return null;

  const concernsCount = report.clinical_concerns?.length || 0;
  const missingCount = report.missing_information?.length || 0;
  const inconsistencyCount = report.potential_inconsistencies?.length || 0;
  const reviewCount = report.requires_review?.length || 0;

  return (
    <div className="card summary-card">
      <div className="card-header" style={{ borderColor: 'rgba(14, 165, 233, 0.2)' }}>
        <div className="card-title" style={{ color: 'var(--primary-800)' }}>
          <Activity size={20} />
          <span>Executive Clinical Report Summary</span>
        </div>
        <div className="summary-badges-container">
          {reviewCount > 0 && (
            <span className="badge badge-processing">
              <AlertTriangle size={12} />
              <span>{reviewCount} Items for Review</span>
            </span>
          )}
          {inconsistencyCount > 0 && (
            <span className="badge badge-failed">
              <ShieldAlert size={12} />
              <span>{inconsistencyCount} Inconsistencies</span>
            </span>
          )}
          {missingCount > 0 && (
            <span className="badge badge-neutral">
              <HelpCircle size={12} />
              <span>{missingCount} Missing Items</span>
            </span>
          )}
        </div>
      </div>

      <p className="summary-text">
        {report.report_summary || 'No summary text generated.'}
      </p>

      {/* Quick summary grid */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
          gap: '1rem',
          marginTop: '1.25rem',
          paddingTop: '1rem',
          borderTop: '1px solid rgba(14, 165, 233, 0.15)',
        }}
      >
        <div>
          <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--neutral-500)', textTransform: 'uppercase' }}>
            Documented Diagnoses
          </span>
          <div style={{ fontSize: '0.9rem', fontWeight: 600, color: 'var(--neutral-800)', marginTop: '0.2rem' }}>
            {report.diagnoses?.length > 0
              ? report.diagnoses.map((d) => d.condition).join(', ')
              : 'None documented'}
          </div>
        </div>

        <div>
          <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--neutral-500)', textTransform: 'uppercase' }}>
            Active Medications
          </span>
          <div style={{ fontSize: '0.9rem', fontWeight: 600, color: 'var(--neutral-800)', marginTop: '0.2rem' }}>
            {report.medications?.length > 0
              ? report.medications.map((m) => m.medication).join(', ')
              : 'None documented'}
          </div>
        </div>

        <div>
          <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--neutral-500)', textTransform: 'uppercase' }}>
            Key Vitals Present
          </span>
          <div style={{ fontSize: '0.9rem', fontWeight: 600, color: 'var(--neutral-800)', marginTop: '0.2rem' }}>
            {report.vitals?.blood_pressure !== 'Not documented' && `BP: ${report.vitals?.blood_pressure} | `}
            {report.vitals?.temperature !== 'Not documented' && `T: ${report.vitals?.temperature} | `}
            {report.vitals?.heart_rate !== 'Not documented' && `HR: ${report.vitals?.heart_rate}`}
            {(!report.vitals || Object.values(report.vitals).every((v) => v === 'Not documented')) && 'None documented'}
          </div>
        </div>
      </div>
    </div>
  );
}
