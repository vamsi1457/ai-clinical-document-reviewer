import React from 'react';
import { Check, Loader2 } from 'lucide-react';

export default function ProcessingState({ currentStageIndex, stages }) {
  return (
    <div className="processing-card">
      <div className="pulse-spinner" />
      <h2 style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--neutral-900)', marginBottom: '0.4rem' }}>
        Processing clinical document...
      </h2>
      <p style={{ fontSize: '0.875rem', color: 'var(--neutral-500)' }}>
        Our pipeline is extracting document content, evaluating clinical context, and verifying schema structure.
      </p>

      <div className="stage-tracker">
        {stages.map((stage, idx) => {
          const isDone = idx < currentStageIndex;
          const isCurrent = idx === currentStageIndex;

          return (
            <div
              key={stage}
              className={`stage-item ${isDone ? 'completed' : ''} ${isCurrent ? 'active' : ''}`}
            >
              <div className="stage-dot">
                {isDone ? (
                  <Check size={12} strokeWidth={3} />
                ) : isCurrent ? (
                  <Loader2 size={12} className="spin-fast" style={{ animation: 'spin 1s linear infinite' }} />
                ) : (
                  <span>{idx + 1}</span>
                )}
              </div>
              <span>{stage}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
