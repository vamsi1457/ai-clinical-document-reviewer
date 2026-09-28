import React, { useState, useRef } from 'react';
import { UploadCloud, File, Trash2, Play, AlertCircle } from 'lucide-react';
import { formatFileSize } from '../utils/formatters';

const ALLOWED_EXTENSIONS = ['pdf', 'png', 'jpg', 'jpeg'];
const MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024; // 10MB

export default function FileUpload({ onAnalyze, disabled }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const [validationError, setValidationError] = useState('');
  const fileInputRef = useRef(null);

  const validateFile = (file) => {
    if (!file) return false;

    // 1. Empty check
    if (file.size === 0) {
      setValidationError('Uploaded file is empty.');
      return false;
    }

    // 2. Size check
    if (file.size > MAX_FILE_SIZE_BYTES) {
      setValidationError('File size exceeds the 10 MB limit.');
      return false;
    }

    // 3. Extension check
    const ext = file.name.split('.').pop().toLowerCase();
    if (!ALLOWED_EXTENSIONS.includes(ext)) {
      setValidationError('Unsupported file type. Please upload PDF, PNG, JPG or JPEG.');
      return false;
    }

    setValidationError('');
    return true;
  };

  const handleFileSelection = (file) => {
    if (validateFile(file)) {
      setSelectedFile(file);
    } else {
      setSelectedFile(null);
    }
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelection(e.dataTransfer.files[0]);
    }
  };

  const handleBrowseClick = () => {
    fileInputRef.current?.click();
  };

  const handleInputChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFileSelection(e.target.files[0]);
    }
  };

  const handleRemove = () => {
    setSelectedFile(null);
    setValidationError('');
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!selectedFile) {
      setValidationError('Please select a clinical document file before submitting.');
      return;
    }
    if (validateFile(selectedFile)) {
      onAnalyze(selectedFile);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        ref={fileInputRef}
        type="file"
        accept=".pdf,.png,.jpg,.jpeg,application/pdf,image/png,image/jpeg"
        onChange={handleInputChange}
        style={{ display: 'none' }}
        disabled={disabled}
      />

      <div
        className={`dropzone ${dragActive ? 'drag-active' : ''}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={handleBrowseClick}
      >
        <div className="dropzone-icon">
          <UploadCloud size={28} />
        </div>
        <h3 style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--neutral-800)', marginBottom: '0.35rem' }}>
          Drag and drop your clinical document here
        </h3>
        <p style={{ fontSize: '0.85rem', color: 'var(--neutral-500)', marginBottom: '1rem' }}>
          Supported formats: PDF, PNG, JPG, JPEG (Max 10 MB)
        </p>
        <button
          type="button"
          className="btn btn-secondary"
          onClick={(e) => {
            e.stopPropagation();
            handleBrowseClick();
          }}
          disabled={disabled}
        >
          Browse Files
        </button>
      </div>

      {selectedFile && (
        <div className="selected-file-card">
          <div className="file-info">
            <div
              style={{
                width: '38px',
                height: '38px',
                borderRadius: 'var(--radius-sm)',
                background: 'var(--primary-100)',
                color: 'var(--primary-700)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <File size={20} />
            </div>
            <div>
              <div className="file-name">{selectedFile.name}</div>
              <div className="file-size">{formatFileSize(selectedFile.size)}</div>
            </div>
          </div>
          <button
            type="button"
            className="btn btn-outline-danger"
            onClick={handleRemove}
            disabled={disabled}
            style={{ padding: '0.4rem 0.75rem', fontSize: '0.8rem' }}
          >
            <Trash2 size={14} />
            Remove
          </button>
        </div>
      )}

      {validationError && (
        <div
          style={{
            color: 'var(--danger-600)',
            fontSize: '0.875rem',
            marginTop: '1rem',
            display: 'flex',
            alignItems: 'center',
            gap: '0.4rem',
            fontWeight: 500,
          }}
        >
          <AlertCircle size={16} />
          <span>{validationError}</span>
        </div>
      )}

      <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '1.25rem' }}>
        <button
          type="submit"
          className="btn btn-primary"
          disabled={disabled || !selectedFile}
          style={{ minWidth: '180px' }}
        >
          <Play size={16} />
          Analyze Document
        </button>
      </div>
    </form>
  );
}
