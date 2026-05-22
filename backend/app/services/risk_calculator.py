"""
Readmission Risk Calculator

Implements rule-based risk scoring algorithm using clinical data from FHIR resources.
Follows the Single Responsibility Principle (SRP) and Open/Closed Principle (OCP).
"""

from typing import List, Dict, Any
from datetime import datetime, timedelta
from app.models.patient import RiskAssessment, RiskFactor, RiskLevel
from app.core.config import settings


class RiskCalculator:
    """
    Hospital Readmission Risk Calculator
    
    Calculates 30-day readmission risk based on multiple clinical factors:
    - Recent admission history
    - High-risk chronic conditions
    - Polypharmacy (multiple medications)
    - Age factor
    - Missed follow-up appointments
    - Abnormal vital signs
    """
    
    # High-risk condition codes (simplified for MVP)
    HIGH_RISK_CONDITIONS = {
        "I50": "Heart Failure",
        "J44": "COPD",
        "E11": "Type 2 Diabetes",
        "I25": "Chronic Ischemic Heart Disease",
        "N18": "Chronic Kidney Disease",
        "I10": "Hypertension (complicated)"
    }
    
    # Vital sign normal ranges
    VITAL_RANGES = {
        "8867-4": {"min": 60, "max": 100, "name": "Heart Rate"},  # bpm
        "8480-6": {"min": 90, "max": 140, "name": "Systolic BP"},  # mmHg
        "8462-4": {"min": 60, "max": 90, "name": "Diastolic BP"},  # mmHg
        "8310-5": {"min": 36.1, "max": 37.5, "name": "Body Temperature"},  # Celsius
        "9279-1": {"min": 12, "max": 20, "name": "Respiratory Rate"}  # breaths/min
    }
    
    def __init__(self):
        self.weights = {
            "recent_admissions": settings.WEIGHT_RECENT_ADMISSIONS,
            "high_risk_conditions": settings.WEIGHT_HIGH_RISK_CONDITIONS,
            "polypharmacy": settings.WEIGHT_POLYPHARMACY,
            "age_factor": settings.WEIGHT_AGE_FACTOR,
            "missed_followups": settings.WEIGHT_MISSED_FOLLOWUPS,
            "abnormal_vitals": settings.WEIGHT_ABNORMAL_VITALS
        }
    
    def calculate_risk(
        self,
        patient_id: str,
        patient_age: int,
        encounters: List[Dict[str, Any]],
        conditions: List[Dict[str, Any]],
        medications: List[Dict[str, Any]],
        observations: List[Dict[str, Any]]
    ) -> RiskAssessment:
        """
        Calculate comprehensive readmission risk score
        
        Args:
            patient_id: FHIR Patient ID
            patient_age: Patient age in years
            encounters: List of Encounter resources
            conditions: List of Condition resources
            medications: List of MedicationRequest resources
            observations: List of Observation resources
            
        Returns:
            RiskAssessment with detailed risk breakdown
        """
        risk_factors = []
        
        # Factor 1: Recent Admissions (last 180 days)
        recent_admissions_score = self._calculate_recent_admissions_score(encounters)
        risk_factors.append(RiskFactor(
            name="Recent Admissions",
            value=recent_admissions_score,
            weight=self.weights["recent_admissions"],
            description=f"Patient has {len([e for e in encounters if self._is_recent_encounter(e)])} admissions in last 6 months"
        ))
        
        # Factor 2: High-Risk Chronic Conditions
        high_risk_conditions_score = self._calculate_high_risk_conditions_score(conditions)
        risk_factors.append(RiskFactor(
            name="High-Risk Conditions",
            value=high_risk_conditions_score,
            weight=self.weights["high_risk_conditions"],
            description=f"Patient has {len([c for c in conditions if self._is_high_risk_condition(c)])} high-risk chronic conditions"
        ))
        
        # Factor 3: Polypharmacy
        polypharmacy_score = self._calculate_polypharmacy_score(medications)
        risk_factors.append(RiskFactor(
            name="Polypharmacy",
            value=polypharmacy_score,
            weight=self.weights["polypharmacy"],
            description=f"Patient is taking {len(medications)} active medications"
        ))
        
        # Factor 4: Age Factor
        age_score = self._calculate_age_score(patient_age)
        risk_factors.append(RiskFactor(
            name="Age Factor",
            value=age_score,
            weight=self.weights["age_factor"],
            description=f"Patient age: {patient_age} years"
        ))
        
        # Factor 5: Missed Follow-ups (inferred from encounter gaps)
        missed_followups_score = self._calculate_missed_followups_score(encounters)
        risk_factors.append(RiskFactor(
            name="Follow-up Adherence",
            value=missed_followups_score,
            weight=self.weights["missed_followups"],
            description="Assessment of follow-up appointment adherence"
        ))
        
        # Factor 6: Abnormal Vital Signs
        abnormal_vitals_score = self._calculate_abnormal_vitals_score(observations)
        risk_factors.append(RiskFactor(
            name="Abnormal Vital Signs",
            value=abnormal_vitals_score,
            weight=self.weights["abnormal_vitals"],
            description=f"Recent vital signs assessment"
        ))
        
        # Calculate weighted risk score
        total_score = sum(factor.value * factor.weight for factor in risk_factors)
        
        # Determine risk level
        risk_level = self._determine_risk_level(total_score)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(risk_level, risk_factors, conditions)
        
        return RiskAssessment(
            patient_id=patient_id,
            risk_score=round(total_score, 3),
            risk_level=risk_level,
            risk_factors=risk_factors,
            recommendations=recommendations
        )
    
    def _is_recent_encounter(self, encounter: Dict[str, Any], days: int = 180) -> bool:
        """Check if encounter occurred within specified days"""
        try:
            period = encounter.get("period", {})
            start_date = period.get("start")
            if start_date:
                enc_date = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
                cutoff = datetime.now(enc_date.tzinfo) - timedelta(days=days)
                return enc_date >= cutoff
        except Exception:
            pass
        return False
    
    def _calculate_recent_admissions_score(self, encounters: List[Dict[str, Any]]) -> float:
        """Score based on number of recent admissions"""
        recent_encounters = [e for e in encounters if self._is_recent_encounter(e)]
        count = len(recent_encounters)
        
        if count >= 3:
            return 1.0  # Very high risk
        elif count == 2:
            return 0.7
        elif count == 1:
            return 0.4
        return 0.1  # Low baseline risk
    
    def _is_high_risk_condition(self, condition: Dict[str, Any]) -> bool:
        """Check if condition is high-risk for readmission"""
        try:
            coding = condition.get("code", {}).get("coding", [])
            for code_obj in coding:
                code = code_obj.get("code", "")
                # Check if code starts with any high-risk condition code
                for risk_code in self.HIGH_RISK_CONDITIONS.keys():
                    if code.startswith(risk_code):
                        return True
        except Exception:
            pass
        return False
    
    def _calculate_high_risk_conditions_score(self, conditions: List[Dict[str, Any]]) -> float:
        """Score based on number and severity of chronic conditions"""
        high_risk_count = sum(1 for c in conditions if self._is_high_risk_condition(c))
        
        if high_risk_count >= 3:
            return 1.0
        elif high_risk_count == 2:
            return 0.7
        elif high_risk_count == 1:
            return 0.4
        return 0.0
    
    def _calculate_polypharmacy_score(self, medications: List[Dict[str, Any]]) -> float:
        """Score based on number of active medications"""
        med_count = len(medications)
        
        if med_count >= 10:
            return 1.0  # Very high polypharmacy
        elif med_count >= 7:
            return 0.7
        elif med_count >= 5:
            return 0.4
        elif med_count >= 3:
            return 0.2
        return 0.0
    
    def _calculate_age_score(self, age: int) -> float:
        """Score based on patient age"""
        if age >= 75:
            return 1.0
        elif age >= 65:
            return 0.6
        elif age >= 55:
            return 0.3
        return 0.0
    
    def _calculate_missed_followups_score(self, encounters: List[Dict[str, Any]]) -> float:
        """
        Score based on encounter patterns
        Large gaps between encounters may indicate missed follow-ups
        """
        recent_encounters = sorted(
            [e for e in encounters if self._is_recent_encounter(e, days=365)],
            key=lambda x: x.get("period", {}).get("start", ""),
            reverse=True
        )
        
        if len(recent_encounters) < 2:
            return 0.5  # Insufficient data, moderate risk
        
        # Check for large gaps (> 90 days) between encounters
        gaps = 0
        for i in range(len(recent_encounters) - 1):
            try:
                date1 = datetime.fromisoformat(
                    recent_encounters[i].get("period", {}).get("start", "").replace("Z", "+00:00")
                )
                date2 = datetime.fromisoformat(
                    recent_encounters[i+1].get("period", {}).get("start", "").replace("Z", "+00:00")
                )
                if (date1 - date2).days > 90:
                    gaps += 1
            except Exception:
                continue
        
        if gaps >= 2:
            return 0.8
        elif gaps == 1:
            return 0.4
        return 0.1
    
    def _calculate_abnormal_vitals_score(self, observations: List[Dict[str, Any]]) -> float:
        """Score based on recent abnormal vital signs"""
        recent_vitals = [o for o in observations if self._is_recent_observation(o, days=30)]
        
        if not recent_vitals:
            return 0.3  # No recent vitals, moderate concern
        
        abnormal_count = 0
        for obs in recent_vitals:
            if self._is_vital_abnormal(obs):
                abnormal_count += 1
        
        abnormal_ratio = abnormal_count / len(recent_vitals) if recent_vitals else 0
        
        if abnormal_ratio >= 0.5:
            return 1.0
        elif abnormal_ratio >= 0.3:
            return 0.6
        elif abnormal_ratio > 0:
            return 0.3
        return 0.0
    
    def _is_recent_observation(self, observation: Dict[str, Any], days: int = 30) -> bool:
        """Check if observation is recent"""
        try:
            effective = observation.get("effectiveDateTime")
            if effective:
                obs_date = datetime.fromisoformat(effective.replace("Z", "+00:00"))
                cutoff = datetime.now(obs_date.tzinfo) - timedelta(days=days)
                return obs_date >= cutoff
        except Exception:
            pass
        return False
    
    def _is_vital_abnormal(self, observation: Dict[str, Any]) -> bool:
        """Check if vital sign is outside normal range"""
        try:
            coding = observation.get("code", {}).get("coding", [])
            for code_obj in coding:
                code = code_obj.get("code", "")
                if code in self.VITAL_RANGES:
                    value_quantity = observation.get("valueQuantity", {})
                    value = value_quantity.get("value")
                    if value:
                        ranges = self.VITAL_RANGES[code]
                        return value < ranges["min"] or value > ranges["max"]
        except Exception:
            pass
        return False
    
    def _determine_risk_level(self, score: float) -> RiskLevel:
        """Determine risk stratification level from score"""
        if score >= settings.HIGH_RISK_THRESHOLD:
            return RiskLevel.HIGH
        elif score >= settings.MODERATE_RISK_THRESHOLD:
            return RiskLevel.MODERATE
        return RiskLevel.LOW
    
    def _generate_recommendations(
        self, 
        risk_level: RiskLevel,
        risk_factors: List[RiskFactor],
        conditions: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate clinical recommendations based on risk assessment"""
        recommendations = []
        
        if risk_level == RiskLevel.HIGH:
            recommendations.append("Schedule follow-up appointment within 7 days of discharge")
            recommendations.append("Consider home health services or transitional care program")
            recommendations.append("Ensure medication reconciliation and patient education")
            recommendations.append("Provide 24/7 phone access to care team")
        elif risk_level == RiskLevel.MODERATE:
            recommendations.append("Schedule follow-up appointment within 14 days of discharge")
            recommendations.append("Conduct thorough medication review and reconciliation")
            recommendations.append("Provide written discharge instructions in plain language")
        else:
            recommendations.append("Schedule follow-up appointment within 30 days")
            recommendations.append("Provide standard discharge instructions")
        
        # Specific recommendations based on risk factors
        for factor in risk_factors:
            if factor.name == "Polypharmacy" and factor.value >= 0.6:
                recommendations.append("Pharmacy consultation for medication management")
            if factor.name == "Abnormal Vital Signs" and factor.value >= 0.6:
                recommendations.append("Close monitoring of vital signs post-discharge")
        
        return list(set(recommendations))  # Remove duplicates


# Singleton instance
risk_calculator = RiskCalculator()
