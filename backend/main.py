"""
Smart Discharge Navigator - Main Application

FastAPI application entry point for the Smart Discharge Navigator backend.
InterSystems Programming Contest: AI Agents for FHIR 2026 - Task #9: Hospital Readmission Risk Workbench

Features an AI Agent powered by OpenAI GPT-4 that analyzes FHIR patient data
for clinical reasoning, readmission risk assessment, and discharge planning.
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.routes import router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s"
)
logger = logging.getLogger("main")

# Initialize FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
    Smart Discharge Navigator - AI Agent for Hospital Readmission Risk Assessment & Discharge Planning
    
    An **AI Agent-powered** FHIR application that:
    - 🤖 Uses GPT-4 AI Agent for clinical reasoning over FHIR data
    - 📊 Assesses 30-day hospital readmission risk using hybrid AI + rule-based approach
    - 💬 Provides conversational AI interface for clinical queries
    - 📋 Generates AI-powered personalized discharge plans
    - 🔍 Compares multiple patients for triage prioritization
    - 📦 Creates FHIR CarePlan and Task resources on InterSystems IRIS
    
    Built for InterSystems Programming Contest 2026 - **AI Agents for FHIR**
    
    ## AI Agent Capabilities
    - **Conversational Chat**: Ask natural language questions about patients
    - **AI Analysis**: LLM-powered risk assessment with step-by-step reasoning
    - **Smart Discharge Plans**: AI-generated personalized discharge recommendations
    - **Patient Comparison**: AI triage across multiple patients
    - **Hybrid Approach**: AI enhances rule-based scoring, never replaces it
    
    ## FHIR Resources Used
    - Patient, Encounter, Condition, Observation
    - MedicationRequest, CarePlan, Task
    
    ## AI Agent Endpoints
    - `POST /api/v1/ai/chat` - Conversational AI interface
    - `GET /api/v1/patients/{id}/ai-analysis` - AI-powered analysis
    - `POST /api/v1/ai/compare-patients` - Multi-patient comparison
    - `POST /api/v1/patients/{id}/ai-discharge-plan` - AI discharge plan
    - `GET /api/v1/ai/status` - Agent status
    """,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix=settings.API_V1_PREFIX)


@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint - API information with AI Agent status
    """
    from app.services.ai_agent_service import ai_agent_service
    
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "description": "AI Agent-Powered Hospital Readmission Risk Assessment & Discharge Planning",
        "contest": "InterSystems Programming Contest: AI Agents for FHIR 2026",
        "task": "Task #9: Hospital Readmission Risk Workbench",
        "ai_agent": {
            "enabled": ai_agent_service.is_ai_available,
            "model": settings.AI_MODEL,
            "mode": "ai-powered" if ai_agent_service.is_ai_available else "rule-based-fallback"
        },
        "endpoints": {
            "documentation": "/docs",
            "health_check": f"{settings.API_V1_PREFIX}/health",
            "ai_status": f"{settings.API_V1_PREFIX}/ai/status",
            "ai_chat": f"{settings.API_V1_PREFIX}/ai/chat"
        }
    }

logger.info(f"Smart Discharge Navigator started - AI Agent: {'ENABLED' if settings.OPENAI_API_KEY else 'FALLBACK MODE'}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
