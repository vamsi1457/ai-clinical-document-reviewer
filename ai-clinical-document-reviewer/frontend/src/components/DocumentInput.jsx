import React, { useState } from 'react';
import { AlignLeft, FileUp } from 'lucide-react';
import TextInput from './TextInput';
import FileUpload from './FileUpload';

export default function DocumentInput({ onAnalyzeText, onAnalyzeFile, disabled }) {
  const [activeTab, setActiveTab] = useState('text'); // 'text' | 'document'

  return (
    <div className="card">
      <div className="tabs-container">
        <button
          type="button"
          className={`tab-btn ${activeTab === 'text' ? 'active' : ''}`}
          onClick={() => setActiveTab('text')}
        >
          <AlignLeft size={18} />
          <span>Clinical Text</span>
        </button>
        <button
          type="button"
          className={`tab-btn ${activeTab === 'document' ? 'active' : ''}`}
          onClick={() => setActiveTab('document')}
        >
          <FileUp size={18} />
          <span>Upload Document</span>
        </button>
      </div>

      <div style={{ marginTop: '1rem' }}>
        {activeTab === 'text' ? (
          <TextInput onAnalyze={onAnalyzeText} disabled={disabled} />
        ) : (
          <FileUpload onAnalyze={onAnalyzeFile} disabled={disabled} />
        )}
      </div>
    </div>
  );
}
