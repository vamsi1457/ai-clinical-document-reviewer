import React from 'react';
import { CheckCircle2, Clock, AlertCircle } from 'lucide-react';

export default function StatusBadge({ status }) {
  const normalized = (status || '').toUpperCase();

  if (normalized === 'COMPLETED') {
    return (
      <span className="badge badge-completed">
        <CheckCircle2 size={13} />
        <span>Completed</span>
      </span>
    );
  }

  if (normalized === 'PROCESSING' || normalized === 'PENDING') {
    return (
      <span className="badge badge-processing">
        <Clock size={13} />
        <span>Processing</span>
      </span>
    );
  }

  if (normalized === 'FAILED') {
    return (
      <span className="badge badge-failed">
        <AlertCircle size={13} />
        <span>Failed</span>
      </span>
    );
  }

  return (
    <span className="badge badge-neutral">
      <span>{status || 'Unknown'}</span>
    </span>
  );
}
