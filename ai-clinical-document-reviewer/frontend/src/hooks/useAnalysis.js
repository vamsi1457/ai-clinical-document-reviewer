import { useState, useCallback } from 'react';
import analysisApi from '../api/analysisApi';

export function useAnalysis() {
  const [loading, setLoading] = useState(false);
  const [currentStage, setCurrentStage] = useState(0);
  const [error, setError] = useState(null);
  const [currentReport, setCurrentReport] = useState(null);
  const [historyList, setHistoryList] = useState([]);

  const stages = [
    'Reading document',
    'Extracting information',
    'Analyzing clinical content',
    'Generating structured report',
    'Saving report',
  ];

  const runStageAnimation = () => {
    setCurrentStage(0);
    const interval = setInterval(() => {
      setCurrentStage((prev) => {
        if (prev < stages.length - 1) return prev + 1;
        return prev;
      });
    }, 1400);
    return interval;
  };

  const analyzeText = useCallback(async (text) => {
    setLoading(true);
    setError(null);
    const timer = runStageAnimation();

    try {
      const response = await analysisApi.submitText(text);
      clearInterval(timer);
      if (!response.success) {
        throw new Error(response.error?.message || 'Analysis failed.');
      }
      setCurrentReport(response.data);
      return response.data;
    } catch (err) {
      clearInterval(timer);
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const analyzeFile = useCallback(async (file) => {
    setLoading(true);
    setError(null);
    const timer = runStageAnimation();

    try {
      const response = await analysisApi.submitFile(file);
      clearInterval(timer);
      if (!response.success) {
        throw new Error(response.error?.message || 'Analysis failed.');
      }
      setCurrentReport(response.data);
      return response.data;
    } catch (err) {
      clearInterval(timer);
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchHistory = useCallback(async (params = {}) => {
    setLoading(true);
    setError(null);
    try {
      const response = await analysisApi.listAnalyses(params);
      if (response.success) {
        setHistoryList(response.data || []);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchReportById = useCallback(async (id) => {
    setLoading(true);
    setError(null);
    try {
      const response = await analysisApi.getAnalysisById(id);
      if (!response.success) {
        throw new Error(response.error?.message || 'Report not found.');
      }
      setCurrentReport(response.data);
      return response.data;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const deleteReport = useCallback(async (id) => {
    try {
      const response = await analysisApi.deleteAnalysis(id);
      if (response.success) {
        setHistoryList((prev) => prev.filter((item) => item.id !== id));
      }
      return response;
    } catch (err) {
      setError(err.message);
      throw err;
    }
  }, []);

  return {
    loading,
    currentStage,
    stages,
    error,
    setError,
    currentReport,
    historyList,
    analyzeText,
    analyzeFile,
    fetchHistory,
    fetchReportById,
    deleteReport,
  };
}
