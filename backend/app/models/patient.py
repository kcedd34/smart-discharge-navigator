"""
Patient Domain Models

Pydantic models for type-safe data validation and serialization.
Follows the Single Responsibility Principle (SRP) and Interface Segregation Principle (ISP).
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum


class RiskLevel(str, Enum):
    """Risk stratification levels"""
    HIGH = "HIGH"
    MODERATE = "MODERATE"
    LOW = "LOW"


class PatientSummary(BaseModel):
    """
    Patient Summary for Dashboard Display
    
    Contains essential patient information and current risk status.
    """
    id: str = Field(..., description="FHIR Patient ID")
    name: str = Field(..., description="Patient full name")
    age: int = Field(..., description="Patient age in years")
    gender: str = Field(..., description="Patient gender")
    risk_score: float = Field(..., ge=0.0, le=1.0, description="Readmission risk score (0-1)")
    risk_level: RiskLevel = Field(..., description="Risk stratification level")
    recent_admissions_count: int = Field(default=0, description="Admissions in last 180 days")
    active_conditions_count: int = Field(default=0, description="Number of active conditions")
    last_encounter_date: Optional[datetime] = Field(None, description="Date of last encounter")
    has_discharge_plan: bool = Field(default=False, description="Whether discharge plan exists")


class RiskFactor(BaseModel):
    """Individual risk factor with weight and score"""
    name: str = Field(..., description="Risk factor name")
    value: float = Field(..., ge=0.0, le=1.0, description="Factor score (0-1)")
    weight: float = Field(..., description="Factor weight in overall score")
    description: str = Field(..., description="Human-readable explanation")


class RiskAssessment(BaseModel):
    """
    Detailed Risk Assessment Result
    
    Contains risk score, level, and breakdown of contributing factors.
    """
    patient_id: str = Field(..., description="FHIR Patient ID")
    risk_score: float = Field(..., ge=0.0, le=1.0, description="Overall risk score")
    risk_level: RiskLevel = Field(..., description="Risk stratification level")
    risk_factors: List[RiskFactor] = Field(default_factory=list, description="Contributing factors")
    assessment_date: datetime = Field(default_factory=datetime.utcnow)
    recommendations: List[str] = Field(default_factory=list, description="Clinical recommendations")


class DischargePlanTask(BaseModel):
    """Single task in discharge plan"""
    title: str = Field(..., description="Task title")
    description: str = Field(..., description="Task description")
    priority: str = Field(..., description="Task priority (high, medium, low)")
    due_date: Optional[datetime] = Field(None, description="Task due date")
    status: str = Field(default="planned", description="Task status")


class DischargePlan(BaseModel):
    """
    Comprehensive Discharge Plan
    
    Contains care plan details, tasks, and follow-up instructions.
    """
    patient_id: str = Field(..., description="FHIR Patient ID")
    care_plan_id: Optional[str] = Field(None, description="FHIR CarePlan resource ID")
    title: str = Field(..., description="Care plan title")
    description: str = Field(..., description="Care plan description")
    tasks: List[DischargePlanTask] = Field(default_factory=list, description="Discharge tasks")
    medications: List[str] = Field(default_factory=list, description="Discharge medications")
    follow_up_appointments: List[str] = Field(default_factory=list, description="Follow-up appointments")
    patient_instructions: str = Field(..., description="Plain-language instructions for patient")
    created_date: datetime = Field(default_factory=datetime.utcnow)


class HealthcareCondition(BaseModel):
    """Simplified condition model"""
    code: str = Field(..., description="Condition code")
    display: str = Field(..., description="Condition display name")
    onset_date: Optional[datetime] = Field(None, description="Condition onset date")
    is_chronic: bool = Field(default=False, description="Whether condition is chronic")


class VitalSign(BaseModel):
    """Vital sign observation"""
    code: str = Field(..., description="LOINC code")
    display: str = Field(..., description="Vital sign name")
    value: float = Field(..., description="Measured value")
    unit: str = Field(..., description="Unit of measure")
    date: datetime = Field(..., description="Observation date")
    is_abnormal: bool = Field(default=False, description="Whether value is abnormal")


# ──────────────────────────────────────────────
# AI Agent Models
# ──────────────────────────────────────────────

class AIReasoningStep(BaseModel):
    """Individual reasoning step from the AI Agent"""
    step: int = Field(..., description="Step number")
    action: str = Field(..., description="What the agent analyzed")
    finding: str = Field(..., description="What was found")
    clinical_relevance: str = Field(..., description="Why it matters clinically")


class AIAnalysis(BaseModel):
    """
    AI-Powered Patient Analysis Result

    Contains LLM-generated insights alongside rule-based scores for hybrid assessment.
    """
    patient_id: str = Field(..., description="FHIR Patient ID")
    patient_name: str = Field(default="", description="Patient name")
    ai_risk_level: str = Field(..., description="AI-determined risk level")
    ai_confidence_score: float = Field(..., ge=0.0, le=1.0, description="AI confidence (0-1)")
    rule_based_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Rule-based score for comparison")
    ai_insights: List[str] = Field(default_factory=list, description="Key AI-generated insights")
    reasoning_steps: List[AIReasoningStep] = Field(default_factory=list, description="Step-by-step reasoning")
    recommendations: List[str] = Field(default_factory=list, description="AI-generated recommendations")
    risks_missed_by_rules: List[str] = Field(default_factory=list, description="Risks identified by AI but not by rules")
    analysis_timestamp: datetime = Field(default_factory=datetime.utcnow)
    model_used: str = Field(default="gpt-4", description="LLM model used")


class ChatMessage(BaseModel):
    """Single chat message"""
    role: str = Field(..., description="Message role: user or assistant")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ChatRequest(BaseModel):
    """Request to the AI Agent chat interface"""
    message: str = Field(..., description="User message/query")
    patient_id: Optional[str] = Field(None, description="Optional patient context")
    conversation_history: List[ChatMessage] = Field(default_factory=list, description="Previous messages")


class ChatResponse(BaseModel):
    """Response from the AI Agent chat interface"""
    response: str = Field(..., description="AI Agent response")
    sources: List[str] = Field(default_factory=list, description="FHIR data sources used")
    patient_ids_referenced: List[str] = Field(default_factory=list, description="Patient IDs referenced")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="Response confidence")
    ai_powered: bool = Field(default=True, description="Whether AI was used")


class PatientCompareRequest(BaseModel):
    """Request to compare multiple patients"""
    patient_ids: List[str] = Field(..., min_length=2, description="Patient IDs to compare")


class AIComparisonResult(BaseModel):
    """AI-powered comparison of multiple patients"""
    patient_ids: List[str] = Field(..., description="Compared patient IDs")
    comparison_summary: str = Field(..., description="Natural language comparison summary")
    risk_ranking: List[dict] = Field(default_factory=list, description="Patients ranked by risk")
    common_risk_factors: List[str] = Field(default_factory=list, description="Shared risk factors")
    unique_concerns: dict = Field(default_factory=dict, description="Unique concerns per patient")
    triage_recommendation: str = Field(..., description="Priority triage recommendation")
    ai_powered: bool = Field(default=True)
