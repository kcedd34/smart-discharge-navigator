"""
Configuration Management

Centralized configuration using Pydantic Settings for type safety and validation.
Follows the Single Responsibility Principle (SRP).
"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """
    Application Settings
    
    All configuration parameters are loaded from environment variables
    with sensible defaults for development.
    """
    
    # Application
    APP_NAME: str = "Smart Discharge Navigator"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # FHIR Server Configuration
    FHIR_BASE_URL: str = "http://iris:52773/fhir/r4"
    IRIS_USERNAME: str = "SuperUser"
    IRIS_PASSWORD: str = "SYS"
    
    # InterSystems IRIS SQL Configuration (FHIR SQL Builder)
    # IRIS exposes FHIR resources as SQL tables via FHIR SQL Builder.
    # This allows SQL analytics on FHIR data alongside the REST API.
    IRIS_SQL_BASE_URL: str = "http://iris:52773"
    IRIS_SQL_NAMESPACE: str = "HSCUSTOM"  # Default FHIR namespace in IRIS for Health
    # FHIR SQL Builder schema — depends on IRIS configuration:
    #   Default: "HSFHIR_I0001_S" for first FHIR endpoint
    IRIS_FHIR_SQL_SCHEMA: str = "HSFHIR_I0001_S"
    
    # API Configuration
    API_V1_PREFIX: str = "/api/v1"
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    
    # Risk Assessment Thresholds
    HIGH_RISK_THRESHOLD: float = 0.7
    MODERATE_RISK_THRESHOLD: float = 0.4
    
    # Readmission Risk Factors (weights for rule-based scoring)
    WEIGHT_RECENT_ADMISSIONS: float = 0.25
    WEIGHT_HIGH_RISK_CONDITIONS: float = 0.20
    WEIGHT_POLYPHARMACY: float = 0.15
    WEIGHT_AGE_FACTOR: float = 0.15
    WEIGHT_MISSED_FOLLOWUPS: float = 0.15
    WEIGHT_ABNORMAL_VITALS: float = 0.10
    
    # AI Agent Configuration
    OPENAI_API_KEY: str = ""
    AI_MODEL: str = "gpt-4"
    AI_TEMPERATURE: float = 0.3
    AI_MAX_TOKENS: int = 2000
    AI_ENABLED: bool = True  # Feature toggle for AI capabilities
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Singleton instance
settings = Settings()
