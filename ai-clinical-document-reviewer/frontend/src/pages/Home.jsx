import React from 'react';
import { useNavigate } from 'react-router-dom';
import DocumentInput from '../components/DocumentInput';
import ProcessingState from '../components/ProcessingState';
import ErrorMessage from '../components/ErrorMessage';
import { useAnalysis } from '../hooks/useAnalysis';

export default function Home() {
  const navigate = useNavigate();
  const {
    loading,
    currentStage,
    stages,
    error,
    setError,
    analyzeText,
    analyzeFile,
  } = useAnalysis();

  const handleAnalyzeText = async (text) => {
    try {
      const result = await analyzeText(text);
      if (result && result.id) {
        navigate(`/reports/${result.id}`);
      }
    } catch {
      // Error handled inside hook
    }
  };

  const handleAnalyzeFile = async (file) => {
    try {
      const result = await analyzeFile(file);
      if (result && result.id) {
        navigate(`/reports/${result.id}`);
      }
    } catch {
      // Error handled inside hook
    }
  };

  return (
    <div>
      <div style={{ marginBottom: '1.75rem' }}>
        <h2 style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--neutral-900)' }}>
          Submit Clinical Documentation
        </h2>
        <p style={{ fontSize: '0.9rem', color: 'var(--neutral-500)', marginTop: '0.2rem' }}>
          Input typed notes or upload digital/scanned clinical documents (PDF, PNG, JPG) to initiate AI document review.
        </p>
      </div>

      <ErrorMessage message={error} onDismiss={() => setError(null)} />

      {loading ? (
        <ProcessingState currentStageIndex={currentStage} stages={stages} />
      ) : (
        <DocumentInput
          onAnalyzeText={handleAnalyzeText}
          onAnalyzeFile={handleAnalyzeFile}
          disabled={loading}
        />
      )}
    </div>
  );
}
