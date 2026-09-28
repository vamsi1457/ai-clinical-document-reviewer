import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db
from app.schemas.report import StructuredClinicalReport, PatientInformation, DiagnosisItem, SymptomItem, VitalSigns, AllergyItem

# Setup in-memory SQLite database for testing
TEST_SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    TEST_SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

MOCK_REPORT = StructuredClinicalReport(
    report_summary="Synthetic outpatient encounter for 45-year-old male presenting with fever and cough.",
    patient_information=PatientInformation(name="John Carter", age="45", gender="Male"),
    symptoms=[SymptomItem(symptom="Fever", duration="2 days", severity="Moderate")],
    diagnoses=[DiagnosisItem(condition="Acute Upper Respiratory Tract Infection", status="documented")],
    medications=[],
    vitals=VitalSigns(temperature="38.5 C", heart_rate="92 bpm", blood_pressure="130/85 mmHg"),
    allergies=[AllergyItem(allergy="Not documented", reaction="Not documented")],
    clinical_observations=["Posterior pharynx mildly erythematous"],
    clinical_concerns=["Febrile state requires monitoring"],
    missing_information=["COVID swab result"],
    potential_inconsistencies=[],
    requires_review=["Verify temperature resolution"]
)


def test_create_analysis_text_success():
    """POST /api/analyses with text creates DB record and returns structured report."""
    with patch("app.services.ai_service.ai_service.analyze_clinical_document", return_value=MOCK_REPORT):
        payload = {"text": "Patient John Carter, 45M, presents with fever and cough for two days. Temp: 38.5 C."}
        response = client.post("/api/analyses", json=payload)
        
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert data["data"]["status"] == "COMPLETED"
        assert data["data"]["input_type"] == "text"
        assert "fever and cough" in data["data"]["report_summary"]
        assert data["data"]["structured_report"]["patient_information"]["name"] == "John Carter"
        assert data["data"]["structured_report"]["vitals"]["temperature"] == "38.5 C"


def test_create_analysis_empty_input_validation():
    """POST /api/analyses with empty text returns validation error."""
    payload = {"text": ""}
    response = client.post("/api/analyses", json=payload)
    
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "VALIDATION_ERROR"
    assert "Please enter clinical text before submitting" in data["error"]["message"]


def test_list_analyses_and_details_workflow():
    """Verify list and detail endpoints after inserting a report."""
    with patch("app.services.ai_service.ai_service.analyze_clinical_document", return_value=MOCK_REPORT):
        # 1. Create analysis
        post_res = client.post("/api/analyses", json={"text": "Clinical documentation for testing history."})
        analysis_id = post_res.json()["data"]["id"]

        # 2. List analyses
        list_res = client.get("/api/analyses")
        assert list_res.status_code == 200
        list_data = list_res.json()
        assert list_data["success"] is True
        assert len(list_data["data"]) >= 1
        assert any(item["id"] == analysis_id for item in list_data["data"])

        # 3. Get analysis by ID
        detail_res = client.get(f"/api/analyses/{analysis_id}")
        assert detail_res.status_code == 200
        detail_data = detail_res.json()
        assert detail_data["success"] is True
        assert detail_data["data"]["id"] == analysis_id
        assert detail_data["data"]["status"] == "COMPLETED"

        # 4. Delete analysis
        del_res = client.delete(f"/api/analyses/{analysis_id}")
        assert del_res.status_code == 200
        assert del_res.json()["success"] is True

        # 5. Verify deletion
        not_found_res = client.get(f"/api/analyses/{analysis_id}")
        assert not_found_res.json()["success"] is False
        assert not_found_res.json()["error"]["code"] == "NOT_FOUND"


def test_get_nonexistent_analysis_returns_404():
    """GET /api/analyses/{id} with unknown ID returns NOT_FOUND."""
    res = client.get("/api/analyses/nonexistent-id-0000")
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is False
    assert data["error"]["code"] == "NOT_FOUND"
