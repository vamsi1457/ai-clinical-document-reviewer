import React, { useEffect, useState, useMemo } from 'react';
import { useAnalysis } from '../hooks/useAnalysis';
import ReportHistory from '../components/ReportHistory';
import ErrorMessage from '../components/ErrorMessage';
import { Loader2 } from 'lucide-react';

export default function History() {
  const { historyList, loading, error, setError, fetchHistory, deleteReport } = useAnalysis();
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');

  useEffect(() => {
    fetchHistory();
  }, [fetchHistory]);

  const filteredReports = useMemo(() => {
    return historyList.filter((item) => {
      // Status filter
      if (statusFilter !== 'ALL' && item.status?.toUpperCase() !== statusFilter) {
        return false;
      }

      // Search query filter
      if (searchQuery.trim()) {
        const query = searchQuery.toLowerCase();
        const matchesSummary = item.report_summary?.toLowerCase().includes(query);
        const matchesFilename = item.original_filename?.toLowerCase().includes(query);
        const matchesId = item.id?.toLowerCase().includes(query);
        return matchesSummary || matchesFilename || matchesId;
      }

      return true;
    });
  }, [historyList, searchQuery, statusFilter]);

  const handleDelete = async (id) => {
    try {
      await deleteReport(id);
    } catch {
      // Error handled in hook
    }
  };

  return (
    <div>
      <div style={{ marginBottom: '1.75rem' }}>
        <h2 style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--neutral-900)' }}>
          Clinical Review History
        </h2>
        <p style={{ fontSize: '0.9rem', color: 'var(--neutral-500)', marginTop: '0.2rem' }}>
          Audit and access previously processed clinical document reviews, structured summaries, and extraction metadata.
        </p>
      </div>

      <ErrorMessage message={error} onDismiss={() => setError(null)} />

      {loading && historyList.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '3rem' }}>
          <Loader2 size={32} style={{ animation: 'spin 1s linear infinite', color: 'var(--primary-600)', margin: '0 auto' }} />
          <p style={{ color: 'var(--neutral-500)', marginTop: '0.75rem', fontSize: '0.9rem' }}>Loading review history...</p>
        </div>
      ) : (
        <ReportHistory
          reports={filteredReports}
          searchQuery={searchQuery}
          onSearchChange={setSearchQuery}
          statusFilter={statusFilter}
          onStatusChange={setStatusFilter}
          onDeleteReport={handleDelete}
        />
      )}
    </div>
  );
}
