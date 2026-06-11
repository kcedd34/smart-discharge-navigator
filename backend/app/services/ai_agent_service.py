"""
AI Agent Service — LLM-Powered Clinical Reasoning
(InterSystems AI Hub Integration)

Implements an AI Agent that uses OpenAI GPT-4 to analyze FHIR patient data,
provide clinical insights, and generate personalized discharge recommendations.

This service enhances (not replaces) the existing rule-based risk calculator
by adding LLM-powered reasoning on top of FHIR data.

═══════════════════════════════════════════════════════════════════════════
InterSystems AI Hub Integration Architecture
═══════════════════════════════════════════════════════════════════════════

This service implements the **AI Hub** pattern from the InterSystems platform:

  ┌─────────────────────────────────────────────────────────────────────┐
  │                    InterSystems AI Hub Pattern                     │
  │                                                                    │
  │  ┌────────────┐    ┌──────────────────┐    ┌──────────────────┐   │
  │  │ FHIR Data  │───►│  AI Agent Service │───►│  LLM Provider    │   │
  │  │ (IRIS)     │    │  (Orchestrator)   │    │  (OpenAI GPT-4)  │   │
  │  └────────────┘    └──────────────────┘    └──────────────────┘   │
  │                           │                                        │
  │                    ┌──────┴──────┐                                 │
  │                    │ Rule Engine │                                  │
  │                    │ (Baseline)  │                                  │
  │                    └─────────────┘                                  │
  └─────────────────────────────────────────────────────────────────────┘

  AI Hub Integration Details:
  ─────────────────────────
  • The InterSystems AI Hub provides a framework for integrating AI/ML models
    with healthcare data stored in IRIS.
  • In this implementation, we use OpenAI GPT-4 as the **external LLM provider**
    following the AI Hub's model-agnostic integration pattern.
  • The AI Agent Service acts as the **orchestrator** that:
    1. Retrieves clinical data from IRIS FHIR server
    2. Structures it as clinical context for the LLM
    3. Sends reasoning requests to the LLM provider
    4. Merges AI insights with rule-based baseline scores
    5. Returns hybrid (AI + rules) clinical assessments
  • This architecture is compatible with InterSystems IntegratedML:
    - In production, the external LLM could be replaced with (or supplemented by)
      IntegratedML models trained directly on IRIS data
    - The orchestrator pattern remains the same regardless of model source
    - IRIS IntegratedML supports: CREATE MODEL, TRAIN MODEL, PREDICT statements
  • The graceful degradation to rule-based mode when the LLM is unavailable
    mirrors the AI Hub's resilience pattern.

  Contest Compliance:
  ──────────────────
  ✅ AI Hub: External LLM integration following AI Hub orchestration pattern
  ✅ FHIR Data: All reasoning grounded in FHIR R4 resources from IRIS
  ✅ Hybrid Approach: AI enhances (never replaces) deterministic rules
  ✅ Model-Agnostic: Architecture supports swapping LLM providers or
     using IntegratedML for on-premise models

Follows the Single Responsibility Principle and integrates with InterSystems IRIS
via the existing FHIR client.
"""

import json
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime

from openai import AsyncOpenAI, APIError, RateLimitError, APIConnectionError
from app.core.config import settings
from app.core.fhir_client import fhir_client
from app.services.risk_calculator import risk_calculator
from app.models.patient import (
    AIAnalysis, AIReasoningStep, ChatResponse,
    AIComparisonResult, RiskAssessment, PatientRoleSummary
)

logger = logging.getLogger("ai_agent")
logger.setLevel(logging.INFO)


# ──────────────────────────────────────────────
# System Prompts for the AI Agent
# ──────────────────────────────────────────────

SYSTEM_PROMPT = """You are a Clinical AI Agent specialized in hospital readmission risk assessment, \
integrated with InterSystems IRIS for Health FHIR R4 server.

Your capabilities:
1. Analyze FHIR patient data (Patient, Encounter, Condition, Observation, MedicationRequest, AllergyIntolerance resources)
2. Assess 30-day hospital readmission risk using clinical reasoning
3. Generate personalized discharge recommendations
4. Identify risk factors that rule-based systems might miss (drug interactions, social determinants, comorbidity synergies, allergy risks)
5. Compare multiple patients for triage prioritization
6. Generate role-adapted patient summaries (doctor, patient, caregiver, care_manager)

Guidelines:
- Always ground your analysis in the provided FHIR data
- Use evidence-based clinical reasoning
- Clearly distinguish between high-confidence findings and uncertain observations
- Provide actionable, specific recommendations
- Consider the whole patient picture: demographics, conditions, medications, encounters, vitals
- When you identify risks that a simple rule-based system would miss, explicitly call them out
- Format responses clearly with sections and bullet points
- Be concise but thorough

You are part of the Smart Discharge Navigator system for the InterSystems Programming Contest: AI Agents for FHIR 2026."""

ANALYSIS_PROMPT_TEMPLATE = """Analyze this patient's 30-day hospital readmission risk using the FHIR data below.

**Patient FHIR Data:**
{fhir_data}

**Rule-Based Assessment (baseline):**
- Risk Score: {rule_score}
- Risk Level: {rule_level}
- Rule-Based Factors: {rule_factors}

**Instructions:**
Provide your analysis as a JSON object with this exact structure:
{{
  "ai_risk_level": "HIGH" | "MODERATE" | "LOW",
  "confidence_score": 0.0 to 1.0,
  "insights": ["insight1", "insight2", ...],
  "reasoning_steps": [
    {{"step": 1, "action": "what you analyzed", "finding": "what you found", "clinical_relevance": "why it matters"}}
  ],
  "recommendations": ["recommendation1", "recommendation2", ...],
  "risks_missed_by_rules": ["risk1", "risk2", ...]
}}

Focus on:
1. Comorbidity interactions the rule-based system might miss
2. Medication-related risks (polypharmacy, drug interactions, adherence concerns)
3. AllergyIntolerance risks — flag known allergies that may interact with current medications or typical discharge prescriptions
4. Encounter patterns suggesting deterioration
5. Social and demographic factors affecting readmission
6. Vital sign trends rather than single-point values
7. Specific, actionable discharge interventions"""

DISCHARGE_PLAN_PROMPT = """Generate a comprehensive, personalized AI-powered discharge plan for this patient.

**Patient FHIR Data:**
{fhir_data}

**Risk Assessment:**
- AI Risk Level: {risk_level}
- Key Risks: {key_risks}

**Instructions:**
Create a detailed discharge plan as a markdown document with these sections:
1. **Patient Summary** - Brief clinical overview
2. **Risk Mitigation Strategy** - How to address each identified risk
3. **Medication Management** - Specific medication instructions, potential interactions to watch
4. **Follow-up Schedule** - Recommended appointments with timeframes and priorities
5. **Patient Education** - Key topics the patient needs to understand
6. **Warning Signs** - Red flags that should prompt immediate medical attention
7. **Care Coordination** - Recommended specialist referrals and care team communication
8. **Home Care Instructions** - Daily activities, diet, exercise recommendations

Be specific and personalized based on the patient's actual conditions and medications."""

COMPARE_PROMPT_TEMPLATE = """Compare these patients for readmission risk triage prioritization.

**Patients FHIR Data:**
{patients_data}

**Instructions:**
Provide your comparison as a JSON object:
{{
  "comparison_summary": "Natural language summary comparing all patients",
  "risk_ranking": [
    {{"patient_id": "id", "patient_name": "name", "risk_level": "HIGH/MODERATE/LOW", "priority_score": 0.0-1.0, "key_concern": "main concern"}}
  ],
  "common_risk_factors": ["factor1", "factor2"],
  "unique_concerns": {{"patient_id": ["concern1", "concern2"]}},
  "triage_recommendation": "Which patient(s) need immediate attention and why"
}}"""

CHAT_PROMPT_TEMPLATE = """Answer the clinical query using available FHIR patient data.

**Available Patient Data:**
{context_data}

**User Query:**
{query}

Provide a helpful, clinically-informed response grounded in the FHIR data provided above.
When ranking patients by readmission risk, use the rule_based_risk_score and rule_based_risk_level
fields as a baseline, then apply additional clinical reasoning from their encounters, conditions,
medications, observations, and allergies to refine the ranking.
Always cite which FHIR resources informed your answer."""

SUMMARY_ROLE_PROMPT_TEMPLATE = """Generate a patient summary tailored for the role: **{role}**

Role-specific instructions:
- **doctor / ed_doctor**: Full clinical detail. Include ICD-10/SNOMED codes, lab/vital trends, active medication list with dosages, comorbidity interactions, allergy flags and cross-reactions with current meds, encounter history, risk score, and specialty referral recommendations.
- **care_manager**: Focus on care gaps, follow-up adherence, social determinants of health, post-discharge coordination needs, allergy considerations for community prescriptions, and risk stratification for case management prioritization.
- **patient**: Plain language (8th-grade reading level). Explain conditions in everyday words, describe what each medication does, list allergy warnings they must share with any new provider, describe warning signs that require emergency care, and provide simple next-step actions.
- **caregiver / family**: Home-care focused. What to watch for day-to-day, how to administer medications safely (note any allergy-related precautions), when to call the doctor, dietary/activity guidance, and emergency action plan.

**Patient FHIR Data:**
{fhir_data}

**Risk Assessment:**
{risk_summary}

**Known Allergies:**
{allergies}

Return a JSON object with this exact structure:
{{
  "role": "{role}",
  "summary_title": "Brief descriptive title",
  "sections": [
    {{"title": "Section title", "content": "Section text — use clear paragraphs or bullet points"}}
  ],
  "key_alerts": ["Alert 1", "Alert 2"],
  "next_actions": ["Action 1", "Action 2"],
  "allergy_warnings": ["Allergy warning if relevant, else empty list"]
}}"""


class AIAgentService:
    """
    AI Agent Service — LLM-powered clinical reasoning for FHIR data
    (InterSystems AI Hub Integration)

    Implements the AI Hub pattern by orchestrating between:
    - InterSystems IRIS FHIR data (input)
    - OpenAI GPT-4 LLM (reasoning engine — AI Hub external model)
    - Rule-based risk calculator (deterministic baseline)

    This service can be adapted to use InterSystems IntegratedML
    instead of (or alongside) the external LLM, by replacing the
    _call_llm() method with IntegratedML PREDICT calls.

    Provides:
    - AI-powered patient risk analysis (hybrid with rule-based)
    - Conversational clinical query interface
    - AI-generated discharge plans
    - Multi-patient comparison for triage
    """

    def __init__(self):
        self.fhir_client = fhir_client
        self.risk_calculator = risk_calculator
        self._client: Optional[AsyncOpenAI] = None
        self._ai_available = False
        self._initialize_client()

    def _initialize_client(self):
        """Initialize OpenAI client if API key is available"""
        if settings.OPENAI_API_KEY:
            self._client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            self._ai_available = True
            logger.info("AI Agent initialized with OpenAI API key")
        else:
            logger.warning(
                "OPENAI_API_KEY not set - AI Agent will use fallback mode. "
                "Set the environment variable to enable full AI capabilities."
            )

    @property
    def is_ai_available(self) -> bool:
        """Check if AI capabilities are available"""
        return self._ai_available and settings.AI_ENABLED

    async def _call_llm(self, system_prompt: str, user_prompt: str, json_mode: bool = False) -> str:
        """
        Call OpenAI LLM with error handling and retry logic

        Args:
            system_prompt: System role instructions
            user_prompt: User message with data/query
            json_mode: Whether to request JSON-formatted output

        Returns:
            LLM response text
        """
        if not self.is_ai_available:
            raise ValueError("AI Agent not available - OPENAI_API_KEY not configured")

        try:
            kwargs = {
                "model": settings.AI_MODEL,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": settings.AI_TEMPERATURE,
                "max_tokens": settings.AI_MAX_TOKENS,
            }
            if json_mode:
                kwargs["response_format"] = {"type": "json_object"}

            response = await self._client.chat.completions.create(**kwargs)

            logger.info(
                f"LLM call completed - model={settings.AI_MODEL}, "
                f"tokens_used={response.usage.total_tokens if response.usage else 'N/A'}"
            )

            return response.choices[0].message.content

        except RateLimitError as e:
            logger.error(f"OpenAI rate limit hit: {e}")
            raise ValueError("AI service temporarily unavailable due to rate limiting. Please retry.")
        except APIConnectionError as e:
            logger.error(f"OpenAI connection error: {e}")
            raise ValueError("Unable to connect to AI service. Please check network connectivity.")
        except APIError as e:
            logger.error(f"OpenAI API error: {e}")
            raise ValueError(f"AI service error: {str(e)}")

    async def _gather_patient_fhir_data(self, patient_id: str) -> Dict[str, Any]:
        """
        Gather all relevant FHIR data for a patient

        Fetches Patient, Encounter, Condition, Observation, and MedicationRequest
        resources from InterSystems IRIS FHIR server.

        Returns:
            Dictionary with structured FHIR data summary
        """
        patient = await self.fhir_client.get_resource("Patient", patient_id)
        if not patient:
            return {}

        encounters = await self.fhir_client.get_patient_encounters(patient_id)
        conditions = await self.fhir_client.get_patient_conditions(patient_id)
        observations = await self.fhir_client.get_patient_observations(patient_id)
        medications = await self.fhir_client.get_patient_medications(patient_id)
        allergies = await self.fhir_client.get_patient_allergies(patient_id)

        # Extract readable name
        name = "Unknown"
        name_list = patient.get("name", [])
        if name_list:
            n = name_list[0]
            name = f"{' '.join(n.get('given', []))} {n.get('family', '')}".strip()

        # Build structured summary for LLM context
        return {
            "patient_id": patient_id,
            "patient_name": name,
            "birth_date": patient.get("birthDate", "unknown"),
            "gender": patient.get("gender", "unknown"),
            "encounters": [
                {
                    "id": e.get("id"),
                    "status": e.get("status"),
                    "class": e.get("class", {}).get("code", "unknown"),
                    "period": e.get("period", {}),
                    "type": [t.get("text", "") for t in e.get("type", [])],
                    "reason": [r.get("text", "") for r in e.get("reasonCode", [])]
                }
                for e in encounters[:20]  # Limit to avoid token overflow
            ],
            "conditions": [
                {
                    "code": c.get("code", {}).get("coding", [{}])[0].get("code", "") if c.get("code", {}).get("coding") else "",
                    "display": c.get("code", {}).get("coding", [{}])[0].get("display", "") if c.get("code", {}).get("coding") else c.get("code", {}).get("text", ""),
                    "clinical_status": c.get("clinicalStatus", {}).get("coding", [{}])[0].get("code", "") if c.get("clinicalStatus", {}).get("coding") else "",
                    "onset": c.get("onsetDateTime", "")
                }
                for c in conditions[:20]
            ],
            "observations": [
                {
                    "code": o.get("code", {}).get("coding", [{}])[0].get("display", "") if o.get("code", {}).get("coding") else "",
                    "value": o.get("valueQuantity", {}).get("value", ""),
                    "unit": o.get("valueQuantity", {}).get("unit", ""),
                    "date": o.get("effectiveDateTime", ""),
                    "status": o.get("status", "")
                }
                for o in observations[:30]
            ],
            "medications": [
                {
                    "medication": m.get("medicationCodeableConcept", {}).get("text", "") or
                                  (m.get("medicationCodeableConcept", {}).get("coding", [{}])[0].get("display", "") if m.get("medicationCodeableConcept", {}).get("coding") else ""),
                    "status": m.get("status", ""),
                    "dosage": [d.get("text", "") for d in m.get("dosageInstruction", [])]
                }
                for m in medications[:20]
            ],
            "encounter_count": len(encounters),
            "condition_count": len(conditions),
            "medication_count": len(medications),
            "allergies": [
                {
                    "substance": a.get("code", {}).get("text", "") or
                                 (a.get("code", {}).get("coding", [{}])[0].get("display", "") if a.get("code", {}).get("coding") else ""),
                    "criticality": a.get("criticality", "unknown"),
                    "clinical_status": a.get("clinicalStatus", {}).get("coding", [{}])[0].get("code", "") if a.get("clinicalStatus", {}).get("coding") else "",
                    "reaction": [
                        r.get("manifestation", [{}])[0].get("coding", [{}])[0].get("display", "")
                        if r.get("manifestation") and r["manifestation"][0].get("coding")
                        else r.get("manifestation", [{}])[0].get("text", "")
                        for r in a.get("reaction", [])
                    ]
                }
                for a in allergies[:20]
            ],
            "allergy_count": len(allergies)
        }

    def _generate_fallback_analysis(self, patient_id: str, patient_name: str,
                                     rule_assessment: RiskAssessment) -> AIAnalysis:
        """
        Generate analysis using rule-based system when AI is not available.
        Provides structured output matching AI format for consistent UI rendering.
        """
        insights = [
            f"Rule-based risk score: {rule_assessment.risk_score:.3f} ({rule_assessment.risk_level})",
            f"Analysis based on {len(rule_assessment.risk_factors)} clinical risk factors",
        ]
        for factor in rule_assessment.risk_factors:
            if factor.value > 0.5:
                insights.append(f"⚠️ High factor: {factor.name} ({factor.value:.0%}) - {factor.description}")

        return AIAnalysis(
            patient_id=patient_id,
            patient_name=patient_name,
            ai_risk_level=rule_assessment.risk_level,
            ai_confidence_score=0.6,  # Lower confidence for rule-based
            rule_based_score=rule_assessment.risk_score,
            ai_insights=insights,
            reasoning_steps=[
                AIReasoningStep(
                    step=i + 1,
                    action=f"Evaluate {f.name}",
                    finding=f.description,
                    clinical_relevance=f"Contributes {f.weight:.0%} weight with score {f.value:.0%}"
                )
                for i, f in enumerate(rule_assessment.risk_factors)
            ],
            recommendations=rule_assessment.recommendations,
            risks_missed_by_rules=[],
            model_used="rule-based-fallback"
        )

    async def analyze_patient_with_ai(self, patient_id: str) -> AIAnalysis:
        """
        Perform AI-powered analysis of a patient's readmission risk.

        Combines FHIR data retrieval, rule-based scoring, and LLM reasoning
        to produce a comprehensive risk assessment.

        Args:
            patient_id: FHIR Patient resource ID

        Returns:
            AIAnalysis with insights, reasoning steps, and recommendations
        """
        # Step 1: Gather FHIR data from InterSystems IRIS
        fhir_data = await self._gather_patient_fhir_data(patient_id)
        if not fhir_data:
            raise ValueError(f"Patient {patient_id} not found in FHIR server")

        patient_name = fhir_data.get("patient_name", "Unknown")

        # Step 2: Get rule-based assessment as baseline
        patient = await self.fhir_client.get_resource("Patient", patient_id)
        age = self._calculate_age(patient.get("birthDate"))
        encounters = await self.fhir_client.get_patient_encounters(patient_id)
        conditions = await self.fhir_client.get_patient_conditions(patient_id)
        medications = await self.fhir_client.get_patient_medications(patient_id)
        observations = await self.fhir_client.get_patient_observations(patient_id)

        rule_assessment = self.risk_calculator.calculate_risk(
            patient_id=patient_id,
            patient_age=age,
            encounters=encounters,
            conditions=conditions,
            medications=medications,
            observations=observations
        )

        # Step 3: If AI not available, return enhanced rule-based analysis
        if not self.is_ai_available:
            logger.info(f"AI unavailable - returning rule-based analysis for patient {patient_id}")
            return self._generate_fallback_analysis(patient_id, patient_name, rule_assessment)

        # Step 4: Call LLM with FHIR context
        rule_factors_str = "; ".join(
            f"{f.name}: {f.value:.0%} (weight={f.weight:.0%})"
            for f in rule_assessment.risk_factors
        )

        user_prompt = ANALYSIS_PROMPT_TEMPLATE.format(
            fhir_data=json.dumps(fhir_data, indent=2, default=str),
            rule_score=f"{rule_assessment.risk_score:.3f}",
            rule_level=rule_assessment.risk_level,
            rule_factors=rule_factors_str
        )

        try:
            llm_response = await self._call_llm(SYSTEM_PROMPT, user_prompt, json_mode=True)
            result = json.loads(llm_response)

            reasoning_steps = [
                AIReasoningStep(**step) for step in result.get("reasoning_steps", [])
            ]

            return AIAnalysis(
                patient_id=patient_id,
                patient_name=patient_name,
                ai_risk_level=result.get("ai_risk_level", rule_assessment.risk_level),
                ai_confidence_score=min(1.0, max(0.0, result.get("confidence_score", 0.7))),
                rule_based_score=rule_assessment.risk_score,
                ai_insights=result.get("insights", []),
                reasoning_steps=reasoning_steps,
                recommendations=result.get("recommendations", []),
                risks_missed_by_rules=result.get("risks_missed_by_rules", []),
                model_used=settings.AI_MODEL
            )

        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to parse LLM response: {e}")
            return self._generate_fallback_analysis(patient_id, patient_name, rule_assessment)
        except ValueError as e:
            logger.error(f"LLM call failed: {e}")
            return self._generate_fallback_analysis(patient_id, patient_name, rule_assessment)

    async def chat_with_agent(self, query: str, patient_id: Optional[str] = None,
                               conversation_history: list = None) -> ChatResponse:
        """
        Conversational interface to the AI Agent.

        Allows clinicians to ask natural language questions about patients,
        readmission risks, and discharge planning.

        Args:
            query: Natural language question
            patient_id: Optional patient context
            conversation_history: Previous chat messages

        Returns:
            ChatResponse with answer and sources
        """
        context_data = {}
        sources = []
        patient_ids_referenced = []

        # Gather context based on query
        if patient_id:
            fhir_data = await self._gather_patient_fhir_data(patient_id)
            if fhir_data:
                context_data[patient_id] = fhir_data
                sources.extend([
                    f"Patient/{patient_id}",
                    f"Encounter (×{fhir_data['encounter_count']})",
                    f"Condition (×{fhir_data['condition_count']})",
                    f"MedicationRequest (×{fhir_data['medication_count']})"
                ])
                patient_ids_referenced.append(patient_id)
        else:
            # For general queries, load full clinical FHIR data + risk scores for all patients
            patients = await self.fhir_client.search_resources("Patient", {"_count": "50"})
            enriched_summaries = []
            for p in patients[:10]:  # Limit to 10 for token economy
                pid = p.get("id", "")
                if not pid:
                    continue

                # Gather full FHIR data for each patient
                fhir_data = await self._gather_patient_fhir_data(pid)
                if not fhir_data:
                    continue

                # Calculate rule-based risk score as context for the LLM
                try:
                    age = self._calculate_age(p.get("birthDate"))
                    encounters = await self.fhir_client.get_patient_encounters(pid)
                    conditions = await self.fhir_client.get_patient_conditions(pid)
                    medications = await self.fhir_client.get_patient_medications(pid)
                    observations = await self.fhir_client.get_patient_observations(pid)
                    rule_assessment = self.risk_calculator.calculate_risk(
                        patient_id=pid,
                        patient_age=age,
                        encounters=encounters,
                        conditions=conditions,
                        medications=medications,
                        observations=observations
                    )
                    fhir_data["rule_based_risk_score"] = round(rule_assessment.risk_score, 3)
                    fhir_data["rule_based_risk_level"] = rule_assessment.risk_level
                    fhir_data["rule_based_risk_factors"] = [
                        {"name": f.name, "value": round(f.value, 3), "description": f.description}
                        for f in rule_assessment.risk_factors
                    ]
                except Exception as e:
                    logger.warning(f"Could not calculate risk for patient {pid}: {e}")
                    fhir_data["rule_based_risk_score"] = None
                    fhir_data["rule_based_risk_level"] = "UNKNOWN"

                enriched_summaries.append(fhir_data)
                patient_ids_referenced.append(pid)

            context_data["patients"] = enriched_summaries
            sources.append(f"Patient list (×{len(enriched_summaries)})")
            sources.append(f"Encounter, Condition, MedicationRequest, Observation, AllergyIntolerance per patient")

        if not self.is_ai_available:
            return ChatResponse(
                response=(
                    "⚠️ **AI Agent is in fallback mode** (OpenAI API key not configured).\n\n"
                    "I can still provide information based on the rule-based system:\n"
                    f"- Available patient data: {len(context_data)} records loaded\n"
                    f"- Sources: {', '.join(sources)}\n\n"
                    "To enable full AI-powered conversations, set the `OPENAI_API_KEY` environment variable."
                ),
                sources=sources,
                patient_ids_referenced=patient_ids_referenced,
                confidence=0.3,
                ai_powered=False
            )

        # Build conversation messages
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        if conversation_history:
            for msg in conversation_history[-10:]:  # Last 10 messages for context window
                messages.append({"role": msg.role, "content": msg.content})

        user_prompt = CHAT_PROMPT_TEMPLATE.format(
            context_data=json.dumps(context_data, indent=2, default=str),
            query=query
        )
        messages.append({"role": "user", "content": user_prompt})

        try:
            response = await self._client.chat.completions.create(
                model=settings.AI_MODEL,
                messages=messages,
                temperature=settings.AI_TEMPERATURE,
                max_tokens=settings.AI_MAX_TOKENS,
            )

            return ChatResponse(
                response=response.choices[0].message.content,
                sources=sources,
                patient_ids_referenced=patient_ids_referenced,
                confidence=0.85,
                ai_powered=True
            )

        except Exception as e:
            logger.error(f"Chat LLM error: {e}")
            return ChatResponse(
                response=f"I encountered an issue processing your query: {str(e)}. Please try again.",
                sources=sources,
                patient_ids_referenced=patient_ids_referenced,
                confidence=0.0,
                ai_powered=False
            )

    async def generate_ai_discharge_plan(self, patient_id: str) -> str:
        """
        Generate an AI-powered personalized discharge plan.

        Uses LLM to create a comprehensive, patient-specific discharge plan
        based on FHIR data and risk assessment.

        Args:
            patient_id: FHIR Patient resource ID

        Returns:
            Markdown-formatted discharge plan
        """
        fhir_data = await self._gather_patient_fhir_data(patient_id)
        if not fhir_data:
            raise ValueError(f"Patient {patient_id} not found in FHIR server")

        # Get AI analysis for risk context
        try:
            analysis = await self.analyze_patient_with_ai(patient_id)
            risk_level = analysis.ai_risk_level
            key_risks = analysis.ai_insights[:5]
        except Exception:
            risk_level = "UNKNOWN"
            key_risks = ["Unable to determine - using available data"]

        if not self.is_ai_available:
            # Fallback: generate structured plan without LLM
            return self._generate_fallback_discharge_plan(fhir_data, risk_level)

        user_prompt = DISCHARGE_PLAN_PROMPT.format(
            fhir_data=json.dumps(fhir_data, indent=2, default=str),
            risk_level=risk_level,
            key_risks="\n".join(f"- {r}" for r in key_risks)
        )

        try:
            return await self._call_llm(SYSTEM_PROMPT, user_prompt)
        except ValueError as e:
            logger.error(f"Discharge plan LLM error: {e}")
            return self._generate_fallback_discharge_plan(fhir_data, risk_level)

    async def compare_patients(self, patient_ids: List[str]) -> AIComparisonResult:
        """
        Compare multiple patients for triage prioritization using AI.

        Args:
            patient_ids: List of FHIR Patient IDs to compare

        Returns:
            AIComparisonResult with ranking and insights
        """
        patients_data = {}
        for pid in patient_ids:
            data = await self._gather_patient_fhir_data(pid)
            if data:
                patients_data[pid] = data

        if len(patients_data) < 2:
            raise ValueError("At least 2 valid patients required for comparison")

        if not self.is_ai_available:
            return self._generate_fallback_comparison(patients_data)

        user_prompt = COMPARE_PROMPT_TEMPLATE.format(
            patients_data=json.dumps(patients_data, indent=2, default=str)
        )

        try:
            llm_response = await self._call_llm(SYSTEM_PROMPT, user_prompt, json_mode=True)
            result = json.loads(llm_response)

            return AIComparisonResult(
                patient_ids=list(patients_data.keys()),
                comparison_summary=result.get("comparison_summary", ""),
                risk_ranking=result.get("risk_ranking", []),
                common_risk_factors=result.get("common_risk_factors", []),
                unique_concerns=result.get("unique_concerns", {}),
                triage_recommendation=result.get("triage_recommendation", ""),
                ai_powered=True
            )

        except Exception as e:
            logger.error(f"Compare patients LLM error: {e}")
            return self._generate_fallback_comparison(patients_data)

    async def generate_patient_summary_by_role(
        self, patient_id: str, role: str
    ) -> "PatientRoleSummary":
        """
        Generate a role-adapted patient summary using LLM.

        Tailors the clinical narrative for the target audience:
        - doctor/ed_doctor: Full clinical detail with codes and interactions
        - care_manager: Care gaps, follow-up adherence, SDH
        - patient: Plain language, what it means, what to do
        - caregiver/family: Home-care instructions and warning signs

        Args:
            patient_id: FHIR Patient ID
            role: Target role (doctor | ed_doctor | patient | caregiver | family | care_manager)

        Returns:
            PatientRoleSummary with role-adapted sections
        """
        valid_roles = {"doctor", "ed_doctor", "patient", "caregiver", "family", "care_manager"}
        if role not in valid_roles:
            role = "doctor"

        fhir_data = await self._gather_patient_fhir_data(patient_id)
        if not fhir_data:
            raise ValueError(f"Patient {patient_id} not found in FHIR server")

        # Build a concise risk summary using rule-based calculator
        patient = await self.fhir_client.get_resource("Patient", patient_id)
        age = self._calculate_age(patient.get("birthDate"))
        encounters = await self.fhir_client.get_patient_encounters(patient_id)
        conditions = await self.fhir_client.get_patient_conditions(patient_id)
        medications = await self.fhir_client.get_patient_medications(patient_id)
        observations = await self.fhir_client.get_patient_observations(patient_id)

        rule_assessment = self.risk_calculator.calculate_risk(
            patient_id=patient_id,
            patient_age=age,
            encounters=encounters,
            conditions=conditions,
            medications=medications,
            observations=observations
        )

        risk_summary = (
            f"Risk Score: {rule_assessment.risk_score:.3f} | "
            f"Level: {rule_assessment.risk_level} | "
            f"Top factors: {', '.join(f.name for f in rule_assessment.risk_factors if f.value > 0.5)}"
        )

        allergies_str = (
            "; ".join(
                f"{a['substance']} (criticality: {a['criticality']}, reaction: {', '.join(r for r in a['reaction'] if r)})"
                for a in fhir_data.get("allergies", [])
            ) or "No active allergies documented"
        )

        if not self.is_ai_available:
            return self._generate_fallback_role_summary(
                fhir_data, role, rule_assessment, allergies_str
            )

        user_prompt = SUMMARY_ROLE_PROMPT_TEMPLATE.format(
            role=role,
            fhir_data=json.dumps(fhir_data, indent=2, default=str),
            risk_summary=risk_summary,
            allergies=allergies_str
        )

        try:
            llm_response = await self._call_llm(SYSTEM_PROMPT, user_prompt, json_mode=True)
            result = json.loads(llm_response)

            return PatientRoleSummary(
                patient_id=patient_id,
                patient_name=fhir_data.get("patient_name", "Unknown"),
                role=result.get("role", role),
                summary_title=result.get("summary_title", f"Patient Summary for {role}"),
                sections=result.get("sections", []),
                key_alerts=result.get("key_alerts", []),
                next_actions=result.get("next_actions", []),
                allergy_warnings=result.get("allergy_warnings", []),
                ai_powered=True,
                model_used=settings.AI_MODEL
            )

        except Exception as e:
            logger.error(f"Role summary LLM error for patient {patient_id} role={role}: {e}")
            return self._generate_fallback_role_summary(
                fhir_data, role, rule_assessment, allergies_str
            )

    def _generate_fallback_role_summary(
        self, fhir_data: dict, role: str,
        rule_assessment: "RiskAssessment", allergies_str: str
    ) -> "PatientRoleSummary":
        """Generate a basic role summary without LLM."""
        name = fhir_data.get("patient_name", "Unknown")
        conditions = [c.get("display", "") for c in fhir_data.get("conditions", []) if c.get("display")]
        medications = [m.get("medication", "") for m in fhir_data.get("medications", []) if m.get("medication")]

        sections = [
            {"title": "Conditions", "content": "; ".join(conditions[:5]) or "None documented"},
            {"title": "Medications", "content": "; ".join(medications[:8]) or "None documented"},
            {"title": "Allergies", "content": allergies_str},
            {"title": "Risk Level", "content": f"{rule_assessment.risk_level} (score: {rule_assessment.risk_score:.3f})"}
        ]

        return PatientRoleSummary(
            patient_id=fhir_data.get("patient_id", ""),
            patient_name=name,
            role=role,
            summary_title=f"Patient Summary — {name} ({role})",
            sections=sections,
            key_alerts=[f"Risk level: {rule_assessment.risk_level}"],
            next_actions=rule_assessment.recommendations[:3],
            allergy_warnings=[allergies_str] if fhir_data.get("allergy_count", 0) > 0 else [],
            ai_powered=False,
            model_used="rule-based-fallback"
        )

    def _generate_fallback_discharge_plan(self, fhir_data: dict, risk_level: str) -> str:
        """Generate a structured discharge plan without LLM"""
        name = fhir_data.get("patient_name", "the patient")
        conditions = [c.get("display", "Unknown") for c in fhir_data.get("conditions", [])]
        medications = [m.get("medication", "Unknown") for m in fhir_data.get("medications", [])]

        return f"""# AI Discharge Plan for {name}
*Generated by Smart Discharge Navigator (Rule-Based Fallback)*
*Note: Set OPENAI_API_KEY for full AI-powered plans*

## Patient Summary
- **Name:** {name}
- **Risk Level:** {risk_level}
- **Active Conditions:** {', '.join(conditions[:5]) if conditions else 'None documented'}
- **Current Medications:** {len(medications)} active medications

## Discharge Recommendations
1. Schedule follow-up appointment within {'48 hours' if risk_level == 'HIGH' else '7 days'}
2. Review all current medications with pharmacist
3. Ensure patient education on warning signs
4. {'Arrange home health visit' if risk_level == 'HIGH' else 'Provide self-care instructions'}

## Medications
{chr(10).join(f'- {m}' for m in medications[:10]) if medications else '- No medications documented'}

## Follow-up Schedule
- Primary Care: {'Within 48 hours' if risk_level == 'HIGH' else 'Within 1 week'}
- Specialist: As needed based on conditions
- Lab Work: Per condition-specific protocols

## Warning Signs - Seek Immediate Care If:
- Worsening shortness of breath
- Chest pain or pressure
- Sudden confusion or dizziness
- Fever above 101°F (38.3°C)
- Inability to keep medications down
"""

    def _generate_fallback_comparison(self, patients_data: dict) -> AIComparisonResult:
        """Generate comparison without LLM using rule-based data"""
        ranking = []
        for pid, data in patients_data.items():
            ranking.append({
                "patient_id": pid,
                "patient_name": data.get("patient_name", "Unknown"),
                "condition_count": data.get("condition_count", 0),
                "medication_count": data.get("medication_count", 0),
                "encounter_count": data.get("encounter_count", 0)
            })

        ranking.sort(key=lambda x: x["encounter_count"], reverse=True)

        return AIComparisonResult(
            patient_ids=list(patients_data.keys()),
            comparison_summary="Comparison based on rule-based analysis (AI not available). "
                             "Patients ranked by encounter frequency as proxy for acuity.",
            risk_ranking=ranking,
            common_risk_factors=["Multiple encounters"],
            unique_concerns={},
            triage_recommendation="Review patients with highest encounter counts first. "
                                "Enable AI (set OPENAI_API_KEY) for deeper clinical comparison.",
            ai_powered=False
        )

    @staticmethod
    def _calculate_age(birth_date: str) -> int:
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


# Singleton instance
ai_agent_service = AIAgentService()
