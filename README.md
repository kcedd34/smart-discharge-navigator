# Smart Discharge Navigator 🏥🤖

**AI-Powered Clinical Reasoning Agent for Hospital Readmission Risk Assessment**

*Hybrid Intelligence: LLM-based Clinical Insights + Evidence-based Rule Engine*

[![InterSystems Contest](https://img.shields.io/badge/InterSystems-AI%20Agents%20for%20FHIR%202026-blue)](https://community.intersystems.com/post/intersystems-programming-contest-ai-agents-fhir)
[![Task](https://img.shields.io/badge/Contest%20Task-%239%20Hospital%20Readmission%20Risk-green)](https://community.intersystems.com/post/intersystems-programming-contest-ai-agents-fhir)
[![AI Agent](https://img.shields.io/badge/AI%20Agent-OpenAI%20GPT--4o-blueviolet)](https://openai.com/)
[![FHIR](https://img.shields.io/badge/FHIR-R4-orange)](https://www.hl7.org/fhir/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Author](https://img.shields.io/badge/Author-Carlos%20Eduardo%20Dias%20Duarte-informational)](mailto:kcedd34@gmail.com)
[![GitHub](https://img.shields.io/badge/GitHub-kcedd34%2Fsmart--discharge--navigator-181717?logo=github)](https://github.com/kcedd34/smart-discharge-navigator)

---

## 📋 Table of Contents

- [Overview](#overview)
- [What Makes This an AI Agent?](#-what-makes-this-an-ai-agent)
- [AI Agent Features](#-ai-agent-features)
- [AI Agent Architecture](#-ai-agent-architecture)
- [Contest Alignment](#-contest-alignment)
- [Features](#-features)
- [Risk Assessment Algorithm](#-risk-assessment-algorithm)
- [API Documentation](#-api-documentation)
- [Installation](#-installation)
- [Environment Variables](#-environment-variables)
- [Usage](#-usage)
- [FHIR Resources](#-fhir-resources)
- [Technology Stack](#-technology-stack)
- [Development](#-development)
- [Demo Video](#-demo-video)
- [License](#-license)

---

## 🎯 Overview

**Smart Discharge Navigator** is a **true AI Agent for FHIR** that combines LLM-powered clinical reasoning (OpenAI GPT-4) with evidence-based rule scoring to tackle one of healthcare's most critical challenges: **hospital readmissions**.

The AI Agent:
- **Reads and reasons** over FHIR patient data (encounters, conditions, medications, vitals)
- **Engages in clinical dialogue** through a conversational chat interface
- **Generates contextual insights** that go beyond fixed rules — identifying non-obvious risk factors
- **Produces personalized discharge plans** with clinical reasoning explanations
- **Compares and triages** multiple patients using AI-powered risk ranking

### The Problem

- **$17 billion** lost annually in the US due to preventable hospital readmissions
- **20%** of readmissions are preventable with proper discharge planning
- Hospital Readmission Reduction Program (HRRP) penalties cost hospitals millions
- Traditional rule-based systems miss nuanced, patient-specific risk factors

### The Solution — Hybrid Intelligence

Smart Discharge Navigator provides a **two-layer approach**:

1. **🤖 AI Agent Layer (Primary)** — GPT-4-powered clinical reasoning that analyzes FHIR data, explains its thinking, and identifies risks that rules alone miss
2. **📊 Rule-Based Engine (Baseline)** — Deterministic, evidence-based scoring providing a reliable safety net and benchmark

This hybrid design ensures **accurate, explainable, and safe** clinical decision support.

---

## ✨ What Makes This an AI Agent?

This project implements a **genuine AI Agent** — not just a rule engine with "AI" branding. Here's the concrete difference:

| Aspect | Before (Rule-based only) | After (AI Agent + Rules) |
|--------|--------------------------|--------------------------|
| **Analysis** | Fixed scoring algorithm | LLM-powered clinical reasoning |
| **Output** | Deterministic numeric scores | Contextual explanations + scores |
| **Reasoning** | No reasoning explanation | Step-by-step clinical reasoning |
| **Risk Detection** | Limited to predefined rules | Identifies non-obvious risk factors |
| **Interaction** | Static dashboard only | Conversational chat interface |
| **Discharge Plans** | Template-based | Personalized, AI-generated narratives |
| **Patient Comparison** | Sort by score | AI-powered triage with rationale |
| **Adaptability** | Same output for same inputs | Context-aware, nuanced analysis |

### Why "AI Agent" and not just "AI"?

The system acts as an **autonomous clinical reasoning agent** that:

1. **Perceives** — Gathers and reads multi-resource FHIR patient data
2. **Reasons** — Applies clinical knowledge via LLM to interpret data patterns
3. **Acts** — Generates risk assessments, discharge plans, and triage recommendations
4. **Communicates** — Engages in natural language dialogue about patients
5. **Falls back gracefully** — Operates in rule-based mode when AI is unavailable

---

## 🤖 AI Agent Features

### 1. AI Clinical Chat Interface

A conversational interface where clinicians can ask questions about patients and receive AI-powered responses grounded in FHIR data.

**Example interactions:**
- *"What are the main readmission risk factors for this patient?"*
- *"Should I be concerned about medication interactions?"*
- *"Compare readmission risk across my ICU patients"*
- *"Generate a discharge plan focusing on cardiac care"*

The chat maintains conversation history, supports patient context switching, and suggests clinically relevant questions.

### 2. AI-Powered Patient Analysis

Performs deep clinical analysis using GPT-4:

- **Hybrid risk scoring**: AI confidence score alongside rule-based score
- **Step-by-step reasoning**: Shows the AI's clinical reasoning process
- **Key insights**: AI-identified risk factors and clinical observations
- **Missed risks**: Flags risks that the rule-based engine alone would not catch
- **Personalized recommendations**: Context-aware action items

### 3. AI Discharge Plan Generation

Generates comprehensive, personalized discharge plans using LLM reasoning:

- Medication reconciliation with interaction awareness
- Follow-up scheduling based on clinical priorities
- Patient-friendly instructions in plain language
- Risk-specific interventions and precautions

### 4. Multi-Patient AI Comparison

Compares multiple patients simultaneously for triage prioritization:

- **Risk ranking**: AI-ordered list by clinical urgency
- **Common risk factors**: Shared patterns across patients
- **Unique concerns**: Patient-specific flags
- **Triage recommendation**: AI-generated prioritization rationale

### 5. Graceful Degradation

When `OPENAI_API_KEY` is not configured or the AI service is unavailable:

- System automatically falls back to **rule-based mode**
- All core features remain functional
- UI clearly indicates "AI Fallback" status
- No disruption to clinical workflows

---

## 🏗️ AI Agent Architecture

### System Architecture with AI Layer

```
┌─────────────────────────────────────────────────────────────────┐
│                     Frontend (React 18)                         │
│  ┌─────────────────┐  ┌──────────────────┐  ┌───────────────┐ │
│  │ Patient Dashboard│  │ AI Chat Interface │  │ AI Comparison │ │
│  │ + AI Analysis    │  │ + Context Select  │  │ + Triage View │ │
│  └────────┬────────┘  └────────┬─────────┘  └──────┬────────┘ │
└───────────┼─────────────────────┼───────────────────┼──────────┘
            │ REST API            │                    │
┌───────────┴─────────────────────┴───────────────────┴──────────┐
│              Backend API (FastAPI / Python)                     │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  API Layer (routes.py)                                   │   │
│  │  /ai/chat  /ai/status  /ai/compare-patients              │   │
│  │  /patients/{id}/ai-analysis  /patients/{id}/ai-discharge │   │
│  └──────────┬──────────────────────────────────┬───────────┘   │
│             │                                   │               │
│  ┌──────────┴──────────┐  ┌────────────────────┴───────────┐  │
│  │  🤖 AI Agent Service │  │  📊 Rule-Based Services        │  │
│  │  (ai_agent_service)  │  │  (risk_calculator,             │  │
│  │  - LLM Reasoning     │  │   care_plan_generator,         │  │
│  │  - Prompt Engineering│  │   fhir_service)                │  │
│  │  - Chat Management   │  │  - Deterministic Scoring       │  │
│  │  - FHIR Data Gather  │  │  - Template Plans              │  │
│  └──────────┬──────────┘  └────────────────────┬───────────┘  │
│             │                                   │               │
│  ┌──────────┴───────────────────────────────────┴───────────┐  │
│  │  Core Layer                                               │  │
│  │  - FHIR Client (HTTP) · Configuration · OpenAI Client     │  │
│  └──────────────────────────┬────────────────────────────────┘  │
└─────────────────────────────┼───────────────────────────────────┘
          FHIR API (HTTP)     │          OpenAI API (HTTPS)
┌─────────────────────────────┴────────┐  ┌────────────────────┐
│  InterSystems IRIS for Health        │  │  OpenAI GPT-4      │
│  - FHIR Server (R4)                 │  │  - Clinical LLM    │
│  - Resource Storage                  │  │  - Chat Completion │
│  - FHIR SQL Builder                 │  │  - Reasoning Engine │
└──────────────────────────────────────┘  └────────────────────┘
```

### AI Agent Interaction Flow

```
User Question ──► AI Agent Service
                      │
                      ├── 1. Gather FHIR Data (Patient, Encounters,
                      │      Conditions, Medications, Observations)
                      │
                      ├── 2. Build Clinical Context Prompt
                      │      (structured patient summary + clinical rules)
                      │
                      ├── 3. Call GPT-4 with System + User prompts
                      │
                      ├── 4. Parse LLM Response
                      │      (risk level, insights, reasoning, recommendations)
                      │
                      └── 5. Return Hybrid Result
                             (AI analysis + rule-based baseline for comparison)
```

### Graceful Degradation Flow

```
Request ──► Check AI Availability
                │
          ┌─────┴──────┐
          │ AI Available│ ──► Full AI Analysis + Rule-based baseline
          └─────┬──────┘
                │ No
                ▼
          Rule-based Fallback ──► Deterministic scoring only
          (UI shows "Fallback" badge)
```

---

## 🏆 Contest Alignment

### InterSystems Programming Contest: AI Agents for FHIR 2026

**Contest Task**: #9 — Hospital Readmission Risk Workbench

#### Requirements — ALL MET ✅

| Requirement | Status | Implementation |
|-------------|--------|----------------|
| **AI Agent for FHIR** | ✅ **TRUE AI AGENT** | GPT-4 LLM with clinical reasoning over FHIR data |
| **FHIR Resources** | ✅ | Patient, Encounter, Condition, Observation, MedicationRequest, AllergyIntolerance, CarePlan, Task |
| **Platform Features** | ✅ | FHIR API, FHIR SQL Builder, AI Hub (LLM integration) |
| **MVP Criteria** | ✅ | Rule-based + AI risk scoring, Task-based interventions |
| **Conversational AI** | ✅ | Chat interface with patient context and clinical dialogue |
| **Explainable AI** | ✅ | Step-by-step reasoning, insight attribution, confidence scores |

#### Nice Twists 🎯

- **Hybrid Intelligence**: AI Agent + Rule Engine working together
- **Multi-patient triage**: AI-powered comparison and prioritization
- **Graceful degradation**: Works without API key (rule-based fallback)
- **Risk gap detection**: AI identifies what rules miss
- **Population health dashboard** with AI status monitoring

---

## ✨ Features

### Primary: AI-Powered Clinical Analysis

| Feature | Description |
|---------|-------------|
| **AI Clinical Chat** | Conversational interface for clinical queries about patients |
| **AI Risk Analysis** | LLM-powered deep analysis with reasoning steps |
| **AI Discharge Plans** | Personalized, AI-generated discharge narratives |
| **AI Patient Comparison** | Multi-patient triage with AI prioritization |
| **AI Status Monitoring** | Real-time AI availability indicator in UI |

### Baseline: Evidence-Based Rule Engine

| Feature | Description |
|---------|-------------|
| **Multi-Factor Risk Scoring** | 6-factor weighted algorithm (admissions, conditions, medications, age, follow-up, vitals) |
| **Risk Stratification** | HIGH (≥70%) / MODERATE (40-69%) / LOW (<40%) |
| **Automated Discharge Plans** | Template-based FHIR CarePlan + Task generation |
| **Clinical Dashboard** | Patient list sorted by risk, population statistics |
| **FHIR Compliance** | Full R4 read/write with InterSystems IRIS |

### Dashboard & UI

- **Tabbed navigation**: Dashboard view + AI Chat view
- **AI Analysis modal**: Side-by-side rule-based vs AI comparison
- **Score comparison cards**: Visual comparison of AI vs rule-based scores
- **Reasoning steps display**: Transparent AI decision process
- **Missed risks panel**: Risks caught by AI but not by rules
- **Patient context selector**: Choose patient context for chat
- **Suggested questions**: Clinically relevant quick-start queries

---

## 🧮 Risk Assessment Algorithm

### Hybrid Approach

The system uses a **two-layer** risk assessment:

1. **Rule-Based Score** — Deterministic, weighted factor calculation
2. **AI Agent Score** — LLM analysis with clinical reasoning

Both scores are presented side-by-side for clinical transparency.

### Rule-Based Risk Score Calculation

```python
risk_score = Σ (factor_value × factor_weight)
```

#### Risk Factors

| Factor | Weight | Description |
|--------|--------|-------------|
| Recent Admissions | 25% | Hospitalizations in last 6 months |
| High-Risk Conditions | 20% | Heart failure, COPD, diabetes, CKD |
| Polypharmacy | 15% | Number of active medications |
| Age Factor | 15% | Increased risk for elderly patients |
| Follow-up Adherence | 15% | Gaps in care continuity |
| Abnormal Vital Signs | 10% | Recent concerning measurements |

#### Risk Stratification

| Level | Threshold | Action |
|-------|-----------|--------|
| **HIGH** | ≥ 70% | Intensive discharge support, follow-up within 7 days |
| **MODERATE** | 40–69% | Standard discharge protocol, follow-up within 14 days |
| **LOW** | < 40% | Basic discharge instructions, follow-up within 30 days |

### AI Agent Enhancement

The AI Agent adds value beyond rule-based scoring by:

- Identifying **comorbidity interactions** not captured by individual risk factors
- Detecting **social/behavioral risk patterns** from clinical notes context
- Providing **clinical reasoning explanations** for each risk assessment
- Flagging **risks that rules miss** (e.g., medication interaction risks, psychosocial factors)
- Generating **confidence scores** reflecting certainty of AI analysis

---

## 📡 API Documentation

### Base URL

```
http://localhost:8000/api/v1
```

### AI Agent Endpoints 🤖

#### AI Status Check
```http
GET /api/v1/ai/status
```

Response:
```json
{
  "ai_available": true,
  "model": "gpt-4o",
  "features": {
    "chat": true,
    "patient_analysis": true,
    "discharge_planning": true,
    "patient_comparison": true
  },
  "mode": "ai-powered"
}
```

#### AI Clinical Chat
```http
POST /api/v1/ai/chat
```

Request:
```json
{
  "message": "What are the main readmission risk factors for this patient?",
  "patient_id": "patient-001",
  "conversation_history": []
}
```

Response:
```json
{
  "response": "Based on the FHIR data for this patient, the key readmission risk factors are...",
  "sources": ["Patient", "Encounter", "Condition", "MedicationRequest"],
  "patient_ids_referenced": ["patient-001"],
  "confidence": 0.87,
  "ai_powered": true
}
```

#### AI Patient Analysis
```http
GET /api/v1/patients/{patient_id}/ai-analysis
```

Response:
```json
{
  "patient_id": "1",
  "patient_name": "Barbara Miller",
  "ai_risk_level": "HIGH",
  "ai_confidence_score": 0.85,
  "rule_based_score": 0.76,
  "ai_insights": [
    "Multiple cardiac comorbidities increase interaction risk",
    "Recent admission pattern suggests inadequate discharge planning"
  ],
  "reasoning_steps": [
    {
      "step": 1,
      "action": "Reviewed encounter history",
      "finding": "3 admissions in 6 months",
      "clinical_relevance": "Strong predictor of readmission"
    }
  ],
  "recommendations": [
    "Cardiac rehabilitation program referral",
    "Home health nursing for medication management"
  ],
  "risks_missed_by_rules": [
    "Potential medication interaction between metformin and contrast agents"
  ],
  "analysis_timestamp": "2026-05-22T19:07:08.319427",
  "model_used": "gpt-4o"
}
```

#### AI Patient Comparison
```http
POST /api/v1/ai/compare-patients
```

Request:
```json
{
  "patient_ids": ["patient-001", "patient-002", "patient-003"]
}
```

Response:
```json
{
  "patient_ids": ["patient-001", "patient-002", "patient-003"],
  "comparison_summary": "Triage analysis of 3 patients...",
  "risk_ranking": [
    {"patient_id": "patient-001", "rank": 1, "rationale": "Highest acuity..."}
  ],
  "common_risk_factors": ["Age > 65", "Polypharmacy"],
  "unique_concerns": {"patient-001": ["Recent cardiac event"]},
  "triage_recommendation": "Prioritize patient-001 for intensive discharge planning",
  "ai_powered": true
}
```

#### AI Discharge Plan
```http
POST /api/v1/patients/{patient_id}/ai-discharge-plan
```

Response:
```json
{
  "patient_id": "22",
  "discharge_plan": "## Personalized Discharge Plan\n\n### Medications\n...",
  "ai_powered": true,
  "model_used": "gpt-4o"
}
```

### Core Endpoints 📊

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/health` | Health check |
| `GET` | `/api/v1/patients` | List all patients with risk scores |
| `GET` | `/api/v1/patients/{id}` | Get patient details |
| `GET` | `/api/v1/patients/{id}/risk-assessment` | Rule-based risk assessment |
| `POST` | `/api/v1/patients/{id}/discharge-plan` | Generate rule-based discharge plan |
| `GET` | `/api/v1/statistics` | Population statistics |
| `GET` | `/api/v1/patients/{id}/summary?role=` | Role-based AI patient summary (doctor/patient/caregiver/care_manager) |
| `POST` | `/api/v1/ai/nl-to-sql` | Natural language to SQL query translation |
| `GET` | `/api/v1/analytics/sql-stats` | FHIR SQL Builder analytics stats |
| `GET` | `/api/v1/analytics/readmission-sql` | SQL-based readmission analytics |
| `GET` | `/api/v1/analytics/sql-builder-info` | FHIR SQL Builder feature info |

### Interactive API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 🚀 Installation

### Prerequisites

- **Docker** (v20.10+) with at least **6 GB RAM** allocated to Docker
- **Docker Compose** (v2.0+)
- **Git**
- **Python 3.8+** with `pip` (for data loading script)
- **OpenAI API Key** (optional — system works in rule-based fallback mode without it)

> **Important**: InterSystems IRIS for Health requires significant memory during FHIR schema installation. Ensure Docker has at least 6 GB RAM available. The `config/iris/merge.cpf` file already sets `globals=256` to allocate 256 MB for IRIS globals buffer.

### Installation Steps

#### 1. Clone the Repository

```bash
git clone https://github.com/kcedd34/smart-discharge-navigator.git
cd smart-discharge-navigator
```

#### 2. Configure Environment (Optional — AI Features)

The system works fully without an API key in **rule-based fallback mode**. To enable AI features, create a `.env` file in the project root:

```bash
# .env  (never commit this file — it is already in .gitignore)
OPENAI_API_KEY=sk-your-key-here
AI_MODEL=gpt-4o
AI_ENABLED=true
```

> **Important**: Use `gpt-4o` (or `gpt-4-turbo`) — not `gpt-4` base. The base `gpt-4` model does not support JSON mode (`response_format=json_object`), which is required for structured clinical analysis, and will fall back to rule-based mode.

Alternatively, export the key in the shell before `docker-compose up`:

```bash
# Linux / macOS
export OPENAI_API_KEY=sk-your-key-here

# Windows PowerShell
$env:OPENAI_API_KEY = "sk-your-key-here"
```

#### 3. Start All Services

```bash
# Recommended: use the automated start script
./start.sh
```

The script handles everything: starts containers, waits for IRIS to become healthy, installs the FHIR R4 endpoint, and loads sample data.

**On Windows** (without WSL), run manually:

```bash
docker-compose up -d
```

Then follow Steps 4 and 5 below.

---

#### Manual Installation (if `start.sh` is not available)

**Step 3a — Start containers**

```bash
docker-compose up -d
```

This starts three services:
- **IRIS for Health** — Port 52773 (FHIR Server + Management Portal)
- **Backend API** — Port 8000 (FastAPI + AI Agent)
- **Frontend** — Port 3000 (React app)

**Step 3b — Wait for IRIS to become healthy**

IRIS requires 2–5 minutes to fully initialise. Wait until the healthcheck passes:

```bash
docker inspect --format='{{.State.Health.Status}}' smart-discharge-iris
# Wait until the output is: healthy
```

**Step 3c — Install the FHIR R4 Endpoint**

> **This step is mandatory on first run and after `docker-compose down` (data reset).** The FHIR endpoint is not pre-configured in the image — it must be installed into IRIS using ObjectScript.

```bash
# Linux / macOS / WSL
docker cp config/iris/install_fhir.txt smart-discharge-iris:/tmp/install_fhir.txt
docker exec -i smart-discharge-iris bash -c 'iris session IRIS -U HSSYS < /tmp/install_fhir.txt'
```

```powershell
# Windows PowerShell
docker cp config\iris\install_fhir.txt smart-discharge-iris:/tmp/install_fhir.txt
docker exec -i smart-discharge-iris bash -c 'iris session IRIS -U HSSYS < /tmp/install_fhir.txt'
```

**Expected output** (success indicators):
```
HSCUSTOM already registered   ← or "ConfigItem save sc=1" on first run
Saving hl7.fhir.r3.core@3.0.2 ← package data loading (may take 2-5 minutes)
Saving hl7.fhir.r5.core@5.0.0
...
/fhir/r4 already installed     ← or "InstallInstance sc=1" on first run
Done - EndpointExists:1        ← endpoint installed successfully
```

**Step 3d — Configure CSP gateway routing and authentication**

This step is **required** on every fresh container install. The embedded IRIS web gateway (httpd) needs to be told that `/fhir` requests should be forwarded to IRIS, and the IRIS security settings must allow HTTP Basic auth on the FHIR endpoint.

```bash
docker cp config/iris/setup_fhir_post_install.sh smart-discharge-iris:/tmp/setup_fhir_post_install.sh
docker exec smart-discharge-iris bash /tmp/setup_fhir_post_install.sh
```

This script:
1. Adds `/fhir` to the CSP gateway routing table (`CSP.ini`) — without this, all `/fhir/r4/*` URLs return `404 Not Found`
2. Reloads/restarts the embedded httpd to pick up the new routing
3. Sets `SuperUser` authentication to HTTP Basic with password `SYS`
4. Sets the `/fhir/r4` CSP application to accept HTTP Basic + delegated auth (`AutheEnabled=96`)

**Verify the FHIR endpoint is working:**
```bash
curl http://localhost:52773/fhir/r4/metadata
# Should return a large JSON CapabilityStatement (resourceType: "CapabilityStatement")
```

#### 4. Load Sample Data

```bash
pip install requests
python3 data/load_sample_data.py
```

This creates 8 synthetic patients categorised by risk level:
- **3 HIGH risk** — elderly patients with multiple chronic comorbidities (heart failure, COPD, CKD)
- **3 MODERATE risk** — patients with 2 chronic conditions and recent encounters
- **2 LOW risk** — younger patients with a single condition

#### 5. Access the Application

| Service | URL | Credentials |
|---------|-----|-------------|
| **Application** | http://localhost:3000 | — |
| **AI Chat** | http://localhost:3000 | Click "AI Chat" tab |
| **Backend API** | http://localhost:8000 | — |
| **Swagger Docs** | http://localhost:8000/docs | — |
| **IRIS Portal** | http://localhost:52773/csp/sys/UtilHome.csp | SuperUser / SYS |
| **FHIR Endpoint** | http://localhost:52773/fhir/r4/metadata | — (no auth for GET) |

---

### Re-running After a Restart

If Docker containers are **stopped and restarted** (without `docker-compose down`), the FHIR endpoint persists and no reinstallation is needed. However, the CSP gateway routing and authentication configuration **must be re-applied** after every container restart, because the CSP.ini changes made inside the container are ephemeral:

```bash
docker-compose up -d

# Re-apply CSP gateway + auth configuration (required after every restart)
docker cp config/iris/setup_fhir_post_install.sh smart-discharge-iris:/tmp/setup_fhir_post_install.sh
docker exec smart-discharge-iris bash /tmp/setup_fhir_post_install.sh
```

> **Tip**: The `start.sh` script handles this automatically — use it instead of running `docker-compose up -d` directly.

If the containers are **destroyed** (`docker-compose down`), the IRIS data is lost and the full installation (Steps 3b–3d) must be repeated.

---

### Docker Compose Image Version

The `docker-compose.yml` uses `intersystemsdc/irishealth-community:latest`. This application was developed and tested with `irishealth-community:2026.1.0.235.2`. If you encounter issues with a newer image, pin the version:

```yaml
image: intersystemsdc/irishealth-community:2026.1.0.235.2
```

---

## ⚙️ Environment Variables

Environment variables are set directly in `docker-compose.yml`. The file ships with sensible defaults — the only variable you need to supply is `OPENAI_API_KEY` for AI features.

### Key Variables in `docker-compose.yml`

```yaml
environment:
  # FHIR / IRIS connection
  - FHIR_BASE_URL=http://iris:52773/fhir/r4
  - IRIS_USERNAME=SuperUser
  - IRIS_PASSWORD=SYS

  # CORS — must be a JSON array (pydantic-settings v2 requirement)
  - CORS_ORIGINS=["http://localhost:3000","http://localhost:3001"]

  # AI Agent (optional) — set values in .env file (recommended) or in shell
  - OPENAI_API_KEY=${OPENAI_API_KEY:-}
  - AI_MODEL=${AI_MODEL:-gpt-4o}    # gpt-4o required for JSON mode support
  - AI_ENABLED=${AI_ENABLED:-true}
```

> **CORS format**: `CORS_ORIGINS` must be a valid JSON array string. A plain URL like
> `CORS_ORIGINS=http://localhost:3000` will cause a pydantic parse error and prevent the
> backend from starting.

### Full Variable Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `FHIR_BASE_URL` | Yes | `http://iris:52773/fhir/r4` | Internal FHIR endpoint (container-to-container) |
| `IRIS_USERNAME` | Yes | `SuperUser` | IRIS user for authenticated FHIR writes |
| `IRIS_PASSWORD` | Yes | `SYS` | IRIS user password |
| `CORS_ORIGINS` | Yes | `["http://localhost:3000","http://localhost:3001"]` | Allowed CORS origins (JSON array) |
| `OPENAI_API_KEY` | No | _(empty)_ | OpenAI key. Without it, system runs in rule-based fallback mode. Set via `.env` file (recommended) |
| `AI_MODEL` | No | `gpt-4o` | LLM model. Use `gpt-4o` or `gpt-4-turbo` — base `gpt-4` does not support JSON mode and will cause AI to fall back to rule-based mode |
| `AI_TEMPERATURE` | No | `0.3` | Sampling temperature (lower = more deterministic) |
| `AI_MAX_TOKENS` | No | `2000` | Maximum tokens in AI response |
| `AI_ENABLED` | No | `true` | Master toggle for AI features |
| `HIGH_RISK_THRESHOLD` | No | `0.7` | Score threshold for HIGH risk classification |
| `MODERATE_RISK_THRESHOLD` | No | `0.4` | Score threshold for MODERATE risk classification |

---

## 📖 Usage

### AI Chat Interface

1. Click **"🤖 AI Chat"** tab in the navigation
2. Select a patient from the sidebar (optional — for patient-specific queries)
3. Type a clinical question or select a suggested question
4. View AI response with FHIR data sources cited

### AI Patient Analysis

1. In the Dashboard, click **"🤖 AI Analysis"** on any patient
2. View side-by-side comparison: Rule-based score vs AI score
3. Read through AI reasoning steps
4. Review risks missed by rules
5. Act on AI recommendations

### AI Discharge Planning

1. Click **"🤖 AI Discharge Plan"** for any patient
2. Review AI-generated personalized plan
3. Plan includes medications, follow-ups, patient instructions

### Multi-Patient Comparison

1. Enable **"Compare Patients"** mode in the dashboard
2. Select 2+ patients
3. Click **"AI Compare"**
4. View AI-generated triage ranking and recommendations

### Rule-Based Dashboard (Baseline)

1. View all patients sorted by risk score
2. Click **"View Risk"** for detailed factor breakdown
3. Click **"Generate Plan"** for template-based discharge plan

---

## 🔗 FHIR Resources

### Resources Used (Read)

| Resource | Purpose | AI Agent Usage |
|----------|---------|----------------|
| **Patient** | Demographics, age | Context for AI reasoning |
| **Encounter** | Admission history | Pattern analysis by AI |
| **Condition** | Active diagnoses | Comorbidity reasoning |
| **Observation** | Vital signs, labs | Trend detection by AI |
| **MedicationRequest** | Active medications | Interaction analysis |
| **AllergyIntolerance** | Drug/food allergies | Allergy-aware discharge planning |

### Resources Created (Write)

| Resource | Purpose |
|----------|---------|
| **CarePlan** | Structured discharge plan (rule-based + AI-enhanced) |
| **Task** | Discharge checklist items |

---

## 🏛️ InterSystems Platform Features Usage

### FHIR SQL Builder — SQL Analytics over FHIR Resources

The application leverages the **FHIR SQL Builder** built into InterSystems IRIS for Health to run standard SQL queries directly against FHIR resource projections. Instead of parsing JSON bundles in application code, the backend executes analytical SQL via the IRIS REST SQL endpoint.

**How it works:**
1. IRIS FHIR SQL Builder automatically creates SQL projections for every stored FHIR resource during `InstallInstance`. The schema is named `HSFHIR_X000x_S` where `x` is the installation sequence number (e.g., `HSFHIR_X0001_S` on a clean first install, `HSFHIR_X0008_S` if reinstalled several times).
2. The backend service (`fhir_sql_analytics.py`) sends SQL queries to IRIS via `POST /api/atelier/v1/{namespace}/_query/sql`.
3. Results come back as tabular data — ready for dashboards, aggregations, and JOINs across resources.

> The SQL examples below use `HSFHIR_X0001_S` as a representative first-install schema name.

**Example SQL queries executed:**

```sql
-- Patient demographics distribution
SELECT Age_group, Gender, COUNT(*) as patient_count
FROM HSFHIR_X0001_S.Patient
GROUP BY Age_group, Gender

-- Multi-resource JOIN: encounter frequency per patient
SELECT p.Key as patient_id, COUNT(e.Key) as encounter_count
FROM HSFHIR_X0001_S.Patient p
JOIN HSFHIR_X0001_S.Encounter e ON e.subject = p.Key
GROUP BY p.Key
ORDER BY encounter_count DESC

-- 3-table JOIN: high-risk population analysis
SELECT p.Key, c.code, e.status
FROM HSFHIR_X0001_S.Patient p
JOIN HSFHIR_X0001_S.Condition c ON c.subject = p.Key
JOIN HSFHIR_X0001_S.Encounter e ON e.subject = p.Key
WHERE c.code IN ('44054006','73211009','38341003')

-- Readmission candidates via encounter history
SELECT subject as patient_id, COUNT(*) as admissions
FROM HSFHIR_X0001_S.Encounter
WHERE status = 'finished'
GROUP BY subject
HAVING COUNT(*) > 1

-- Polypharmacy analysis (5+ active medications)
SELECT subject as patient_id, COUNT(*) as med_count
FROM HSFHIR_X0001_S.MedicationRequest
WHERE status = 'active'
GROUP BY subject
HAVING COUNT(*) >= 5
```

**API Endpoints:**
| Endpoint | Description |
|----------|-------------|
| `GET /analytics/sql-stats` | Population-level analytics via FHIR SQL Builder |
| `GET /analytics/readmission-sql` | Readmission candidates identified by SQL |
| `GET /analytics/sql-builder-info` | Platform feature info and query catalog |

### AI Hub Integration — LLM-Powered Clinical Intelligence

The AI layer follows the **InterSystems AI Hub** integration pattern, providing a clean abstraction for LLM access that is compatible with the IRIS AI ecosystem:

```
┌─────────────────────────────────┐
│     Smart Discharge Navigator   │
│         (FastAPI Backend)       │
├─────────────────────────────────┤
│   AIAgentService                │
│   ├─ OpenAI-compatible API ←────── AI Hub pattern (model gateway)
│   ├─ Structured clinical prompts│
│   ├─ FHIR context injection     │
│   └─ Graceful degradation       │
├─────────────────────────────────┤
│   InterSystems IRIS for Health  │
│   ├─ FHIR Repository (R4)      │
│   ├─ FHIR SQL Builder          │
│   └─ IntegratedML (production)  │
└─────────────────────────────────┘
```

**Key design decisions:**
- Uses **OpenAI-compatible API** — the same interface that InterSystems AI Hub exposes for registered models
- **Structured clinical prompts** inject FHIR data context (Patient, Encounter, Condition, Observation, MedicationRequest) for evidence-based AI reasoning
- **Graceful degradation** — the system operates fully without AI, falling back to the rule-based risk engine

### Dashboards — React Analytics UI

The React frontend includes a dedicated **Analytics Dashboard** tab that visualizes data from the FHIR SQL Builder queries:
- Population risk distribution charts
- Readmission candidate lists
- Condition prevalence statistics
- Encounter frequency analysis

---

## 🛠️ Technology Stack

### AI Layer
- **LLM**: OpenAI GPT-4 (clinical reasoning engine)
- **Client**: OpenAI Python SDK (async)
- **Prompt Engineering**: Structured clinical prompts with FHIR data context

### Backend
- **Language**: Python 3.11
- **Framework**: FastAPI (async REST API)
- **FHIR Client**: httpx + custom wrapper
- **Validation**: Pydantic v2
- **AI Integration**: openai >= 1.0.0, tiktoken

### Frontend
- **Framework**: React 18
- **HTTP Client**: Axios
- **UI**: Custom CSS with AI chat interface
- **Features**: Tabbed navigation, AI modals, comparison view

### FHIR Server
- **Platform**: InterSystems IRIS for Health Community Edition
- **FHIR Version**: R4
- **Container**: `intersystemsdc/irishealth-community:latest`

### Infrastructure
- **Containerization**: Docker + Docker Compose
- **Orchestration**: Docker Compose 3.8

---

## 🛠️ Development

### Project Structure

```
smart-discharge-navigator/
├── backend/
│   ├── app/
│   │   ├── core/
│   │   │   ├── config.py              # Config (incl. AI settings)
│   │   │   └── fhir_client.py         # FHIR API wrapper
│   │   ├── models/
│   │   │   └── patient.py             # Models (incl. AI models)
│   │   ├── services/
│   │   │   ├── ai_agent_service.py    # 🤖 AI Agent (NEW)
│   │   │   ├── risk_calculator.py     # Rule-based scoring
│   │   │   ├── care_plan_generator.py # Discharge planning
│   │   │   └── fhir_service.py        # FHIR orchestration
│   │   └── api/
│   │       └── routes.py              # API endpoints (incl. AI)
│   ├── main.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── App.js                     # React app (incl. AI Chat)
│   │   ├── index.js
│   │   └── index.css                  # Styles (incl. AI UI)
│   ├── public/
│   ├── package.json
│   └── Dockerfile
├── data/
│   └── load_sample_data.py
├── .env.example                        # Environment template
├── docker-compose.yml
├── start.sh
├── AI_AGENT_GUIDE.md                   # 🤖 AI Agent documentation
├── ARCHITECTURE.md
└── README.md
```

### Running Locally (Development Mode)

#### Backend

```bash
cd backend
pip install -r requirements.txt

# Set AI configuration
export OPENAI_API_KEY=sk-your-key-here

uvicorn main:app --reload --port 8000
```

#### Frontend

```bash
cd frontend
npm install
npm start
```

---

## 🎥 Demo Video

### Video Script

**Duration**: 5–7 minutes

1. **Introduction** (30s) — Problem: hospital readmissions. Solution: AI Agent for FHIR
2. **AI Agent Demo** (2 min) — Show AI Chat, ask clinical questions, demonstrate patient context
3. **AI Analysis** (1.5 min) — Side-by-side AI vs rule-based comparison, reasoning steps, missed risks
4. **AI Discharge Plan** (1 min) — Generate personalized AI discharge plan
5. **Multi-Patient Comparison** (1 min) — AI triage of multiple patients
6. **Rule-Based Baseline** (30s) — Show the deterministic scoring underneath
7. **Architecture & Contest Fit** (30s) — Hybrid architecture, FHIR compliance, contest alignment

### Key Demo Points

- Show the **AI Status badge** (Active vs Fallback)
- Demonstrate **conversation memory** in AI Chat
- Highlight **"Risks Missed by Rules"** section
- Show **graceful fallback** by toggling `AI_ENABLED=false`

---

## 📄 License

MIT License — see [LICENSE](LICENSE)

---

## �‍💻 Author

**Carlos Eduardo Dias Duarte**
- Email: [kcedd34@gmail.com](mailto:kcedd34@gmail.com)
- GitHub: [@kcedd34](https://github.com/kcedd34)

---

## 🙏 Acknowledgments

- **InterSystems** — IRIS for Health Community Edition and FHIR support
- **OpenAI** — GPT-4o powering the clinical reasoning agent
- **HL7 FHIR** — Fast Healthcare Interoperability Resources standard
- **Contest Organizers** — For the opportunity to build meaningful healthcare AI

---

## 🚦 Troubleshooting

### IRIS / FHIR Issues

#### FHIR endpoint returns 404 — "CSP application path not in CSP gateway"

This is the most common 404 cause on a fresh install. The IRIS embedded web gateway (httpd) does not know to route `/fhir` requests to IRIS unless `/fhir` is listed in `CSP.ini`. Run the post-install setup script to fix this:

```bash
docker cp config/iris/setup_fhir_post_install.sh smart-discharge-iris:/tmp/setup_fhir_post_install.sh
docker exec smart-discharge-iris bash /tmp/setup_fhir_post_install.sh
```

Verify:
```bash
curl http://localhost:52773/fhir/r4/metadata
# Expected: 200 with CapabilityStatement JSON
```

#### FHIR endpoint returns 404 — endpoint not installed

If the FHIR R4 endpoint was never installed (e.g. first run or after `docker-compose down`), install it:

```bash
docker cp config/iris/install_fhir.txt smart-discharge-iris:/tmp/install_fhir.txt
docker exec -i smart-discharge-iris bash -c 'iris session IRIS -U HSSYS < /tmp/install_fhir.txt'
```

Wait 3–8 minutes for class compilation to complete, then run the post-install setup:
```bash
docker cp config/iris/setup_fhir_post_install.sh smart-discharge-iris:/tmp/setup_fhir_post_install.sh
docker exec smart-discharge-iris bash /tmp/setup_fhir_post_install.sh
```

#### FHIR write (POST/PUT) returns HTTP 500 with "PROPERTY DOES NOT EXIST"

This means the FHIR search index classes were not fully generated during installation. The error looks like:
```
<PROPERTY DOES NOT EXIST>AddToSearchTableEntry *family,HSFHIR.X000x.S.Patient
```

Fix: uninstall and reinstall the FHIR endpoint. Run this in an IRIS session:

```objectscript
// In HSSYS namespace — uninstall then reinstall via the install script
// Step 1: Uninstall
set sc = ##class(HS.FHIRServer.Installer).UninstallInstance("/fhir/r4")
write "Uninstall sc=",sc,!

// Step 2: Re-run the install script (handles ConfigItem registration + namespace setup)
// Exit this session and run from shell:
// docker cp config/iris/install_fhir.txt smart-discharge-iris:/tmp/install_fhir.txt
// docker exec -i smart-discharge-iris bash -c 'iris session IRIS -U HSSYS < /tmp/install_fhir.txt'
```

Or simply re-run the install script (it will create a new schema version):
```bash
docker cp config/iris/install_fhir.txt smart-discharge-iris:/tmp/install_fhir.txt
docker exec -i smart-discharge-iris bash -c 'iris session IRIS -U HSSYS < /tmp/install_fhir.txt'
```

#### IRIS container exits or runs out of memory

IRIS needs at least 4 GB RAM. Confirm Docker resource limits and check that `config/iris/merge.cpf` contains:
```
[config]
globals=256,0,0,0,0,0
```

Check container health and logs:
```bash
docker inspect --format='{{.State.Health.Status}}' smart-discharge-iris
docker logs smart-discharge-iris --tail=50
```

#### FHIR GET works but POST returns 401 Unauthorised

Write operations require HTTP Basic Auth. The backend handles this automatically. If testing manually:
```bash
# Correct: include credentials for write operations
curl -u SuperUser:SYS -X POST http://localhost:52773/fhir/r4/Patient \
  -H "Content-Type: application/fhir+json" \
  -d '{"resourceType":"Patient","name":[{"family":"Test"}]}'

# Note: GET /fhir/r4/metadata works WITHOUT credentials (by design)
```

#### SuperUser login fails via Management Portal

The IRIS community image may set `ChangePassword=1` on the SuperUser account. Fix via ObjectScript:

```bash
echo 'set props("ChangePassword")=0
do ##class(Security.Users).Modify("SuperUser",.props)
halt' | docker exec -i smart-discharge-iris bash -c 'iris session IRIS -U %SYS'
```

Then log in at http://localhost:52773/csp/sys/UtilHome.csp with `SuperUser` / `SYS`.

---

### Backend Issues

#### Backend fails to start — "error parsing value for field CORS_ORIGINS"

The `CORS_ORIGINS` variable must be a JSON array. In `docker-compose.yml`, ensure:
```yaml
- CORS_ORIGINS=["http://localhost:3000","http://localhost:3001"]
```
A plain URL string (`CORS_ORIGINS=http://localhost:3000`) will cause a pydantic-settings v2 parse error.

#### Backend can't connect to IRIS

```bash
docker-compose ps         # check all containers are running
docker-compose logs iris  # look for IRIS startup errors
docker-compose logs backend --tail=30
```

The backend connects to IRIS using the internal Docker hostname `iris` (not `localhost`).
This is set via `FHIR_BASE_URL=http://iris:52773/fhir/r4` in `docker-compose.yml`.

---

### Sample Data Loading Issues

#### "Expecting value: line 1 column 1 (char 0)" when loading data

IRIS returns HTTP 201 Created with an **empty response body** for successful resource creations. The sample data loader (`data/load_sample_data.py`) handles this by extracting the new resource ID from the `Location` response header. If you see this error on an old copy of the script, update from the repository.

#### Data loader runs but patients show no conditions/encounters

This means patient creation succeeded but linked resource creation failed. Check that the FHIR endpoint accepts writes:
```bash
curl -s -o /dev/null -w "%{http_code}" -u SuperUser:SYS \
  -X POST http://localhost:52773/fhir/r4/Patient \
  -H "Content-Type: application/fhir+json" \
  -d '{"resourceType":"Patient","name":[{"family":"Test"}]}'
# Expected: 201
```

---

### AI Agent Issues

**AI features not working:**
```bash
# Check AI status endpoint
curl http://localhost:8000/api/v1/ai/status
```

**AI returns fallback responses:**
- Verify `OPENAI_API_KEY` is set — preferred method is a `.env` file in the project root
- Ensure `AI_MODEL=gpt-4o` (or `gpt-4-turbo`) — base `gpt-4` does **not** support JSON mode and silently falls back to rule-based mode
- Check `AI_ENABLED=true` in `docker-compose.yml`
- Review backend logs: `docker-compose logs backend`

**Discharge plan button shows "Failed to generate discharge plan" (HTTP 500):**

IRIS returns HTTP 201 with an **empty response body** when creating FHIR resources such as `CarePlan` and `Task`. If you see `JSONDecodeError: Expecting value: line 1 column 1 (char 0)` in backend logs, the `create_resource()` method in `fhir_client.py` is calling `.json()` on an empty body. The fix extracts the resource ID from the `Location` response header instead. Ensure you are running the latest code:
```bash
docker-compose up -d --no-deps --force-recreate backend
```

**Frontend shows CORS errors:**
CORS errors on the frontend are almost always caused by a backend 500 error — the backend does not emit CORS headers on error responses. Fix the underlying backend error first (check `docker-compose logs backend`), then the CORS error resolves automatically.
```bash
# Verify CORS_ORIGINS matches frontend URL
# Must be JSON array: CORS_ORIGINS=["http://localhost:3000","http://localhost:3001"]
```

**Sample data fails to load:**
```bash
# Ensure IRIS has fully started (wait 60 seconds)
sleep 60
python3 data/load_sample_data.py
```

---

**Built with ❤️ and 🤖 by [Carlos Eduardo Dias Duarte](mailto:kcedd34@gmail.com) for InterSystems Programming Contest: AI Agents for FHIR 2026**
