# Smart Discharge Navigator 🏥🤖

**AI-Powered Clinical Reasoning Agent for Hospital Readmission Risk Assessment**

[![InterSystems Contest](https://img.shields.io/badge/InterSystems-AI%20Agents%20for%20FHIR%202026-blue)](https://community.intersystems.com/post/intersystems-programming-contest-ai-agents-fhir)
[![Task](https://img.shields.io/badge/Contest%20Task-%239%20Hospital%20Readmission%20Risk-green)](https://community.intersystems.com/post/intersystems-programming-contest-ai-agents-fhir)
[![AI Agent](https://img.shields.io/badge/AI%20Agent-OpenAI%20GPT--4o-blueviolet)](https://openai.com/)
[![FHIR](https://img.shields.io/badge/FHIR-R4-orange)](https://www.hl7.org/fhir/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Author**: Carlos Eduardo Dias Duarte | **Email**: kcedd34@gmail.com | **GitHub**: [@kcedd34](https://github.com/kcedd34/smart-discharge-navigator)

---

## 🚀 Quick Start

```bash
# 1. Clone repository
git clone https://github.com/kcedd34/smart-discharge-navigator.git
cd smart-discharge-navigator

# 2. (Optional) Enable AI features
echo "OPENAI_API_KEY=sk-your-key-here" > .env
echo "AI_MODEL=gpt-4o" >> .env

# 3. Start application
chmod +x start.sh
./start.sh
```

**Windows Users** (or if `start.sh` fails): see [Manual Installation](#method-2-manual-installation) below.

**Note**: Without `OPENAI_API_KEY`, the system runs in rule-based mode — fully functional, no AI features.

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Usage](#-usage)
- [API Reference](#-api-reference)
- [Contest Alignment](#-contest-alignment)
- [FHIR Resources](#-fhir-resources)
- [InterSystems Platform Features](#-intersystems-platform-features)
- [Technology Stack](#-technology-stack)
- [Development](#-development)
- [Demo Video](#-demo-video)
- [Environment Variables](#-environment-variables)
- [Troubleshooting](#-troubleshooting)
- [License](#-license)

---

## 🎯 Overview

**Smart Discharge Navigator** tackles hospital readmissions ($17B annual cost in US) through a **hybrid AI Agent + rule-based system** that:

- Analyzes FHIR patient data (Patient, Encounter, Condition, MedicationRequest, Observation, AllergyIntolerance)
- Provides **AI-powered clinical reasoning** (GPT-4o) with explainable insights
- Falls back to **deterministic rule-based scoring** when AI is unavailable
- Generates personalized discharge plans as FHIR CarePlan + Task resources
- Supports **conversational clinical queries** through an AI chat interface

### Hybrid Architecture

| Layer | Purpose | When Used |
|-------|---------|-----------|
| **AI Agent (GPT-4o)** | Deep clinical reasoning, identifies non-obvious risks, conversational interface | When `OPENAI_API_KEY` is configured |
| **Rule-Based Engine** | Evidence-based deterministic scoring (6 weighted factors) | Always (baseline + fallback) |

**Key Differentiator**: The AI Agent identifies risks missed by rules (medication interactions, comorbidity patterns, social determinants) while maintaining explainable step-by-step reasoning.

---

## ✨ Key Features

### AI Agent Capabilities (when enabled)

| Feature | Description |
|---------|-------------|
| **AI Clinical Chat** | Conversational interface for patient queries with FHIR data context |
| **AI Risk Analysis** | LLM-powered assessment with step-by-step clinical reasoning |
| **AI Discharge Plans** | Personalized, AI-generated discharge narratives |
| **AI Patient Comparison** | Multi-patient triage with AI prioritization rationale |
| **Graceful Degradation** | Auto-fallback to rule-based mode when AI is unavailable |

### Rule-Based Baseline (always available)

- **Multi-Factor Risk Scoring**: 6 weighted factors (admissions, conditions, medications, age, follow-up, vitals)
- **Risk Stratification**: HIGH (≥70%) / MODERATE (40–69%) / LOW (<40%)
- **Automated Discharge Plans**: Template-based FHIR CarePlan + Task generation
- **Population Dashboard**: Patient list sorted by risk score with statistics

### Technical Features

- **FHIR R4 Compliance**: Full read/write with InterSystems IRIS for Health
- **FHIR SQL Builder**: SQL analytics over FHIR resource projections
- **Interactive API Docs**: Swagger UI with all endpoints documented
- **React Dashboard**: Tabbed UI (Dashboard + AI Chat + Analytics)

---

## 📦 Prerequisites

| Requirement | Version | Notes |
|-------------|---------|-------|
| **Docker** | 20.10+ | Allocate **minimum 6 GB RAM** to Docker |
| **Docker Compose** | 2.0+ | |
| **Python** | 3.8+ | For sample data loading script |
| **Git** | Latest | |
| **OpenAI API Key** | — | **Optional** — enables AI features |

> **Critical**: InterSystems IRIS requires significant memory. Ensure Docker has at least 6 GB RAM allocated (Docker Desktop → Settings → Resources). The `config/iris/merge.cpf` file sets `globals=256` to allocate 256 MB for IRIS globals buffer.

---

## 🚀 Installation

> ⚠️ **`docker-compose up -d` alone is NOT sufficient.** It only starts the containers — the FHIR endpoint and sample data are **not** pre-installed in the image. Use `./start.sh` for a fully automatic setup (Linux/macOS), or follow Steps 5–7 manually (Windows users or if `start.sh` fails).

### Method 1: Automated Script (Recommended)

```bash
git clone https://github.com/kcedd34/smart-discharge-navigator.git
cd smart-discharge-navigator

# Optional: enable AI features
echo "OPENAI_API_KEY=sk-your-key-here" > .env
echo "AI_MODEL=gpt-4o" >> .env

chmod +x start.sh
./start.sh
```

The script automatically: starts Docker containers, waits for IRIS readiness (healthcheck + HTTP probe), installs the FHIR R4 endpoint, configures CSP gateway routing, sets up authentication, and loads 8 sample patients.

**Access Points**:

| Service | URL | Credentials |
|---------|-----|-------------|
| Frontend | http://localhost:3000 | — |
| Backend API | http://localhost:8000 | — |
| Swagger Docs | http://localhost:8000/docs | — |
| IRIS Portal | http://localhost:52773/csp/sys/UtilHome.csp | SuperUser / SYS |
| FHIR Endpoint | http://localhost:52773/fhir/r4/metadata | — (no auth for GET) |

---

### Method 2: Manual Installation

> ⚠️ **`docker-compose up -d` (Step 3) only starts the containers.** You must also complete Steps 5, 6, and 7 to install the FHIR endpoint and load sample data — without them the application will show no patients.

#### Step 1: Clone Repository
```bash
git clone https://github.com/kcedd34/smart-discharge-navigator.git
cd smart-discharge-navigator
```

#### Step 2: Configure AI (Optional)

Create `.env` in the project root:
```bash
OPENAI_API_KEY=sk-your-key-here
AI_MODEL=gpt-4o
AI_ENABLED=true
```

> **Important**: Use `gpt-4o` or `gpt-4-turbo`. Base `gpt-4` lacks JSON mode support and will fall back to rule-based mode.

#### Step 3: Start Containers
```bash
docker-compose up -d
```

Starts 3 services: **IRIS for Health** (port 52773), **Backend API** (port 8000), **Frontend** (port 3000).

#### Step 4: Wait for IRIS Initialization
```bash
# Wait until the web server responds (2–5 minutes)
curl -s -o /dev/null -w "%{http_code}" http://localhost:52773/csp/sys/UtilHome.csp
# Expected output: 200, 302, or 401
```

#### Step 5: Install FHIR R4 Endpoint

> **Mandatory on first run and after `docker-compose down`.** The FHIR endpoint is not pre-configured in the image.

Open an interactive IRIS terminal (the `-U %SYS` flag is required — FHIR installation classes live in the `%SYS` namespace):
```bash
docker exec -it smart-discharge-iris iris session IRIS -U %SYS
```

Paste all commands inside the IRIS terminal:
```objectscript
set $NAMESPACE = "%SYS"
do ##class(Security.Users).UnExpireUserPasswords("*")
set $NAMESPACE = "HSLIB"
do ##class(HS.Util.Installer.Foundation).Install("FHIRSERVER")
set $NAMESPACE = "FHIRSERVER"
do ##class(HS.FHIRServer.Installer).InstallNamespace()
do ##class(HS.FHIRServer.Installer).InstallInstance("/fhir/r4", "HS.FHIRServer.Storage.Json.InteractionsStrategy", "hl7.fhir.r4.core@4.0.1")
set strategy = ##class(HS.FHIRServer.API.InteractionsStrategy).GetStrategyForEndpoint("/fhir/r4")
set configData = strategy.GetServiceConfigData()
set configData.DefaultSearchPageSize = 1000
set configData.MaxSearchPageSize = 10000
set configData.MaxSearchResults = 10000
do strategy.SaveServiceConfigData(configData)
write "FHIR installed at /fhir/r4",!
halt
```

**Wait 3–8 minutes** for package download and class compilation. Success indicator: `FHIR installed at /fhir/r4`.

#### Step 6: Configure CSP Gateway

Adds `/fhir` to the CSP gateway routing table so requests to `/fhir/r4/*` are routed correctly.

```bash
docker cp config/iris/setup_fhir_post_install.sh smart-discharge-iris:/tmp/setup_fhir_post_install.sh
docker exec smart-discharge-iris bash /tmp/setup_fhir_post_install.sh
```

> **Note**: The FHIR `metadata` endpoint (HTTP GET) is typically accessible immediately after Step 5 without this step. Step 6 registers a `/fhir` CSP application entry and enables Password auth for the path — required for some IRIS editions or configurations.

Verify:
```bash
curl http://localhost:52773/fhir/r4/metadata
# Expected: 200 with CapabilityStatement JSON

# Direct FHIR resource access requires Basic Auth (handled automatically by the backend):
curl -u SuperUser:SYS http://localhost:52773/fhir/r4/Patient?_count=5
```

#### Step 7: Load Sample Data

Must run from inside the backend container to access the Docker network:

```bash
docker cp data/load_sample_data.py smart-discharge-backend:/tmp/load_sample_data.py
docker exec -e FHIR_BASE_URL=http://iris:52773/fhir/r4 smart-discharge-backend python /tmp/load_sample_data.py
```

Creates 8 synthetic patients:
- **3 HIGH risk** — elderly, multiple chronic comorbidities, critical allergies
- **3 MODERATE risk** — 2 chronic conditions, recent encounters
- **2 LOW risk** — younger, single condition

---

### Restarting After Stop

**Containers stopped** (not destroyed):
```bash
docker-compose start

# Re-apply CSP gateway config (ephemeral — required after every restart)
docker cp config/iris/setup_fhir_post_install.sh smart-discharge-iris:/tmp/setup_fhir_post_install.sh
docker exec smart-discharge-iris bash /tmp/setup_fhir_post_install.sh
```

**Containers destroyed** (`docker-compose down`): repeat Steps 3–7.

> **Tip**: Use `start.sh` instead of `docker-compose start` — it handles the CSP re-configuration automatically.

---

## 📖 Usage

### Dashboard (Rule-Based Baseline)

Access http://localhost:3000 to view all patients sorted by risk score.
- Click **"View Risk"** for a detailed factor breakdown
- Click **"Generate Plan"** for a template-based discharge plan

### AI Clinical Chat

1. Click the **"🤖 AI Chat"** tab
2. Select a patient from the sidebar (optional — for patient-specific queries)
3. Type a question or click a suggested prompt
4. View the AI response with FHIR data sources cited

**Example questions**:
- "What are the main readmission risk factors for this patient?"
- "Compare readmission risk across all ICU patients"
- "Should I be concerned about medication interactions?"

### AI Patient Analysis

From the Dashboard, click **"🤖 AI Analysis"** on any patient to view:
- Side-by-side AI vs rule-based risk scores
- Step-by-step AI reasoning with key clinical insights
- Risks missed by the rule-based engine
- AI recommendations

### AI Discharge Planning

Click **"🤖 AI Discharge Plan"** to generate a personalized plan including:
- Medication reconciliation with interaction awareness
- Follow-up scheduling based on clinical priorities
- Patient-friendly instructions

### Multi-Patient Comparison

1. Enable **"Compare Patients"** mode in the dashboard
2. Select 2+ patients using the checkboxes
3. Click **"AI Compare"**
4. View AI triage ranking with rationale

---

## 📡 API Reference

**Base URL**: `http://localhost:8000/api/v1` | **Interactive Docs**: http://localhost:8000/docs

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check |
| `GET` | `/patients` | List all patients with risk scores |
| `GET` | `/patients/{id}` | Get patient details |
| `GET` | `/patients/{id}/risk-assessment` | Rule-based risk assessment |
| `POST` | `/patients/{id}/discharge-plan` | Generate discharge plan (creates FHIR CarePlan + Tasks) |
| `GET` | `/statistics` | Population statistics |

### AI Agent Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/ai/status` | Check AI availability |
| `POST` | `/ai/chat` | Clinical chat with patient context |
| `GET` | `/patients/{id}/ai-analysis` | AI-powered risk analysis |
| `POST` | `/patients/{id}/ai-discharge-plan` | AI-generated discharge plan |
| `POST` | `/ai/compare-patients` | Multi-patient AI triage |

### Analytics Endpoints (FHIR SQL Builder)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/analytics/sql-stats` | Population analytics via SQL |
| `GET` | `/analytics/readmission-sql` | Readmission candidates (SQL-based) |
| `GET` | `/analytics/sql-builder-info` | FHIR SQL Builder feature info |

---

## 🏆 Contest Alignment

**InterSystems Programming Contest: AI Agents for FHIR 2026** — Task #9: Hospital Readmission Risk Workbench

| Requirement | Implementation |
|-------------|----------------|
| **AI Agent for FHIR** | ✅ GPT-4o LLM with clinical reasoning over FHIR R4 data |
| **FHIR Resources** | ✅ Patient, Encounter, Condition, Observation, MedicationRequest, AllergyIntolerance, CarePlan, Task |
| **Platform Features** | ✅ FHIR API, FHIR SQL Builder, AI Hub pattern (OpenAI-compatible) |
| **MVP Criteria** | ✅ Rule-based + AI scoring, FHIR Task generation, discharge plans |
| **Conversational AI** | ✅ Chat interface with patient context switching |
| **Explainable AI** | ✅ Step-by-step reasoning, confidence scores, risk attribution |

### Differentiators
- **Hybrid Intelligence**: AI Agent + rule engine working in tandem
- **Graceful Degradation**: Full functionality without an API key
- **Risk Gap Detection**: AI identifies what rules miss
- **Multi-patient Triage**: AI-powered comparison for discharge prioritization
- **FHIR SQL Analytics**: Leverages IRIS SQL Builder for population insights

---

## 🔗 FHIR Resources

### Resources Used (Read)

| Resource | Purpose | AI Agent Usage |
|----------|---------|----------------|
| **Patient** | Demographics, age | Context for AI reasoning |
| **Encounter** | Admission history | Pattern analysis |
| **Condition** | Active diagnoses | Comorbidity reasoning |
| **Observation** | Vital signs, labs | Trend detection |
| **MedicationRequest** | Active medications | Interaction analysis |
| **AllergyIntolerance** | Drug/food allergies | Allergy-aware planning |

### Resources Created (Write)

| Resource | Purpose |
|----------|---------|
| **CarePlan** | Structured discharge plan (rule-based + AI-enhanced) |
| **Task** | Discharge checklist items |

---

## 🏛️ InterSystems Platform Features

### FHIR SQL Builder

The backend uses the **FHIR SQL Builder** built into IRIS for Health to run standard SQL directly against FHIR resource projections, avoiding JSON bundle parsing in application code.

**How it works**:
1. `InstallInstance` automatically creates SQL projections for every stored FHIR resource. The schema is named `HSFHIR_X000x_S` (e.g., `HSFHIR_X0001_S` on a clean first install).
2. The backend service (`fhir_sql_analytics.py`) sends queries via `POST /api/atelier/v1/{namespace}/_query/sql`.
3. Results are tabular — ready for dashboards, aggregations, and cross-resource JOINs.

**Example queries**:
```sql
-- Readmission candidates
SELECT subject AS patient_id, COUNT(*) AS admissions
FROM HSFHIR_X0001_S.Encounter
WHERE status = 'finished'
GROUP BY subject
HAVING COUNT(*) > 1

-- Polypharmacy analysis (5+ active medications)
SELECT subject AS patient_id, COUNT(*) AS med_count
FROM HSFHIR_X0001_S.MedicationRequest
WHERE status = 'active'
GROUP BY subject
HAVING COUNT(*) >= 5

-- High-risk population (3-table JOIN)
SELECT p.Key, c.code, e.status
FROM HSFHIR_X0001_S.Patient p
JOIN HSFHIR_X0001_S.Condition c ON c.subject = p.Key
JOIN HSFHIR_X0001_S.Encounter e ON e.subject = p.Key
WHERE c.code IN ('44054006','73211009','38341003')
```

### AI Hub Integration

The AI layer follows the **InterSystems AI Hub** integration pattern using an OpenAI-compatible API interface:

```
┌─────────────────────────────────┐
│     Smart Discharge Navigator   │
├─────────────────────────────────┤
│   AIAgentService                │
│   ├─ OpenAI-compatible API ←─── AI Hub pattern (model gateway)
│   ├─ Structured clinical prompts│
│   ├─ FHIR context injection     │
│   └─ Graceful degradation       │
├─────────────────────────────────┤
│   InterSystems IRIS for Health  │
│   ├─ FHIR Repository (R4)       │
│   ├─ FHIR SQL Builder           │
│   └─ IntegratedML (production)  │
└─────────────────────────────────┘
```

---

## 🛠️ Technology Stack

### AI Layer
- **LLM**: OpenAI GPT-4o
- **Client**: OpenAI Python SDK (async)
- **Prompt Engineering**: Structured clinical prompts with FHIR data context injection

### Backend
- **Language**: Python 3.11
- **Framework**: FastAPI (async REST API)
- **FHIR Client**: httpx + custom wrapper
- **Validation**: Pydantic v2
- **AI Integration**: openai >= 1.0.0

### Frontend
- **Framework**: React 18
- **HTTP Client**: Axios
- **UI**: Custom CSS with AI chat interface and tabbed navigation

### FHIR Server
- **Platform**: InterSystems IRIS for Health Community Edition
- **FHIR Version**: R4
- **Container**: `intersystemsdc/irishealth-community:latest`

### Infrastructure
- **Orchestration**: Docker Compose 3.8
- **Services**: 3 containers (IRIS, Backend, Frontend)

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
│   │   │   ├── ai_agent_service.py    # AI Agent
│   │   │   ├── risk_calculator.py     # Rule-based scoring
│   │   │   ├── care_plan_generator.py # Discharge planning
│   │   │   └── fhir_service.py        # FHIR orchestration
│   │   └── api/
│   │       └── routes.py              # API endpoints
│   ├── main.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── App.js                     # React app (incl. AI Chat)
│   │   ├── index.js
│   │   └── index.css
│   ├── public/
│   ├── package.json
│   └── Dockerfile
├── data/
│   └── load_sample_data.py
├── config/
│   └── iris/
│       ├── merge.cpf
│       └── setup_fhir_post_install.sh
├── .env.example
├── docker-compose.yml
├── start.sh
├── AI_AGENT_GUIDE.md
├── ARCHITECTURE.md
└── README.md
```

### Running Locally (Development Mode)

**Backend**:
```bash
cd backend
pip install -r requirements.txt
export OPENAI_API_KEY=sk-your-key-here
uvicorn main:app --reload --port 8000
```

**Frontend**:
```bash
cd frontend
npm install
npm start
```

---

## 🎥 Demo Video

▶️ **[Smart Discharge Navigator Demo](https://www.youtube.com/watch?v=MANijj_yASs)** (YouTube)

**Coverage** (5–7 minutes):

1. **Introduction** (30s) — Problem: hospital readmissions. Solution: AI Agent for FHIR
2. **AI Agent Demo** (2 min) — AI Chat, patient context switching, clinical questions
3. **AI Analysis** (1.5 min) — Side-by-side comparison, reasoning steps, missed risks
4. **AI Discharge Plan** (1 min) — Personalized AI plan generation
5. **Multi-Patient Comparison** (1 min) — AI triage of multiple patients
6. **Rule-Based Baseline** (30s) — Deterministic scoring underneath
7. **Architecture** (30s) — Hybrid design, FHIR compliance, contest alignment

**Key demo points**:
- Show the **AI Status badge** (Active vs Fallback)
- Highlight the **"Risks Missed by Rules"** section
- Demonstrate **graceful fallback** by toggling `AI_ENABLED=false`

---

## ⚙️ Environment Variables

Variables are set in `docker-compose.yml`. The only value you need to supply is `OPENAI_API_KEY` for AI features (via `.env` file in the project root).

```yaml
environment:
  - FHIR_BASE_URL=http://iris:52773/fhir/r4
  - IRIS_USERNAME=SuperUser
  - IRIS_PASSWORD=SYS
  - CORS_ORIGINS=["http://localhost:3000","http://localhost:3001"]
  - OPENAI_API_KEY=${OPENAI_API_KEY:-}
  - AI_MODEL=${AI_MODEL:-gpt-4o}
  - AI_ENABLED=${AI_ENABLED:-true}
```

> **CORS format**: `CORS_ORIGINS` must be a valid JSON array string. A plain URL string will cause a pydantic-settings v2 parse error and prevent the backend from starting.

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `FHIR_BASE_URL` | Yes | `http://iris:52773/fhir/r4` | Internal FHIR endpoint (container-to-container) |
| `IRIS_USERNAME` | Yes | `SuperUser` | IRIS user for authenticated FHIR writes |
| `IRIS_PASSWORD` | Yes | `SYS` | IRIS password |
| `CORS_ORIGINS` | Yes | `["http://localhost:3000","http://localhost:3001"]` | Allowed CORS origins (JSON array) |
| `OPENAI_API_KEY` | No | _(empty)_ | OpenAI key — without it, system runs in rule-based fallback mode |
| `AI_MODEL` | No | `gpt-4o` | Use `gpt-4o` or `gpt-4-turbo`; base `gpt-4` lacks JSON mode |
| `AI_TEMPERATURE` | No | `0.3` | Sampling temperature |
| `AI_MAX_TOKENS` | No | `2000` | Maximum tokens in AI response |
| `AI_ENABLED` | No | `true` | Master toggle for AI features |
| `HIGH_RISK_THRESHOLD` | No | `0.7` | Score threshold for HIGH risk classification |
| `MODERATE_RISK_THRESHOLD` | No | `0.4` | Score threshold for MODERATE risk classification |

---

## 🚦 Troubleshooting

### IRIS / FHIR Issues

#### FHIR endpoint returns 404 — "CSP application path not in CSP gateway"

Most common 404 on a fresh install. The embedded httpd doesn't route `/fhir` requests to IRIS unless configured.

```bash
docker cp config/iris/setup_fhir_post_install.sh smart-discharge-iris:/tmp/setup_fhir_post_install.sh
docker exec smart-discharge-iris bash /tmp/setup_fhir_post_install.sh
```

Verify: `curl http://localhost:52773/fhir/r4/metadata` — expected 200 with CapabilityStatement.

#### FHIR endpoint returns 404 — endpoint not installed

```bash
docker exec -it smart-discharge-iris iris session IRIS -U %SYS
# Paste all installation commands from Step 5 above
# Wait 3–8 minutes, then configure CSP gateway:
docker cp config/iris/setup_fhir_post_install.sh smart-discharge-iris:/tmp/setup_fhir_post_install.sh
docker exec smart-discharge-iris bash /tmp/setup_fhir_post_install.sh
```

#### FHIR write returns HTTP 500 — "PROPERTY DOES NOT EXIST"

FHIR search index classes were not fully generated during installation. Uninstall and reinstall:

```objectscript
// In an IRIS terminal session
set sc = ##class(HS.FHIRServer.Installer).UninstallInstance("/fhir/r4")
write "Uninstall sc=",sc,!
halt
```

Then re-run Steps 5–6 from the Installation section.

#### IRIS container exits or runs out of memory

IRIS needs at least 4 GB RAM. Confirm `config/iris/merge.cpf` contains `globals=256,0,0,0,0,0`. Check status:
```bash
# Check healthcheck status (use conditional template — plain .State.Health.Status fails if healthcheck not yet initialized)
docker inspect --format='{{if .State.Health}}{{.State.Health.Status}}{{else}}no-healthcheck{{end}}' smart-discharge-iris

# Or probe HTTP directly (more reliable):
curl -s -o /dev/null -w "%{http_code}" http://localhost:52773/csp/sys/UtilHome.csp
# Expected: 200, 302, or 401

docker logs smart-discharge-iris --tail=50
```

#### FHIR GET works but POST returns 401 Unauthorized

Write operations require HTTP Basic Auth (handled automatically by the backend). For manual testing:
```bash
curl -u SuperUser:SYS -X POST http://localhost:52773/fhir/r4/Patient \
  -H "Content-Type: application/fhir+json" \
  -d '{"resourceType":"Patient","name":[{"family":"Test"}]}'
```

#### SuperUser login fails via Management Portal

```bash
echo 'set props("ChangePassword")=0
do ##class(Security.Users).Modify("SuperUser",.props)
halt' | docker exec -i smart-discharge-iris bash -c 'iris session IRIS -U %SYS'
```

---

### Backend Issues

#### "error parsing value for field CORS_ORIGINS"

Ensure `CORS_ORIGINS` is a JSON array in `docker-compose.yml`:
```yaml
- CORS_ORIGINS=["http://localhost:3000","http://localhost:3001"]  # Correct
- CORS_ORIGINS=http://localhost:3000                              # Wrong
```

#### Backend can't connect to IRIS

```bash
docker-compose ps
docker-compose logs iris
docker-compose logs backend --tail=30
```

The backend connects using the internal Docker hostname `iris` (not `localhost`): `FHIR_BASE_URL=http://iris:52773/fhir/r4`.

---

### AI Agent Issues

#### AI features not working

```bash
curl http://localhost:8000/api/v1/ai/status
docker-compose logs backend --tail=50
```

Common causes:
- `OPENAI_API_KEY` not set — create `.env` file in the project root
- `AI_MODEL=gpt-4` (base) — change to `gpt-4o` or `gpt-4-turbo`
- `AI_ENABLED=false` — set to `true` in `docker-compose.yml`

#### Discharge plan shows HTTP 500 — "JSONDecodeError"

IRIS returns HTTP 201 with an **empty body** on resource creation. The `create_resource()` method must extract the ID from the `Location` response header instead of calling `.json()`. Ensure you're on the latest code:
```bash
docker-compose up -d --no-deps --force-recreate backend
```

#### Frontend shows CORS errors

CORS errors almost always indicate an underlying backend 500 — the backend does not emit CORS headers on error responses. Fix the backend error first (`docker-compose logs backend`), and the CORS error will resolve automatically.

---

### Sample Data Loading Issues

#### "Expecting value: line 1 column 1 (char 0)"

IRIS returns an empty body on 201 Created. Ensure you're using the latest `data/load_sample_data.py` (extracts resource ID from the `Location` header).

#### Patients created but no conditions/encounters

Verify that the FHIR endpoint accepts writes:
```bash
curl -s -o /dev/null -w "%{http_code}" -u SuperUser:SYS \
  -X POST http://localhost:52773/fhir/r4/Patient \
  -H "Content-Type: application/fhir+json" \
  -d '{"resourceType":"Patient","name":[{"family":"Test"}]}'
# Expected: 201
```

---

### Docker Image Version

This application was developed with `irishealth-community:2026.1.0.235.2`. If you encounter issues with a newer `latest` image, pin the version in `docker-compose.yml`:
```yaml
image: intersystemsdc/irishealth-community:2026.1.0.235.2
```

---

## 📄 License

MIT License — see [LICENSE](LICENSE)

---

## 👨‍💻 Author

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

**Built with ❤️ and 🤖 by [Carlos Eduardo Dias Duarte](mailto:kcedd34@gmail.com) for InterSystems Programming Contest: AI Agents for FHIR 2026**
