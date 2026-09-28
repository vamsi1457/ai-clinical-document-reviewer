# Technical Decisions & Architectural Rationale

This document provides in-depth technical rationale, trade-off evaluations, maintainability assessments, and security considerations behind the core choices in the **AI Clinical Document Reviewer** architecture.

---

## 1. Core Technology Selection & Rationale

### A. Frontend: React 18 & Vite
- **Why Selected**:
  - **Component Composition**: Clinical reports are highly modular documents comprising patient demographics, vitals grids, medication schedules, and alert cards. React's component model enables strict separation of concerns into isolated, reusable presentational units (`ReportSummary`, `ClinicalReport`, `ReportHistory`).
  - **State Management & UX Responsiveness**: React hooks (`useAnalysis`, `useMemo`) enable reactive, asynchronous UI updates during multi-stage backend processing without freezing the DOM.
  - **Vite Developer Experience & Build Performance**: Vite's native ES module architecture provides near-instantaneous hot module replacement (HMR) and optimized Rollup tree-shaking for small, fast production bundles.
- **Alternatives Considered**: Next.js, Vue, Plain Vanilla JS.
  - *Trade-off*: Next.js introduces SSR/Node server complexity which is unnecessary for an authenticated/internal clinical dashboard consuming a separate REST API backend.

### B. Backend: FastAPI & Python 3.11+
- **Why Selected**:
  - **Native Async & Performance**: Built on Starlette and Uvicorn, FastAPI provides asynchronous concurrency that prevents thread-pool exhaustion during long-running OCR or LLM HTTP calls.
  - **Automatic Schema Serialization & OpenAPI**: Deep integration with Pydantic enables end-to-end type safety, automatic request validation, and auto-generated Swagger UI (`/docs`).
  - **Python Ecosystem Dominance**: Python is the lingua franca for medical NLP, OCR bindings (`fitz`, `PIL`, `rapidocr`), and AI SDKs.
- **Alternatives Considered**: Flask, Django, Node.js/Express.
  - *Trade-off*: Flask lacks modern async-first execution and requires extra boilerplate for OpenAPI specs; Django is overly monolithic for an API-centric microservice.

### C. Database: PostgreSQL 15 & SQLAlchemy 2.0
- **Why Selected**:
  - **Hybrid Relational & Document Model**: Clinical document metadata (timestamps, IDs, statuses, input types) benefits from ACID-compliant relational schemas and foreign keys, while the structured clinical report itself requires a flexible, nested structure. PostgreSQL's native `JSONB` column provides the best of both worlds: structured binary JSON with indexing and schema adaptability without needing a separate document store like MongoDB.
  - **SQLAlchemy 2.0**: The industry standard Python ORM providing type-safe queries, migration support, connection pooling with health pre-pings, and unit test portability (allowing SQLite in pytest).
- **Alternatives Considered**: MongoDB, MySQL, SQLite-only.
  - *Trade-off*: MongoDB lacks the strict transactional integrity and relational join capabilities essential for clinical audit logs; SQLite is insufficient for high-concurrency production deployments.

### D. Document Processing: PyMuPDF (`fitz`)
- **Why Selected**:
  - **Unrivaled Processing Speed**: Built on the MuPDF C-library, PyMuPDF extracts text up to 10x faster than pure-Python libraries like PyPDF2 or pdfminer.
  - **High-Fidelity Page Rendering**: Supports rendering PDF pages directly to high-DPI pixmaps (`page.get_pixmap(dpi=200)`), enabling seamless fallback to OCR when handling scanned or rasterized PDFs.
- **Alternatives Considered**: PyPDF, pdfplumber, pdf2image.
  - *Trade-off*: Requires C-binary wheel bindings, which are readily available and packaged in modern Python wheels and Docker images.

### E. Dual OCR Architecture: RapidOCR (PaddleOCR ONNX) + Tesseract
- **Why Selected**:
  - **Zero-Dependency Local Portability**: Traditional OCR often requires installing external OS-level binaries (`tesseract-ocr`), which can fail or cause path mismatches across varied developer environments (e.g. Windows without admin privileges). By pairing RapidOCR (an ONNX-powered port of PaddleOCR) with Tesseract fallback, the pipeline runs out-of-the-box everywhere while preserving high accuracy.
- **Alternatives Considered**: EasyOCR, Cloud Vision APIs.
  - *Trade-off*: Cloud OCR APIs incur recurring costs and transmit raw patient images to third parties; on-device OCR keeps data within the local/private boundary.

### F. LLM Structured Output & JSON Mode
- **Why Selected**:
  - **Eliminating Freeform Text Ambiguity**: Freeform text generation requires brittle post-hoc regular expressions that frequently break on edge cases. Forcing the LLM into structured JSON mode with explicit Pydantic schemas guarantees consistent schema shape and data types.
  - **Low-Temperature Determinism**: Temperature set to `0.0` ensures clinical facts are extracted verbatim rather than creatively improvised.

### G. Infrastructure: Docker & Docker Compose
- **Why Selected**:
  - **Deterministic Environments**: Bundles the backend, frontend, PostgreSQL database, and native OCR dependencies into isolated, reproducible containers.
  - **Single-Command Setup**: A single `docker compose up --build` command provisions all database tables, networking, and application servers with zero manual configuration.

---

## 2. Architectural Trade-offs & Decisions

| Decision | Trade-off | Rationale |
| :--- | :--- | :--- |
| **Monorepo Structure** | Larger single repository | Ensures unified versioning, atomic integration testing, and simple single-clone onboarding. |
| **Client-Side File Validation + Server-Side Magic Byte Check** | Redundant validation logic | Client-side validation gives instant user feedback; server-side signature validation ensures untrusted uploads cannot bypass security. |
| **JSONB for Clinical Report** | Relational queries inside report require JSON operators | Clinical reports vary widely in depth and medical specialty; rigid relational schemas for every sub-concept would require dozens of join tables. |
| **Synchronous HTTP Pipeline with Stage Animation** | Request latency (3-15s for full OCR+LLM) | Eliminates the operational complexity of Celery/Redis message brokers while providing a fluid, animated stage tracker for end users. |

---

## 3. Maintainability & Code Organization

The application enforces a strict separation of concerns across layered modules:
```
backend/app/
├── api/          # Route handlers & HTTP responses (no business logic)
├── services/     # Pure business logic (DocumentProcessor, AIService, ReportService)
├── models/       # Database entities & table schemas
├── schemas/      # Input/output validation & DTOs
├── prompts/      # System & task prompts isolated from code
└── utils/        # Reusable helpers (logging, file handling, validation)
```
- **Type Hinting**: 100% of Python functions use type annotations.
- **Pydantic v2**: Reusable serialization and validation with `from_attributes=True` and `SettingsConfigDict`.
- **Reusable React Components**: Clean single-responsibility UI elements (`ReportSummary`, `ReportCard`, `StatusBadge`).

---

## 4. Security Considerations

1. **Defense-in-Depth File Validation**: Uploads are checked by file extension, MIME type, and binary magic bytes (`%PDF-`, `\x89PNG`, `\xff\xd8`).
2. **Safe Temporary File Contexts**: Uploaded files processed by external utilities are written to isolated temporary files with guaranteed deletion in `finally` blocks.
3. **No Execution of Uploaded Files**: Uploads are never stored in publicly executable directories.
4. **Secret Masking**: Backend logger implements a regex filter masking API keys and credentials in log streams.
5. **No Client-Side Secrets**: All LLM credentials reside strictly on the server; the frontend communicates exclusively via authenticated REST endpoints.
6. **Synthetic Data Boundaries**: Fictional patient data protects against accidental PHI/PII leakage in test and demo environments.
