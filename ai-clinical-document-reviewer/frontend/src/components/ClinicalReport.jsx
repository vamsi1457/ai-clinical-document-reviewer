import React from 'react';
import {
  User,
  HeartPulse,
  Pill,
  Thermometer,
  ShieldCheck,
  AlertTriangle,
  HelpCircle,
  AlertOctagon,
  Eye,
  FileCheck2,
} from 'lucide-react';
import ReportSummary from './ReportSummary';

export default function ClinicalReport({ analysis }) {
  if (!analysis) return null;

  const report = analysis.structured_report || {};
  const patient = report.patient_information || {};
  const vitals = report.vitals || {};
  const symptoms = report.symptoms || [];
  const diagnoses = report.diagnoses || [];
  const medications = report.medications || [];
  const allergies = report.allergies || [];
  const observations = report.clinical_observations || [];
  const concerns = report.clinical_concerns || [];
  const missingInfo = report.missing_information || [];
  const inconsistencies = report.potential_inconsistencies || [];
  const requiresReview = report.requires_review || [];

  return (
    <div className="clinical-report-container">
      {/* 1. REPORT SUMMARY (FIRST AND MOST PROMINENT) */}
      <ReportSummary report={report} />

      {/* REQUIRES REVIEW (VISUALLY PROMINENT IF PRESENT) */}
      {requiresReview.length > 0 && (
        <div className="alert-box alert-review" style={{ marginBottom: '1.5rem', borderLeftWidth: '6px' }}>
          <AlertTriangle size={24} style={{ flexShrink: 0, marginTop: '2px', color: 'var(--warning-700)' }} />
          <div>
            <h4 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: '0.4rem', color: 'var(--warning-700)' }}>
              ITEMS REQUIRING CLINICAL HUMAN REVIEW
            </h4>
            <p style={{ fontSize: '0.85rem', marginBottom: '0.5rem', color: 'var(--warning-800)' }}>
              The following ambiguities, low-confidence extractions, or clinical nuances require manual clinician verification:
            </p>
            <ul style={{ paddingLeft: '1.25rem', fontSize: '0.875rem', lineHeight: '1.6' }}>
              {requiresReview.map((item, idx) => (
                <li key={idx}><strong>{item}</strong></li>
              ))}
            </ul>
          </div>
        </div>
      )}

      {/* POTENTIAL INCONSISTENCIES (CRITICAL) */}
      {inconsistencies.length > 0 && (
        <div className="alert-box alert-inconsistency" style={{ marginBottom: '1.5rem', borderLeftWidth: '6px' }}>
          <AlertOctagon size={24} style={{ flexShrink: 0, marginTop: '2px', color: 'var(--danger-700)' }} />
          <div>
            <h4 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: '0.4rem', color: 'var(--danger-700)' }}>
              POTENTIAL CLINICAL INCONSISTENCIES DETECTED
            </h4>
            <p style={{ fontSize: '0.85rem', marginBottom: '0.5rem', color: 'var(--danger-800)' }}>
              Contradictory or mismatched values detected across separate document sections:
            </p>
            <ul style={{ paddingLeft: '1.25rem', fontSize: '0.875rem', lineHeight: '1.6' }}>
              {inconsistencies.map((item, idx) => (
                <li key={idx}><strong>{item}</strong></li>
              ))}
            </ul>
          </div>
        </div>
      )}

      {/* 2. PATIENT INFORMATION */}
      <div className="card">
        <div className="card-header">
          <div className="card-title">
            <User size={18} />
            <span>Patient Information</span>
          </div>
          <span style={{ fontSize: '0.75rem', color: 'var(--neutral-400)' }}>Grounded strictly from document</span>
        </div>
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
            gap: '1rem',
          }}
        >
          <div>
            <div className="report-meta-label">Full Name</div>
            <div className="report-meta-value">{patient.name || 'Not provided'}</div>
          </div>
          <div>
            <div className="report-meta-label">Age</div>
            <div className="report-meta-value">{patient.age || 'Not provided'}</div>
          </div>
          <div>
            <div className="report-meta-label">Gender</div>
            <div className="report-meta-value">{patient.gender || 'Not provided'}</div>
          </div>
          <div>
            <div className="report-meta-label">Date of Birth</div>
            <div className="report-meta-value">{patient.dob || 'Not provided'}</div>
          </div>
          <div>
            <div className="report-meta-label">MRN / ID</div>
            <div className="report-meta-value">{patient.mrn || 'Not provided'}</div>
          </div>
          <div>
            <div className="report-meta-label">Other Demographics</div>
            <div className="report-meta-value">{patient.other_demographics || 'Not provided'}</div>
          </div>
        </div>
      </div>

      {/* TWO-COLUMN GRID: Vitals & Allergies */}
      <div className="report-grid-2">
        {/* VITAL SIGNS */}
        <div className="card">
          <div className="card-header">
            <div className="card-title">
              <Thermometer size={18} />
              <span>Vital Signs</span>
            </div>
          </div>
          <table className="clinical-table">
            <tbody>
              <tr>
                <td style={{ fontWeight: 600, width: '45%' }}>Blood Pressure</td>
                <td>{vitals.blood_pressure || 'Not documented'}</td>
              </tr>
              <tr>
                <td style={{ fontWeight: 600 }}>Heart Rate</td>
                <td>{vitals.heart_rate || 'Not documented'}</td>
              </tr>
              <tr>
                <td style={{ fontWeight: 600 }}>Temperature</td>
                <td>{vitals.temperature || 'Not documented'}</td>
              </tr>
              <tr>
                <td style={{ fontWeight: 600 }}>Respiratory Rate</td>
                <td>{vitals.respiratory_rate || 'Not documented'}</td>
              </tr>
              <tr>
                <td style={{ fontWeight: 600 }}>Oxygen Saturation (SpO2)</td>
                <td>{vitals.oxygen_saturation || 'Not documented'}</td>
              </tr>
              <tr>
                <td style={{ fontWeight: 600 }}>Weight</td>
                <td>{vitals.weight || 'Not documented'}</td>
              </tr>
              {vitals.other_vitals && vitals.other_vitals !== 'Not documented' && (
                <tr>
                  <td style={{ fontWeight: 600 }}>Other Vitals</td>
                  <td>{vitals.other_vitals}</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {/* ALLERGIES */}
        <div className="card">
          <div className="card-header">
            <div className="card-title">
              <ShieldCheck size={18} />
              <span>Allergies</span>
            </div>
          </div>
          {allergies.length === 0 || (allergies.length === 1 && allergies[0].allergy === 'Not documented') ? (
            <div style={{ color: 'var(--neutral-500)', fontSize: '0.9rem', fontStyle: 'italic', padding: '0.5rem 0' }}>
              Not documented (Absence of documentation does not confirm lack of allergies).
            </div>
          ) : (
            <table className="clinical-table">
              <thead>
                <tr>
                  <th>Allergen / Substance</th>
                  <th>Documented Reaction</th>
                </tr>
              </thead>
              <tbody>
                {allergies.map((item, idx) => (
                  <tr key={idx}>
                    <td style={{ fontWeight: 600, color: 'var(--danger-700)' }}>{item.allergy}</td>
                    <td>{item.reaction || 'Not documented'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>

      {/* DIAGNOSES & CONDITIONS */}
      <div className="card">
        <div className="card-header">
          <div className="card-title">
            <FileCheck2 size={18} />
            <span>Diagnoses & Conditions</span>
          </div>
        </div>
        {diagnoses.length === 0 ? (
          <div style={{ color: 'var(--neutral-500)', fontSize: '0.9rem', fontStyle: 'italic' }}>
            No explicit diagnoses or conditions documented in source text.
          </div>
        ) : (
          <table className="clinical-table">
            <thead>
              <tr>
                <th>Condition</th>
                <th>Diagnostic Status</th>
                <th>Clinical Context Notes</th>
              </tr>
            </thead>
            <tbody>
              {diagnoses.map((diag, idx) => {
                const isDocumented = diag.status?.toLowerCase() === 'documented';
                return (
                  <tr key={idx}>
                    <td style={{ fontWeight: 600 }}>{diag.condition}</td>
                    <td>
                      <span className={`badge ${isDocumented ? 'badge-completed' : 'badge-processing'}`}>
                        {diag.status || 'documented'}
                      </span>
                    </td>
                    <td>{diag.notes || 'Not documented'}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>

      {/* MEDICATIONS */}
      <div className="card">
        <div className="card-header">
          <div className="card-title">
            <Pill size={18} />
            <span>Medications</span>
          </div>
        </div>
        {medications.length === 0 ? (
          <div style={{ color: 'var(--neutral-500)', fontSize: '0.9rem', fontStyle: 'italic' }}>
            No active or prescribed medications documented.
          </div>
        ) : (
          <table className="clinical-table">
            <thead>
              <tr>
                <th>Medication</th>
                <th>Dosage</th>
                <th>Frequency</th>
                <th>Route</th>
                <th>Notes</th>
              </tr>
            </thead>
            <tbody>
              {medications.map((med, idx) => (
                <tr key={idx}>
                  <td style={{ fontWeight: 600, color: 'var(--primary-700)' }}>{med.medication}</td>
                  <td>{med.dosage || 'Not documented'}</td>
                  <td>{med.frequency || 'Not documented'}</td>
                  <td>{med.route || 'Not documented'}</td>
                  <td>{med.notes || 'Not documented'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* SYMPTOMS */}
      <div className="card">
        <div className="card-header">
          <div className="card-title">
            <HeartPulse size={18} />
            <span>Documented Symptoms</span>
          </div>
        </div>
        {symptoms.length === 0 ? (
          <div style={{ color: 'var(--neutral-500)', fontSize: '0.9rem', fontStyle: 'italic' }}>
            No symptoms explicitly stated.
          </div>
        ) : (
          <table className="clinical-table">
            <thead>
              <tr>
                <th>Symptom</th>
                <th>Duration</th>
                <th>Severity</th>
                <th>Notes</th>
              </tr>
            </thead>
            <tbody>
              {symptoms.map((s, idx) => (
                <tr key={idx}>
                  <td style={{ fontWeight: 600 }}>{s.symptom}</td>
                  <td>{s.duration || 'Not documented'}</td>
                  <td>{s.severity || 'Not documented'}</td>
                  <td>{s.notes || 'Not documented'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* TWO-COLUMN GRID: Observations & Concerns */}
      <div className="report-grid-2">
        {/* CLINICAL OBSERVATIONS */}
        <div className="card">
          <div className="card-header">
            <div className="card-title">
              <Eye size={18} />
              <span>Clinical Observations</span>
            </div>
          </div>
          {observations.length === 0 ? (
            <div style={{ color: 'var(--neutral-500)', fontSize: '0.9rem', fontStyle: 'italic' }}>
              None recorded.
            </div>
          ) : (
            <ul style={{ paddingLeft: '1.25rem', fontSize: '0.875rem', lineHeight: '1.6' }}>
              {observations.map((obs, idx) => (
                <li key={idx} style={{ marginBottom: '0.4rem' }}>{obs}</li>
              ))}
            </ul>
          )}
        </div>

        {/* CLINICAL CONCERNS */}
        <div className="card">
          <div className="card-header">
            <div className="card-title">
              <AlertTriangle size={18} />
              <span>Potential Document Concerns</span>
            </div>
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--neutral-500)', marginBottom: '0.65rem' }}>
            Note: Potential concerns derived from document review; not confirmed clinical diagnoses.
          </div>
          {concerns.length === 0 ? (
            <div style={{ color: 'var(--neutral-500)', fontSize: '0.9rem', fontStyle: 'italic' }}>
              No critical document concerns flagged.
            </div>
          ) : (
            <ul style={{ paddingLeft: '1.25rem', fontSize: '0.875rem', lineHeight: '1.6' }}>
              {concerns.map((c, idx) => (
                <li key={idx} style={{ marginBottom: '0.4rem', color: 'var(--warning-700)' }}>{c}</li>
              ))}
            </ul>
          )}
        </div>
      </div>

      {/* MISSING / INCOMPLETE INFORMATION */}
      {missingInfo.length > 0 && (
        <div className="alert-box alert-missing" style={{ marginBottom: '1.5rem' }}>
          <HelpCircle size={20} style={{ flexShrink: 0, marginTop: '2px', color: 'var(--neutral-600)' }} />
          <div>
            <h4 style={{ fontSize: '0.95rem', fontWeight: 600, marginBottom: '0.35rem', color: 'var(--neutral-800)' }}>
              Missing or Incomplete Information
            </h4>
            <p style={{ fontSize: '0.85rem', color: 'var(--neutral-600)', marginBottom: '0.4rem' }}>
              The following standard clinical elements are absent from this documentation:
            </p>
            <ul style={{ paddingLeft: '1.25rem', fontSize: '0.875rem', lineHeight: '1.6' }}>
              {missingInfo.map((item, idx) => (
                <li key={idx}>{item}</li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  );
}
