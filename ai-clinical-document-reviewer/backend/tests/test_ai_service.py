import pytest
from app.services.ai_service import (
    extract_json_from_text,
    AIService,
    AIServiceUnavailableError,
)
from app.schemas.report import StructuredClinicalReport


def test_extract_json_plain():
    """Extracts valid JSON from raw string."""
    raw = '{"report_summary": "Test summary", "symptoms": []}'
    parsed = extract_json_from_text(raw)
    assert parsed["report_summary"] == "Test summary"
    assert parsed["symptoms"] == []


def test_extract_json_markdown_wrapped():
    """Extracts JSON from markdown fenced code block."""
    raw = """Here is the extracted clinical analysis:
```json
{
  "report_summary": "Fenced summary",
  "patient_information": {"name": "John Doe", "age": "45"}
}
```
Please let me know if further review is required."""
    parsed = extract_json_from_text(raw)
    assert parsed["report_summary"] == "Fenced summary"
    assert parsed["patient_information"]["name"] == "John Doe"


def test_structured_clinical_report_pydantic_validation():
    """Validates complete structured clinical report schema."""
    data = {
        "report_summary": "45-year-old male with fever and cough.",
        "patient_information": {
            "name": "John Carter",
            "age": "45",
            "gender": "Male"
        },
        "symptoms": [
            {"symptom": "Fever", "duration": "2 days", "severity": "Moderate"}
        ],
        "diagnoses": [
            {"condition": "Acute Bronchitis", "status": "suspected", "notes": "Rule out pneumonia"}
        ],
        "medications": [
            {"medication": "Paracetamol", "dosage": "500 mg", "frequency": "twice daily"}
        ],
        "vitals": {
            "temperature": "38.5 C",
            "heart_rate": "92 bpm",
            "blood_pressure": "130/85 mmHg"
        },
        "allergies": [
            {"allergy": "Not documented", "reaction": "Not documented"}
        ],
        "clinical_observations": ["Mild distress", "Pharyngeal erythema"],
        "clinical_concerns": ["Persistent febrile state without antibiotic response"],
        "missing_information": ["COVID-19 swab test result"],
        "potential_inconsistencies": [],
        "requires_review": ["Confirm medication compliance"]
    }

    report = StructuredClinicalReport(**data)
    assert report.report_summary == "45-year-old male with fever and cough."
    assert report.patient_information.name == "John Carter"
    assert report.patient_information.dob == "Not provided"  # Default check
    assert len(report.symptoms) == 1
    assert report.symptoms[0].symptom == "Fever"
    assert report.diagnoses[0].status == "suspected"
    assert report.vitals.temperature == "38.5 C"


def test_ai_service_unconfigured_key_error(monkeypatch):
    """When AI_API_KEY is unset, AI service must raise AIServiceUnavailableError."""
    from app.config import settings
    monkeypatch.setattr(settings, "AI_API_KEY", "")
    service = AIService()
    with pytest.raises(AIServiceUnavailableError, match="AI API key is not configured"):
        service.analyze_clinical_document("Sample text")
