import React from 'react';
import { NavLink } from 'react-router-dom';
import { FileText, History, Stethoscope, AlertTriangle } from 'lucide-react';

export default function Header() {
  return (
    <header className="header">
      <div className="disclaimer-banner">
        <AlertTriangle size={15} />
        <span>
          <strong>CLINICAL DOCUMENT REVIEW ASSISTANT:</strong> For document extraction & review only.
          All data is strictly synthetic. Does not replace professional medical judgment.
        </span>
      </div>

      <div className="header-inner">
        <div className="brand-wrapper">
          <div className="brand-icon">
            <Stethoscope size={24} />
          </div>
          <div className="brand-text">
            <h1>AI Clinical Document Reviewer</h1>
            <p>Upload or enter clinical documentation to generate a structured clinical review.</p>
          </div>
        </div>

        <nav className="nav-links">
          <NavLink
            to="/"
            end
            className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
          >
            <FileText size={18} />
            <span>New Review</span>
          </NavLink>
          <NavLink
            to="/history"
            className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
          >
            <History size={18} />
            <span>History</span>
          </NavLink>
        </nav>
      </div>
    </header>
  );
}
