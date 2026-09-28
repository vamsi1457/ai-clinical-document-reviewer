# AI Clinical Document Reviewer

> **Production-grade web application for AI-powered clinical documentation review, multimodal text extraction, OCR, and structured medical information synthesis.**

[![Backend Tests](https://img.shields.io/badge/pytest-23%20passed-brightgreen.svg)]()
[![Frontend Build](https://img.shields.io/badge/vite-built%20successfully-blue.svg)]()
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg?logo=fastapi&logoColor=white)]()
[![React](https://img.shields.io/badge/React-18-61DAFB.svg?logo=react&logoColor=black)]()
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-4169E1.svg?logo=postgresql&logoColor=white)]()
[![Docker](https://img.shields.io/badge/Docker-compose-2496ED.svg?logo=docker&logoColor=white)]()

---

## Live Deployment Links

- **Live Application URL**: [LIVE_APP_URL_HERE](LIVE_APP_URL_HERE)
- **Backend API URL**: [BACKEND_API_URL_HERE](BACKEND_API_URL_HERE)
- **Interactive Swagger Documentation**: [BACKEND_API_URL_HERE/docs](BACKEND_API_URL_HERE/docs)

---

## Synthetic Data Disclaimer

> [!IMPORTANT]
> **ALL clinical information utilized for development, automated testing, and live demonstration is strictly SYNTHETIC and FICTIONAL.**
>
> No real Protected Health Information (PHI) or Personally Identifiable Information (PII) is processed or stored.
> 
> **Clinical Scope Disclaimer:** The application is an intelligent **DOCUMENT REVIEW ASSISTANT** intended to assist clinicians with structured fact extraction, omissions detection, and discrepancy flagging. It does **NOT** claim to diagnose patients independently or replace professional medical judgment.

---

## Project Overview

In real-world healthcare settings, clinical documentation arrives in diverse formats: typed electronic health record notes, digitized multi-page PDFs, and scanned physical paperwork with variable print and handwriting quality. Clinicians and reviewers spend substantial time extracting pertinent findings, reconciling contradictions, and identifying missing data.

The **AI Clinical Document Reviewer** automates this workflow by ingesting raw text, PDFs, and medical scans, running robust OCR and normalization pipelines, extracting source-grounded clinical facts via configurable Large Language Models, validating output with Pydantic schemas, and presenting structured reviews through a responsive healthcare-grade dashboard.

---

## Key Features

1. **Multimodal Clinical Ingestion**:
   - **Text Mode**: Paste typed clinical notes, encounter summaries, or triage records with live character counting.
   - **Document Mode**: Drag-and-drop or file upload supporting **PDF, PNG, JPG, JPEG** (up to 10 MB).
2. **Adaptive Document Processing & OCR**:
   - Native PyMuPDF digital text extraction for vector PDFs.
   - High-resolution (200 DPI) pixmap rasterization and OCR fallback for scanned or image-only PDFs.
   - Pillow image preprocessing: Grayscale conversion, contrast adjustment, and dynamic resolution scaling.
   - Dual OCR engine: **RapidOCR (PaddleOCR ONNX)** for native zero-dependency execution and **Tesseract OCR** for enterprise container deployments.
3. **Source-Grounded AI Clinical Review**:
   - Strict anti-hallucination prompt constraints.
   - Deterministic low-temperature (`0.0`) structured JSON generation.
   - Explicit distinction between **Documented** vs **Suspected / Uncertain** conditions.
   - Dedicated detection of **Potential Inconsistencies** (e.g. mismatched vital signs across sections).
   - Highlighting of **Missing / Incomplete Information** and **Items Requiring Human Review**.
4. **Resilient Schema Validation & Safe Parsing**:
   - Pydantic v2 schema validation with strict typing.
   - Regex-based markdown cleaner and safe JSON extractor.
   - Automatic single-retry mechanism with corrective feedback on malformed responses.
5. **PostgreSQL Persistence & Audit Trail**:
   - Stores review metadata and structured reports in PostgreSQL using native `JSONB`.
   - Comprehensive audit logging and full raw text recovery.
6. **Professional Healthcare Interface**:
   - Modern, clean dashboard with dedicated status badges (Completed, Processing, Failed).
   - Animated multi-stage loading indicator (`Reading document` → `Extracting information` → `Analyzing clinical content` → `Generating structured report` → `Saving report`).
   - History viewer with live search and status filtering.
   - Print stylesheet for clinical record generation.

---

## Architecture

```mermaid
flowchart TD
    A[React Frontend] --> B[FastAPI Backend]
    B --> C[Input Validation]
    C --> D[Document Processor]
    D --> E[PDF Text Extraction]
    D --> F[OCR / Image Processing]
    E --> G[Extracted Clinical Text]
    F --> G
    G --> H[AI Clinical Analysis]
    H --> I[Pydantic Validation]
    I --> J[Structured Clinical Report]
    J --> K[(PostgreSQL)]
    K --> L[Report History]
    J --> A
```

For complete architectural details, see [docs/architecture.md](docs/architecture.md) and [docs/architecture-diagram.md](docs/architecture-diagram.md).

---

## Tech Stack

| Component | Technology | Rationale |
| :--- | :--- | :--- |
| **Frontend** | React 18, Vite, React Router v6, Axios | Component modularity, fast client-side routing, and responsive healthcare design. |
| **Backend** | Python 3.11+, FastAPI, Pydantic v2 | High-performance asynchronous execution, strict typing, and OpenAPI generation. |
| **Database** | PostgreSQL 15, SQLAlchemy 2.0 | ACID compliance for audit trails; native `JSONB` for structured clinical reports. |
| **Document Processing**| PyMuPDF (`fitz`), Pillow | Blazing fast C-backed PDF parsing and image preprocessing. |
| **OCR Engines** | RapidOCR (PaddleOCR ONNX) & Tesseract | Dual-engine setup ensuring zero-config local runs and containerized Linux support. |
| **AI / LLM** | Google Gemini (2.0 Flash) & OpenAI (GPT-4o-mini) | Configurable multi-provider support with structured JSON mode and low latency. |
| **Infrastructure** | Docker, Docker Compose | Reproducible, single-command containerized orchestration. |
| **Testing** | pytest, httpx, TestClient | Automated validation, OCR, API, and mock AI unit testing. |

---

## Repository Structure

```
ai-clinical-document-reviewer/
├── README.md                           # Master project documentation
├── .gitignore                          # Git ignore rules
├── .env.example                        # Root environment variables template
├── docker-compose.yml                  # Full-stack Docker orchestration
│
├── backend/
│   ├── requirements.txt                # Python backend dependencies
│   ├── Dockerfile                      # Backend container with Tesseract OCR
│   ├── .env.example                    # Backend environment template
│   │
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                     # FastAPI application entrypoint
│   │   ├── config.py                   # Pydantic Settings configuration
│   │   ├── database.py                 # SQLAlchemy session and engine
│   │   │
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── analysis.py             # Analysis SQLAlchemy model
│   │   │
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── analysis.py             # API DTOs and envelopes
│   │   │   └── report.py               # Structured clinical report schema
│   │   │
│   │   ├── api/
│   │   │   ├── __init__.py             # Combined API router
│   │   │   ├── analysis.py             # Analysis CRUD endpoints
│   │   │   └── health.py               # Health check endpoint
│   │   │
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── document_processor.py   # Central document router
│   │   │   ├── pdf_processor.py        # PyMuPDF digital + scanned PDF extraction
│   │   │   ├── image_processor.py      # Pillow preprocessing & OCR invocation
│   │   │   ├── ocr_service.py          # RapidOCR / Tesseract OCR service
│   │   │   ├── ai_service.py           # Multi-provider LLM review service
│   │   │   └── report_service.py       # Normalization and database persistence
│   │   │
│   │   ├── prompts/
│   │   │   ├── __init__.py
│   │   │   └── clinical_review_prompt.py # System prompts & user prompt builder
│   │   │
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── validators.py           # Text & file binary magic bytes validation
│   │       ├── file_utils.py           # Temporary file context manager
│   │       └── logger.py               # Sanitized logger with secret masking
│   │
│   └── tests/
│       ├── __init__.py
│       ├── test_health.py              # Health endpoint verification
│       ├── test_validation.py          # Text & binary upload validators
│       ├── test_document_processing.py # PDF extraction & OCR engine tests
│       ├── test_ai_service.py          # Schema parsing & error tests
│       └── test_analysis_api.py        # End-to-end API & persistence tests
│
├── frontend/
│   ├── package.json                    # Node dependencies
│   ├── vite.config.js                  # Vite configuration
│   ├── Dockerfile                      # Frontend production container
│   ├── .env.example                    # Frontend environment template
│   ├── index.html                      # HTML entrypoint with Inter font
│   │
│   └── src/
│       ├── main.jsx                    # React bootstrap entrypoint
│       ├── App.jsx                     # Layout & React Router setup
│       │
│       ├── api/
│       │   └── analysisApi.js          # Axios API client
│       │
│       ├── components/
│       │   ├── Header.jsx              # Navbar & disclaimer banner
│       │   ├── DocumentInput.jsx       # Tab container (Text / Document)
│       │   ├── TextInput.jsx           # Clinical text area & sample loader
│       │   ├── FileUpload.jsx          # Drag-and-drop file upload zone
│       │   ├── ProcessingState.jsx     # Animated stage progress tracker
│       │   ├── ReportSummary.jsx       # Executive summary & quick findings
│       │   ├── ClinicalReport.jsx      # Full structured report presentation
│       │   ├── ReportHistory.jsx       # History list with search & filter
│       │   ├── ReportCard.jsx          # History summary card
│       │   ├── StatusBadge.jsx         # Status indicator badge
│       │   ├── ErrorMessage.jsx        # Alert banner
│       │   └── EmptyState.jsx          # Empty state component
│       │
│       ├── pages/
│       │   ├── Home.jsx                # Review submission view
│       │   ├── History.jsx             # Analysis history view
│       │   └── ReportDetails.jsx       # Full clinical report view
│       │
│       ├── hooks/
│       │   └── useAnalysis.js          # Custom React hook for analysis workflows
│       │
│       ├── utils/
│       │   └── formatters.js           # Date, size, and duration formatters
│       │
│       └── styles/
│           └── index.css               # Healthcare design system stylesheet
│
├── docs/
│   ├── architecture.md                 # System components & data flow
│   ├── ai-ml-design.md                 # Model selection & hallucination reduction
│   ├── technical-decisions.md          # Architectural rationale & trade-offs
│   └── architecture-diagram.md         # Flowcharts & state diagrams
│
└── sample_data/
    ├── synthetic_clinical_note.txt     # Synthetic outpatient encounter note
    ├── synthetic_clinical_report.pdf   # Synthetic PDF consultation document
    ├── synthetic_clinical_image.png    # Synthetic clinical encounter scan
    ├── test_missing_patient_info.txt   # Test case: missing demographics
    ├── test_conflicting_vitals.txt     # Test case: conflicting vitals (38.5C vs 37.2C)
    ├── test_poor_quality_ocr.txt       # Test case: noisy degraded OCR
    ├── test_irrelevant_content.txt     # Test case: non-clinical catering invoice
    └── test_incomplete_document.txt    # Test case: truncated emergency note
```

---

## Application Flow

```
1. User Input
   ├── Tab 1: Clinical Text Input (with 1-click synthetic sample note)
   └── Tab 2: Document Upload (PDF, PNG, JPG, JPEG)
       ↓
2. Document Validation
   ├── Content length & non-empty validation
   ├── Size bounds check (<= 10MB)
   └── Magic byte header validation (%PDF-, PNG, JPEG signatures)
       ↓
3. Document Processing & OCR
   ├── Native PyMuPDF digital text extraction
   └── Scanned / Image fallback: 200 DPI pixmap rendering + RapidOCR/Tesseract
       ↓
4. AI Clinical Analysis
   ├── Grounded prompt with explicit anti-hallucination rules
   ├── Deterministic low-temperature (0.0) structured JSON generation
   └── Detection of inconsistencies, omissions, and uncertainties
       ↓
5. Pydantic Schema Validation & Normalization
   ├── Strict schema adherence: StructuredClinicalReport
   └── Auto-retry with corrective feedback on malformed JSON
       ↓
6. Database Persistence
   ├── Saved to PostgreSQL with status COMPLETED and processing time
   └── Structured report stored as native JSONB
       ↓
7. Professional UI Rendering
   ├── Navigates to /reports/:id
   ├── Executive Summary Box (Primary findings & review counters)
   ├── Detailed Cards: Demographics, Vitals, Medications, Diagnoses, Allergies
   ├── Visually prominent Review Alerts and Inconsistency Banners
   └── Audit trail with raw extracted source text inspection
```

---

## API Endpoints

All responses utilize a standardized JSON envelope:

**Success Response:**
```json
{
  "success": true,
  "data": { ... }
}
```

**Error Response:**
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable explanation"
  }
}
```

### Endpoints Overview

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/health` | Health check endpoint returning `{"status": "healthy"}` |
| `POST` | `/api/analyses` | Submit plain text OR file upload for AI review |
| `GET` | `/api/analyses` | List past clinical reports with search and status filtering |
| `GET` | `/api/analyses/{id}`| Retrieve complete structured clinical report by ID |
| `DELETE` | `/api/analyses/{id}`| Delete a clinical report record from database |

---

## Environment Variables

### Backend Environment Variables (`backend/.env`)

```ini
# PostgreSQL Connection URL
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/clinical_db

# AI API Key (Google Gemini or OpenAI key)
AI_API_KEY=your_ai_api_key_here

# AI Model Selection
AI_MODEL=gemini-2.0-flash

# AI Provider: 'auto', 'gemini', or 'openai'
AI_PROVIDER=auto

# Optional OpenAI-compatible Base URL
AI_BASE_URL=

# Application & CORS
ENVIRONMENT=development
FRONTEND_URL=http://localhost:5173
MAX_FILE_SIZE_MB=10

# OCR Configuration (Leave blank for automatic detection)
TESSERACT_CMD=
OCR_ENGINE=auto
```

### Frontend Environment Variables (`frontend/.env`)

```ini
# Backend API Base URL
VITE_API_URL=http://localhost:8000/api
```

---

## Local Setup

### Prerequisites
- **Python**: 3.11+
- **Node.js**: 18+ (with `npm`)
- **PostgreSQL**: 14+ (or Docker)

### Option 1: Docker Compose (Recommended)

To launch the complete application stack (PostgreSQL, FastAPI Backend, and React Frontend) with a single command:

```bash
# 1. Clone the repository and enter directory
cd ai-clinical-document-reviewer

# 2. Copy the environment configuration
cp .env.example .env

# 3. Add your AI API Key into .env
# AI_API_KEY=your_gemini_or_openai_key

# 4. Build and start containers
docker compose up --build
```

- **Frontend**: Accessible at `http://localhost:5173`
- **Backend**: Accessible at `http://localhost:8000`
- **Interactive API Docs**: `http://localhost:8000/docs`

---

### Option 2: Manual Local Setup

#### Step 1: Database Setup
Ensure PostgreSQL is running locally and create the database:
```sql
CREATE DATABASE clinical_db;
```

#### Step 2: Backend Setup
```bash
cd backend

# Create and activate virtual environment
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your DATABASE_URL and AI_API_KEY

# Run backend server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### Step 3: Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env

# Run development server
npm run dev
```
Open `http://localhost:5173` in your browser.

---

## Running Automated Tests

The test suite thoroughly exercises validation rules, PDF extraction, OCR engines, AI schema validation, database persistence, and end-to-end API workflows.

```bash
# Run pytest from the repository root
python -m pytest backend/tests -v
```

**Test Coverage Highlights:**
- `test_health.py`: Verifies `/api/health` status.
- `test_validation.py`: Tests empty inputs, character bounds, file size limits, and binary magic byte headers.
- `test_document_processing.py`: Tests digital extraction from `synthetic_clinical_report.pdf` and OCR from `synthetic_clinical_image.png`.
- `test_ai_service.py`: Tests JSON parsing, markdown stripping, and Pydantic validation.
- `test_analysis_api.py`: Tests complete CRUD lifecycle with isolated database sessions.

---

## Public Deployment Instructions

The application is structured for cloud deployment:

### 1. Frontend Deployment (Vercel / Netlify)
- **Framework**: Vite
- **Root Directory**: `frontend/`
- **Build Command**: `npm run build`
- **Output Directory**: `dist`
- **Environment Variables**:
  - `VITE_API_URL`: Your deployed backend API URL (e.g. `https://clinical-backend.onrender.com/api`)

### 2. Backend Deployment (Render / Railway)
- **Root Directory**: `backend/`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Environment Variables**:
  - `DATABASE_URL`: Hosted PostgreSQL connection URI (e.g. Supabase, Neon, or Railway Postgres)
  - `AI_API_KEY`: Your production Google Gemini or OpenAI API Key
  - `AI_MODEL`: `gemini-2.0-flash`
  - `FRONTEND_URL`: URL of the deployed frontend
  - `ENVIRONMENT`: `production`

---

## Application Screenshots

> *Add application screenshots showcasing the review workflow below:*

### 1. Clinical Ingestion Dashboard
*(Screenshot placeholder: Dual input interface showing plain text mode and document drag-and-drop)*

### 2. Multi-Stage Document Processing
*(Screenshot placeholder: Animated stage tracker showing real-time extraction and AI analysis)*

### 3. Structured Clinical Report
*(Screenshot placeholder: Executive summary, vitals table, active medications, diagnoses, and prominent review alert boxes)*

### 4. Review History & Audit Log
*(Screenshot placeholder: Searchable list of past reviews with status badges and raw source text viewer)*

---

## Known Limitations & Future Improvements

### Known Limitations
1. **Low-Quality Cursive Handwriting**: Highly degraded or skewed historical handwritten notes may produce lower OCR confidence scores.
2. **Synchronous Request Pipeline**: While efficient for typical documents, multi-hundred-page records could experience client timeout without background job queues.

### Future Improvements
1. **Asynchronous Task Queue**: Transition long multi-file batch jobs to Celery + Redis workers with WebSocket progress streaming.
2. **Medical Terminology Mapping**: Standardize extracted conditions and medications to SNOMED-CT, ICD-10, and RxNorm concept identifiers.
3. **Multi-Clinician Annotation**: Enable healthcare reviewers to directly annotate, approve, and sign off on AI review items in the UI.

---

## License

MIT License. Designed and developed as a production-quality placement assignment demonstrating full-stack AI/ML engineering, defensive healthcare architecture, and resilient document processing.
