import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Header from './components/Header';
import Home from './pages/Home';
import History from './pages/History';
import ReportDetails from './pages/ReportDetails';

export default function App() {
  return (
    <BrowserRouter>
      <div className="app-container">
        <Header />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/history" element={<History />} />
            <Route path="/reports/:id" element={<ReportDetails />} />
          </Routes>
        </main>
        <footer
          style={{
            borderTop: '1px solid var(--neutral-200)',
            padding: '1.5rem',
            textAlign: 'center',
            fontSize: '0.8rem',
            color: 'var(--neutral-500)',
            backgroundColor: '#ffffff',
          }}
        >
          <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
            <p>
              <strong>AI Clinical Document Reviewer</strong> — Production-Grade Clinical Documentation Assistant.
            </p>
            <p style={{ marginTop: '0.25rem', color: 'var(--neutral-400)' }}>
              All patient information, medical histories, and encounter reports used for demonstration are 100% synthetic.
              This system assists with document review and extraction; it does not perform clinical diagnosis or replace medical judgment.
            </p>
          </div>
        </footer>
      </div>
    </BrowserRouter>
  );
}
