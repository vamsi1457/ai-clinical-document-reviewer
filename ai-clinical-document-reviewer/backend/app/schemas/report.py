from typing import List, Optional
from pydantic import BaseModel, Field


class PatientInformation(BaseModel):
    name: str = Field(default="Not provided", description="Patient name if explicitly mentioned")
    age: str = Field(default="Not provided", description="Patient age if explicitly mentioned")
    gender: str = Field(default="Not provided", description="Patient gender if explicitly mentioned")
    dob: str = Field(default="Not provided", description="Date of birth if explicitly present")
    mrn: str = Field(default="Not provided", description="Medical Record Number if present")
    other_demographics: str = Field(default="Not provided", description="Any other demographic data explicitly present")


class SymptomItem(BaseModel):
    symptom: str = Field(description="Documented symptom name")
    duration: str = Field(default="Not documented", description="Duration of symptom if stated")
    severity: str = Field(default="Not documented", description="Severity (e.g. mild, severe) if stated")
    notes: str = Field(default="Not documented", description="Any additional context explicitly mentioned")


class DiagnosisItem(BaseModel):
    condition: str = Field(description="Documented medical condition or diagnosis")
    status: str = Field(
        default="documented",
        description="Status: 'documented' (confirmed/historical) or 'suspected' or 'uncertain'"
    )
    notes: str = Field(default="Not documented", description="Contextual notes on condition")


class MedicationItem(BaseModel):
    medication: str = Field(description="Medication name")
    dosage: str = Field(default="Not documented", description="Dosage (e.g. 500 mg)")
    frequency: str = Field(default="Not documented", description="Frequency (e.g. twice daily)")
    route: str = Field(default="Not documented", description="Route (e.g. oral, IV)")
    notes: str = Field(default="Not documented", description="Additional medication notes")


class VitalSigns(BaseModel):
    blood_pressure: str = Field(default="Not documented", description="Blood pressure reading")
    heart_rate: str = Field(default="Not documented", description="Heart rate / pulse in bpm")
    temperature: str = Field(default="Not documented", description="Body temperature")
    respiratory_rate: str = Field(default="Not documented", description="Respiratory rate")
    oxygen_saturation: str = Field(default="Not documented", description="Oxygen saturation (SpO2)")
    weight: str = Field(default="Not documented", description="Patient weight")
    other_vitals: str = Field(default="Not documented", description="Any other vitals present")


class AllergyItem(BaseModel):
    allergy: str = Field(description="Allergen or substance")
    reaction: str = Field(default="Not documented", description="Allergic reaction description")


class StructuredClinicalReport(BaseModel):
    report_summary: str = Field(
        description="High-level synthesized summary of primary clinical concerns, diagnoses, medications, and review items"
    )
    patient_information: PatientInformation = Field(default_factory=PatientInformation)
    symptoms: List[SymptomItem] = Field(default_factory=list)
    diagnoses: List[DiagnosisItem] = Field(default_factory=list)
    medications: List[MedicationItem] = Field(default_factory=list)
    vitals: VitalSigns = Field(default_factory=VitalSigns)
    allergies: List[AllergyItem] = Field(default_factory=list)
    clinical_observations: List[str] = Field(default_factory=list)
    clinical_concerns: List[str] = Field(default_factory=list)
    missing_information: List[str] = Field(default_factory=list)
    potential_inconsistencies: List[str] = Field(default_factory=list)
    requires_review: List[str] = Field(default_factory=list)
