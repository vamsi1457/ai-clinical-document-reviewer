import React, { useState } from 'react';
import { Play, RotateCcw, FileText } from 'lucide-react';

const SYNTHETIC_SAMPLE_TEXT = `OUTPATIENT CLINICAL ENCOUNTER NOTE (SYNTHETIC DATA)
Patient: John Carter    Age: 45    Gender: Male
Date of Birth: 1981-06-22    MRN: SYN-883921

Chief Complaint:
Fever, persistent cough, and fatigue for two days. Commenced abruptly 48 hours ago.

Vital Signs:
- Blood Pressure: 130/85 mmHg
- Heart Rate: 92 bpm
- Temperature: 38.5 C
- Respiratory Rate: 18 /min
- Oxygen Saturation: 98% room air
- Weight: 82.5 kg

Current Medications:
- Paracetamol 500 mg oral tablet, twice daily for fever.
- Lisinopril 10 mg oral tablet, once daily for mild hypertension.

Allergies:
No known drug allergies (NKDA).

Assessment & Plan:
1. Acute Upper Respiratory Tract Infection (viral) - Documented
2. Essential Hypertension - Documented
3. Suspected seasonal influenza - Suspected (swab pending)
Plan: Continue Paracetamol 500 mg twice daily, hydration, rest. Follow-up in 48-72 hours if fever persists.`;

export default function TextInput({ onAnalyze, disabled }) {
  const [text, setText] = useState('');
  const [validationError, setValidationError] = useState('');

  const handleTextChange = (e) => {
    setText(e.target.value);
    if (validationError && e.target.value.trim()) {
      setValidationError('');
    }
  };

  const handleClear = () => {
    setText('');
    setValidationError('');
  };

  const handleLoadSample = () => {
    setText(SYNTHETIC_SAMPLE_TEXT);
    setValidationError('');
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!text || !text.trim()) {
      setValidationError('Please enter clinical text before submitting.');
      return;
    }
    setValidationError('');
    onAnalyze(text.trim());
  };

  return (
    <form onSubmit={handleSubmit}>
      <div className="textarea-wrapper">
        <textarea
          className="clinical-textarea"
          value={text}
          onChange={handleTextChange}
          placeholder="Paste or type synthetic clinical documentation here (e.g. encounter note, triage slip, discharge summary)..."
          disabled={disabled}
        />
        <div className="textarea-footer">
          <span>{text.length.toLocaleString()} characters</span>
          <div style={{ display: 'flex', gap: '0.75rem' }}>
            <button
              type="button"
              onClick={handleLoadSample}
              className="btn btn-secondary"
              style={{ padding: '0.35rem 0.75rem', fontSize: '0.8rem' }}
              disabled={disabled}
            >
              <FileText size={14} />
              Load Sample Note
            </button>
            <button
              type="button"
              onClick={handleClear}
              className="btn btn-secondary"
              style={{ padding: '0.35rem 0.75rem', fontSize: '0.8rem' }}
              disabled={disabled || !text}
            >
              <RotateCcw size={14} />
              Clear
            </button>
          </div>
        </div>
      </div>

      {validationError && (
        <div style={{ color: 'var(--danger-600)', fontSize: '0.875rem', marginBottom: '1rem', fontWeight: 500 }}>
          {validationError}
        </div>
      )}

      <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '1rem' }}>
        <button
          type="submit"
          className="btn btn-primary"
          disabled={disabled || !text.trim()}
          style={{ minWidth: '180px' }}
        >
          <Play size={16} />
          Analyze Clinical Text
        </button>
      </div>
    </form>
  );
}
