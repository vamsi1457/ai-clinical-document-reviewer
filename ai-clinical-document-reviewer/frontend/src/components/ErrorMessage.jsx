import React from 'react';
import { AlertOctagon, X } from 'lucide-react';

export default function ErrorMessage({ message, onDismiss }) {
  if (!message) return null;

  return (
    <div className="alert-box alert-inconsistency" style={{ borderColor: 'var(--danger-600)', background: 'var(--danger-50)', color: 'var(--danger-700)' }}>
      <AlertOctagon size={20} style={{ flexShrink: 0, marginTop: '2px' }} />
      <div style={{ flex: 1, fontSize: '0.9rem', lineHeight: '1.5' }}>
        <strong>Error: </strong>
        <span>{message}</span>
      </div>
      {onDismiss && (
        <button
          onClick={onDismiss}
          style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'inherit' }}
          title="Dismiss error"
        >
          <X size={18} />
        </button>
      )}
    </div>
  );
}
