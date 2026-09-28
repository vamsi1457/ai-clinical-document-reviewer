import React from 'react';
import { Search, Filter } from 'lucide-react';
import ReportCard from './ReportCard';
import EmptyState from './EmptyState';

export default function ReportHistory({
  reports,
  searchQuery,
  onSearchChange,
  statusFilter,
  onStatusChange,
  onDeleteReport,
}) {
  return (
    <div>
      <div
        style={{
          display: 'flex',
          gap: '1rem',
          flexWrap: 'wrap',
          marginBottom: '1.5rem',
          alignItems: 'center',
          justifyContent: 'space-between',
        }}
      >
        <div style={{ position: 'relative', flex: 1, minWidth: '240px' }}>
          <Search
            size={18}
            style={{
              position: 'absolute',
              left: '12px',
              top: '50%',
              transform: 'translateY(-50%)',
              color: 'var(--neutral-400)',
            }}
          />
          <input
            type="text"
            placeholder="Search by filename, summary, or ID..."
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            style={{
              width: '100%',
              padding: '0.65rem 1rem 0.65rem 2.4rem',
              borderRadius: 'var(--radius-md)',
              border: '1px solid var(--neutral-300)',
              fontSize: '0.9rem',
              outline: 'none',
              background: '#ffffff',
            }}
          />
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Filter size={16} color="var(--neutral-500)" />
          <select
            value={statusFilter}
            onChange={(e) => onStatusChange(e.target.value)}
            style={{
              padding: '0.65rem 1rem',
              borderRadius: 'var(--radius-md)',
              border: '1px solid var(--neutral-300)',
              fontSize: '0.875rem',
              background: '#ffffff',
              color: 'var(--neutral-700)',
              fontWeight: 500,
            }}
          >
            <option value="ALL">All Statuses</option>
            <option value="COMPLETED">Completed</option>
            <option value="PROCESSING">Processing</option>
            <option value="FAILED">Failed</option>
          </select>
        </div>
      </div>

      {reports.length === 0 ? (
        <EmptyState
          title="No clinical reports match your criteria"
          description="Try adjusting your search terms or filter, or submit a new clinical document for review."
        />
      ) : (
        reports.map((item) => (
          <ReportCard key={item.id} item={item} onDelete={onDeleteReport} />
        ))
      )}
    </div>
  );
}
