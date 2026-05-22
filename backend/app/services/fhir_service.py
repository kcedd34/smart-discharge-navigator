"""
FHIR Service - Orchestration Layer

Coordinates FHIR data retrieval, risk calculation, and care plan generation.
Follows the Facade pattern and Dependency Inversion Principle (DIP).
"""

from typing import List, Optional
from datetime import datetime
from app.core.fhir_client import fhir_client
from app.services.risk_calculator import risk_calculator
from app.services.care_plan_generator import care_plan_generator
from app.models.patient import PatientSummary, RiskAssessment, DischargePlan, RiskLevel


class FHIRService:
    """
    FHIR Service - Main orchestration layer
    
    Provides high-level operations for the Smart Discharge Navigator application.
    """
    
    def __init__(self):
        self.fhir_client = fhir_client
        self.risk_calculator = risk_calculator
        self.care_plan_generator = care_plan_generator
    
    async def get_all_patients_summary(self) -> List[PatientSummary]:
        """
        Get summary of all patients with risk assessments
        
        Returns:
            List of PatientSummary objects
        """
        # Fetch all patients
        patients = await self.fhir_client.search_resources("Patient", {"_count": "100"})
        
        summaries = []
        for patient in patients:
            try:
                summary = await self.get_patient_summary(patient["id"])
                if summary:
                    summaries.append(summary)
            except Exception as e:
                print(f"Error processing patient {patient.get('id')}: {str(e)}")
                continue
        
        # Sort by risk score (highest first)
        summaries.sort(key=lambda x: x.risk_score, reverse=True)
        
        return summaries
    
    async def get_patient_summary(self, patient_id: str) -> Optional[PatientSummary]:
        """
        Get patient summary with current risk assessment
        
        Args:
            patient_id: FHIR Patient ID
            
        Returns:
            PatientSummary or None if patient not found
        """
        # Fetch patient resource
        patient = await self.fhir_client.get_resource("Patient", patient_id)
        if not patient:
            return None
        
        # Extract patient demographics
        name = self._extract_patient_name(patient)
        age = self._calculate_age(patient.get("birthDate"))
        gender = patient.get("gender", "unknown")
        
        # Fetch clinical data
        encounters = await self.fhir_client.get_patient_encounters(patient_id)
        conditions = await self.fhir_client.get_patient_conditions(patient_id)
        medications = await self.fhir_client.get_patient_medications(patient_id)
        observations = await self.fhir_client.get_patient_observations(patient_id)
        
        # Calculate risk assessment
        risk_assessment = self.risk_calculator.calculate_risk(
            patient_id=patient_id,
            patient_age=age,
            encounters=encounters,
            conditions=conditions,
            medications=medications,
            observations=observations
        )
        
        # Get last encounter date
        last_encounter_date = self._get_last_encounter_date(encounters)
        
        # Check if discharge plan exists
        care_plans = await self.fhir_client.search_resources(
            "CarePlan",
            {"patient": patient_id, "_sort": "-date", "_count": "1"}
        )
        has_discharge_plan = len(care_plans) > 0
        
        return PatientSummary(
            id=patient_id,
            name=name,
            age=age,
            gender=gender,
            risk_score=risk_assessment.risk_score,
            risk_level=risk_assessment.risk_level,
            recent_admissions_count=len([e for e in encounters if self._is_recent(e)]),
            active_conditions_count=len(conditions),
            last_encounter_date=last_encounter_date,
            has_discharge_plan=has_discharge_plan
        )
    
    async def get_patient_risk_assessment(self, patient_id: str) -> Optional[RiskAssessment]:
        """
        Get detailed risk assessment for a patient
        
        Args:
            patient_id: FHIR Patient ID
            
        Returns:
            RiskAssessment or None if patient not found
        """
        patient = await self.fhir_client.get_resource("Patient", patient_id)
        if not patient:
            return None
        
        age = self._calculate_age(patient.get("birthDate"))
        
        # Fetch clinical data
        encounters = await self.fhir_client.get_patient_encounters(patient_id)
        conditions = await self.fhir_client.get_patient_conditions(patient_id)
        medications = await self.fhir_client.get_patient_medications(patient_id)
        observations = await self.fhir_client.get_patient_observations(patient_id)
        
        return self.risk_calculator.calculate_risk(
            patient_id=patient_id,
            patient_age=age,
            encounters=encounters,
            conditions=conditions,
            medications=medications,
            observations=observations
        )
    
    async def generate_discharge_plan(self, patient_id: str) -> Optional[DischargePlan]:
        """
        Generate comprehensive discharge plan for a patient
        
        Args:
            patient_id: FHIR Patient ID
            
        Returns:
            DischargePlan or None if patient not found
        """
        patient = await self.fhir_client.get_resource("Patient", patient_id)
        if not patient:
            return None
        
        name = self._extract_patient_name(patient)
        
        # Get risk assessment
        risk_assessment = await self.get_patient_risk_assessment(patient_id)
        if not risk_assessment:
            return None
        
        # Get medications
        medications = await self.fhir_client.get_patient_medications(patient_id)
        
        # Generate discharge plan
        discharge_plan = await self.care_plan_generator.generate_discharge_plan(
            patient_id=patient_id,
            patient_name=name,
            risk_assessment=risk_assessment,
            medications=medications
        )
        
        return discharge_plan
    
    def _extract_patient_name(self, patient: dict) -> str:
        """Extract formatted patient name from Patient resource"""
        try:
            name_list = patient.get("name", [])
            if name_list:
                name_obj = name_list[0]
                given = " ".join(name_obj.get("given", []))
                family = name_obj.get("family", "")
                return f"{given} {family}".strip() or "Unknown Patient"
        except Exception:
            pass
        return "Unknown Patient"
    
    def _calculate_age(self, birth_date: str) -> int:
        """Calculate age from birth date string"""
        if not birth_date:
            return 0
        
        try:
            birth = datetime.fromisoformat(birth_date)
            today = datetime.now()
            age = today.year - birth.year
            if today.month < birth.month or (today.month == birth.month and today.day < birth.day):
                age -= 1
            return max(0, age)
        except Exception:
            return 0
    
    def _is_recent(self, encounter: dict, days: int = 180) -> bool:
        """Check if encounter is recent"""
        try:
            from datetime import timedelta
            period = encounter.get("period", {})
            start_date = period.get("start")
            if start_date:
                enc_date = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
                cutoff = datetime.now(enc_date.tzinfo) - timedelta(days=days)
                return enc_date >= cutoff
        except Exception:
            pass
        return False
    
    def _get_last_encounter_date(self, encounters: list) -> Optional[datetime]:
        """Get date of most recent encounter"""
        if not encounters:
            return None
        
        try:
            recent = sorted(
                encounters,
                key=lambda x: x.get("period", {}).get("start", ""),
                reverse=True
            )
            if recent:
                start_date = recent[0].get("period", {}).get("start")
                if start_date:
                    return datetime.fromisoformat(start_date.replace("Z", "+00:00"))
        except Exception:
            pass
        return None


# Singleton instance
fhir_service = FHIRService()
