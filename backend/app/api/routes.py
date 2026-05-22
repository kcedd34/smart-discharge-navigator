"""
API Routes

REST API endpoints for Smart Discharge Navigator.
Includes both rule-based and AI Agent endpoints.
Follows RESTful conventions and proper error handling.
"""

import logging
from fastapi import APIRouter, HTTPException, status
from typing import List
from app.models.patient import (
    PatientSummary, RiskAssessment, DischargePlan,
    AIAnalysis, ChatRequest, ChatResponse,
    PatientCompareRequest, AIComparisonResult,
    PatientRoleSummary, NLToSQLRequest, NLToSQLResult
)
from app.core.config import settings
from app.services.fhir_service import fhir_service
from app.services.ai_agent_service import ai_agent_service
from app.services.fhir_sql_analytics import fhir_sql_analytics

logger = logging.getLogger("api")

router = APIRouter()


@router.get("/health", tags=["System"])
async def health_check():
    """
    Health check endpoint
    
    Returns:
        System health status
    """
    return {
        "status": "healthy",
        "service": "Smart Discharge Navigator",
        "version": "1.0.0"
    }


@router.get("/patients", response_model=List[PatientSummary], tags=["Patients"])
async def get_all_patients():
    """
    Get all patients with risk assessments
    
    Returns:
        List of patient summaries sorted by risk score (highest first)
    """
    try:
        summaries = await fhir_service.get_all_patients_summary()
        return summaries
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching patients: {str(e)}"
        )


@router.get("/patients/{patient_id}", response_model=PatientSummary, tags=["Patients"])
async def get_patient(patient_id: str):
    """
    Get patient summary by ID
    
    Args:
        patient_id: FHIR Patient ID
        
    Returns:
        Patient summary with risk assessment
    """
    summary = await fhir_service.get_patient_summary(patient_id)
    
    if not summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient {patient_id} not found"
        )
    
    return summary


@router.get(
    "/patients/{patient_id}/risk-assessment",
    response_model=RiskAssessment,
    tags=["Risk Assessment"]
)
async def get_patient_risk_assessment(patient_id: str):
    """
    Get detailed risk assessment for a patient
    
    Args:
        patient_id: FHIR Patient ID
        
    Returns:
        Detailed risk assessment with factor breakdown
    """
    risk_assessment = await fhir_service.get_patient_risk_assessment(patient_id)
    
    if not risk_assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient {patient_id} not found"
        )
    
    return risk_assessment


@router.post(
    "/patients/{patient_id}/discharge-plan",
    response_model=DischargePlan,
    tags=["Discharge Planning"],
    status_code=status.HTTP_201_CREATED
)
async def generate_discharge_plan(patient_id: str):
    """
    Generate discharge plan for a patient
    
    Creates FHIR CarePlan and Task resources based on risk assessment.
    
    Args:
        patient_id: FHIR Patient ID
        
    Returns:
        Generated discharge plan with tasks and instructions
    """
    discharge_plan = await fhir_service.generate_discharge_plan(patient_id)
    
    if not discharge_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient {patient_id} not found"
        )
    
    return discharge_plan


@router.get("/statistics", tags=["Analytics"])
async def get_statistics():
    """
    Get system-wide statistics
    
    Returns:
        Dashboard statistics including risk distribution
    """
    try:
        summaries = await fhir_service.get_all_patients_summary()
        
        total_patients = len(summaries)
        high_risk_count = sum(1 for s in summaries if s.risk_level == "HIGH")
        moderate_risk_count = sum(1 for s in summaries if s.risk_level == "MODERATE")
        low_risk_count = sum(1 for s in summaries if s.risk_level == "LOW")
        
        with_discharge_plan = sum(1 for s in summaries if s.has_discharge_plan)
        
        avg_risk_score = sum(s.risk_score for s in summaries) / total_patients if total_patients > 0 else 0
        
        return {
            "total_patients": total_patients,
            "risk_distribution": {
                "high": high_risk_count,
                "moderate": moderate_risk_count,
                "low": low_risk_count
            },
            "average_risk_score": round(avg_risk_score, 3),
            "patients_with_discharge_plan": with_discharge_plan,
            "discharge_plan_coverage": round(with_discharge_plan / total_patients * 100, 1) if total_patients > 0 else 0
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching statistics: {str(e)}"
        )


# ──────────────────────────────────────────────
# AI Agent Endpoints
# ──────────────────────────────────────────────

@router.get("/ai/status", tags=["AI Agent"])
async def ai_agent_status():
    """
    Check AI Agent availability and configuration
    
    Returns:
        AI Agent status including model info and availability
    """
    return {
        "ai_available": ai_agent_service.is_ai_available,
        "model": settings.AI_MODEL if ai_agent_service.is_ai_available else "fallback-rule-based",
        "features": {
            "chat": True,
            "patient_analysis": True,
            "discharge_planning": True,
            "patient_comparison": True
        },
        "mode": "ai-powered" if ai_agent_service.is_ai_available else "rule-based-fallback"
    }


@router.post("/ai/chat", response_model=ChatResponse, tags=["AI Agent"])
async def chat_with_ai_agent(request: ChatRequest):
    """
    Conversational interface to the AI Clinical Agent
    
    Send natural language clinical queries and get AI-powered responses
    grounded in FHIR patient data from InterSystems IRIS.
    
    Args:
        request: ChatRequest with message and optional patient context
        
    Returns:
        ChatResponse with AI-generated answer and sources
    """
    try:
        logger.info(f"AI Chat request: '{request.message[:100]}...' patient_id={request.patient_id}")
        response = await ai_agent_service.chat_with_agent(
            query=request.message,
            patient_id=request.patient_id,
            conversation_history=request.conversation_history
        )
        return response
    except Exception as e:
        logger.error(f"AI Chat error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI Agent error: {str(e)}"
        )


@router.get(
    "/patients/{patient_id}/ai-analysis",
    response_model=AIAnalysis,
    tags=["AI Agent"]
)
async def get_ai_patient_analysis(patient_id: str):
    """
    AI-powered patient analysis with LLM reasoning
    
    Combines rule-based scoring with GPT-4 clinical reasoning for
    comprehensive readmission risk assessment.
    
    Args:
        patient_id: FHIR Patient ID
        
    Returns:
        AIAnalysis with insights, reasoning steps, and recommendations
    """
    try:
        logger.info(f"AI Analysis request for patient {patient_id}")
        analysis = await ai_agent_service.analyze_patient_with_ai(patient_id)
        return analysis
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"AI Analysis error for patient {patient_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI Analysis error: {str(e)}"
        )


@router.post("/ai/compare-patients", response_model=AIComparisonResult, tags=["AI Agent"])
async def compare_patients_with_ai(request: PatientCompareRequest):
    """
    Compare multiple patients for triage prioritization using AI
    
    Uses LLM to analyze and rank patients by readmission risk,
    identifying common and unique risk factors.
    
    Args:
        request: PatientCompareRequest with list of patient IDs
        
    Returns:
        AIComparisonResult with ranking and insights
    """
    try:
        logger.info(f"AI Compare request for patients: {request.patient_ids}")
        result = await ai_agent_service.compare_patients(request.patient_ids)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"AI Compare error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI Comparison error: {str(e)}"
        )


@router.post(
    "/patients/{patient_id}/ai-discharge-plan",
    tags=["AI Agent"]
)
async def generate_ai_discharge_plan(patient_id: str):
    """
    Generate AI-powered personalized discharge plan
    
    Uses GPT-4 with FHIR patient data to create a comprehensive,
    personalized discharge plan with specific recommendations.
    
    Args:
        patient_id: FHIR Patient ID
        
    Returns:
        AI-generated discharge plan in markdown format
    """
    try:
        logger.info(f"AI Discharge Plan request for patient {patient_id}")
        plan = await ai_agent_service.generate_ai_discharge_plan(patient_id)
        return {
            "patient_id": patient_id,
            "discharge_plan": plan,
            "ai_powered": ai_agent_service.is_ai_available,
            "model_used": settings.AI_MODEL if ai_agent_service.is_ai_available else "rule-based-fallback"
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"AI Discharge Plan error for patient {patient_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI Discharge Plan error: {str(e)}"
        )


# ──────────────────────────────────────────────
# FHIR SQL Builder Endpoints
# (InterSystems Platform Feature)
# ──────────────────────────────────────────────

@router.get("/analytics/sql-stats", tags=["FHIR SQL Builder"])
async def get_sql_analytics():
    """
    Population analytics via FHIR SQL Builder

    Demonstrates InterSystems IRIS FHIR SQL Builder by executing SQL queries
    against FHIR resource projections. This is a key platform feature that
    enables server-side analytics on FHIR data using standard SQL.

    Queries executed:
    1. Patient demographics aggregation (COUNT, AVG on Patient table)
    2. Gender distribution (GROUP BY on Patient)
    3. Encounter frequency analysis (Patient ⟷ Encounter JOIN)
    4. Condition prevalence (aggregation with nested FHIR coding elements)
    5. High-risk population identification (3-table JOIN: Patient, Encounter, Condition)
    6. Medication utilization statistics (MedicationRequest aggregation)

    Returns:
        SQL query results with metadata showing FHIR SQL Builder usage
    """
    try:
        logger.info("Executing FHIR SQL Builder population analytics")
        analytics = await fhir_sql_analytics.get_population_analytics()
        return analytics
    except Exception as e:
        logger.error(f"FHIR SQL Builder analytics error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"FHIR SQL Builder error: {str(e)}"
        )


@router.get("/analytics/readmission-sql", tags=["FHIR SQL Builder"])
async def get_readmission_sql_stats():
    """
    Readmission-specific analytics via FHIR SQL Builder

    Uses SQL queries against FHIR SQL Builder projections to compute
    readmission risk indicators at the database level. Demonstrates
    how SQL Builder can support the contest task (#9: Hospital
    Readmission Risk Workbench) with server-side analytics.

    Queries:
    1. Readmission candidates: Patient-Encounter JOIN with CASE-based risk stratification
    2. Polypharmacy analysis: MedicationRequest aggregation with risk classification

    Returns:
        Readmission-focused SQL analytics results
    """
    try:
        logger.info("Executing FHIR SQL Builder readmission analytics")
        stats = await fhir_sql_analytics.get_readmission_risk_sql_stats()
        return stats
    except Exception as e:
        logger.error(f"FHIR SQL Builder readmission analytics error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"FHIR SQL Builder error: {str(e)}"
        )


@router.get("/analytics/sql-builder-info", tags=["FHIR SQL Builder"])
async def get_sql_builder_info():
    """
    FHIR SQL Builder configuration and capabilities info

    Returns information about the FHIR SQL Builder integration,
    including available tables, connection details, and supported
    SQL operations. Useful for understanding the platform feature.

    Returns:
        FHIR SQL Builder configuration and capability details
    """
    try:
        info = await fhir_sql_analytics.get_fhir_sql_builder_info()
        return info
    except Exception as e:
        logger.error(f"FHIR SQL Builder info error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"FHIR SQL Builder info error: {str(e)}"
        )


# ──────────────────────────────────────────────
# Role-Based Patient Summary Endpoint
# (Contest Task #1 — Smart Patient Summary)
# ──────────────────────────────────────────────

@router.get(
    "/patients/{patient_id}/summary",
    response_model=PatientRoleSummary,
    tags=["AI Agent"]
)
async def get_patient_role_summary(
    patient_id: str,
    role: str = "doctor"
):
    """
    Role-adapted AI patient summary

    Generates a LLM-powered narrative tailored to the target audience:

    - **doctor / ed_doctor**: Full clinical detail, ICD-10 codes, vitals, allergy-drug interactions
    - **care_manager**: Care gaps, follow-up adherence, social determinants, care coordination
    - **patient**: Plain language (8th grade), what conditions mean, daily instructions, warning signs
    - **caregiver / family**: Home-care guidance, medication safety, when to call the doctor

    Demonstrates Contest Task #1 (Smart Patient Summary) with FHIR data from IRIS.

    Args:
        patient_id: FHIR Patient ID
        role: Target audience — doctor | ed_doctor | patient | caregiver | family | care_manager

    Returns:
        PatientRoleSummary with structured sections, key alerts, and next actions
    """
    try:
        logger.info(f"Role summary request: patient={patient_id} role={role}")
        summary = await ai_agent_service.generate_patient_summary_by_role(patient_id, role)
        return summary
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Role summary error for patient {patient_id} role={role}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Role summary error: {str(e)}"
        )


# ──────────────────────────────────────────────
# Natural Language → SQL Endpoint
# (Contest Task #8 — NL to FHIR Query Explorer)
# ──────────────────────────────────────────────

@router.post(
    "/ai/nl-to-sql",
    response_model=NLToSQLResult,
    tags=["FHIR SQL Builder", "AI Agent"]
)
async def natural_language_to_sql(request: NLToSQLRequest):
    """
    Natural Language to SQL translation via FHIR SQL Builder

    Uses GPT-4o to translate a plain-English clinical question into a SQL query
    targeting InterSystems IRIS FHIR SQL Builder projections, then executes it.

    The response includes the **generated SQL** so users can inspect, learn,
    and build on the translation — directly demonstrating NL→SQL transparency.

    Example queries:
    - "How many patients have diabetes and more than 2 hospital encounters?"
    - "List all patients with a Penicillin allergy who are on active medications"
    - "What are the most common conditions among high-risk patients?"
    - "Show me patients older than 70 with chronic kidney disease"

    Demonstrates Contest Task #8 (Natural Language to FHIR Query Explorer).

    Args:
        request: NLToSQLRequest with natural language query and execute flag

    Returns:
        NLToSQLResult with generated SQL, execution results, and explanation
    """
    try:
        logger.info(f"NL-to-SQL request: '{request.query[:100]}'")
        result = await fhir_sql_analytics.translate_nl_to_sql(
            nl_query=request.query,
            execute=request.execute
        )
        return NLToSQLResult(
            nl_query=result["nl_query"],
            generated_sql=result["generated_sql"],
            schema_used=result["schema_used"],
            results=result.get("results"),
            explanation=result["explanation"],
            executed=result["executed"],
            ai_powered=result["ai_powered"],
            model_used=result["model_used"]
        )
    except Exception as e:
        logger.error(f"NL-to-SQL error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"NL-to-SQL error: {str(e)}"
        )
