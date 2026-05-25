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

# 2. (Optional) Enable AI features - create .env file
echo "OPENAI_API_KEY=sk-your-key-here" > .env
echo "AI_MODEL=gpt-4o" >> .env

# 3. Start application (automated script)
chmod +x start.sh
./start.sh

# 4. Access
# - Frontend: http://localhost:3000
# - Backend API: http://localhost:8000/docs
# - IRIS Portal: http://localhost:52773/csp/sys/UtilHome.csp (SuperUser/SYS)
```

**Windows Users** (or if `start.sh` fails):
```bash
# Start containers
docker-compose up -d

# Wait 60 seconds for IRIS initialization
sleep 60

# Install FHIR endpoint (interactive terminal)
docker exec -it smart-discharge-iris iris session IRIS
# Then paste the commands from Step 5 below and wait for completion

# Configure CSP gateway
docker cp config/iris/setup_fhir_post_install.sh smart-discharge-iris:/tmp/setup_fhir_post_install.sh
docker exec smart-discharge-iris bash /tmp/setup_fhir_post_install.sh

# Load sample data (from backend container)
docker cp data/load_sample_data.py smart-discharge-backend:/app/
docker exec smart-discharge-backend pip install requests
docker exec -e FHIR_BASE_URL=http://iris:52773/fhir/r4 smart-discharge-backend python /app/load_sample_data.py
```

**Note**: Without `OPENAI_API_KEY`, the system runs in rule-based mode (fully functional, no AI features).

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Usage](#-usage)
- [API Reference](#-api-reference)
- [Contest Alignment](#-contest-alignment)
- [Technology Stack](#-technology-stack)
- [Troubleshooting](#-troubleshooting)
- [Appendix](#-appendix)

---

## 🎯 Overview

**Smart Discharge Navigator** tackles hospital readmissions ($17B annual cost in US) through a **hybrid AI Agent + rule-based system** that:

- Analyzes FHIR patient data (Patient, Encounter, Condition, MedicationRequest, Observation, AllergyIntolerance)
- Provides **AI-powered clinical reasoning** (GPT-4o) with explainable insights
- Falls back to **deterministic rule-based scoring** when AI unavailable
- Generates personalized discharge plans as FHIR CarePlan + Task resources
- Supports **conversational clinical queries** through AI chat interface

### Hybrid Architecture

| Layer | Purpose | When Used |
|-------|---------|-----------|
| **AI Agent (GPT-4o)** | Deep clinical reasoning, identifies non-obvious risks, conversational interface | When `OPENAI_API_KEY` configured |
| **Rule-Based Engine** | Evidence-based deterministic scoring (6 factors weighted) | Always (provides baseline + fallback) |

**Key Differentiator**: AI Agent identifies risks missed by rules (medication interactions, comorbidity patterns, social determinants) while maintaining explainable step-by-step reasoning.

---

## ✨ Key Features

### AI Agent Capabilities (when enabled)

| Feature | Description |
|---------|-------------|
| **AI Clinical Chat** | Conversational interface for patient queries with FHIR data context |
| **AI Risk Analysis** | LLM-powered assessment with step-by-step clinical reasoning |
| **AI Discharge Plans** | Personalized, AI-generated discharge narratives |
| **AI Patient Comparison** | Multi-patient triage with AI prioritization rationale |
| **Graceful Degradation** | Auto-fallback to rule-based mode when AI unavailable |

### Rule-Based Baseline (always available)

- **Multi-Factor Risk Scoring**: 6 weighted factors (admissions, conditions, medications, age, follow-up, vitals)
- **Risk Stratification**: HIGH (≥70%) / MODERATE (40-69%) / LOW (<40%)
- **Automated Discharge Plans**: Template-based FHIR CarePlan + Task generation
- **Population Dashboard**: Patient list sorted by risk with statistics

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
| **OpenAI API Key** | - | **Optional** - enables AI features |

> **Critical**: InterSystems IRIS requires significant memory. Ensure Docker has at least 6 GB RAM allocated (Docker Desktop → Settings → Resources).

---
- **Step-by-step reasoning**: Shows the AI's clinical reasoning process
- **Key insights**: AI-identified risk factors and clinical observations
- **Missed risks**: Flags risks that the rule-based engine alone would not catch
- **Personalized recommendations**: Context-aware action items

### 3. AI Discharge Plan Generation

Generates comprehensive, personalized discharge plans using LLM reasoning:

- Medication reconciliation with interaction awareness
- Follow-up scheduling based on clinical priorities
- Patient-friendly instructions in plain language
## 🚀 Installation

### Method 1: Automated Script (Recommended)

```bash
git clone https://github.com/kcedd34/smart-discharge-navigator.git
cd smart-discharge-navigator

# Optional: enable AI features
echo "OPENAI_API_KEY=sk-your-key-here" > .env
echo "AI_MODEL=gpt-4o" >> .env

# Start everything
chmod +x start.sh
./start.sh
```

The script automatically:
1. Starts Docker containers
2. Waits for IRIS health check
3. Installs FHIR R4 endpoint (`/fhir/r4`)
4. Configures CSP gateway routing
5. Sets up authentication
6. Loads 8 sample patients

**Access Points**:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/docs
- IRIS Portal: http://localhost:52773/csp/sys/UtilHome.csp (SuperUser/SYS)
- FHIR Endpoint: http://localhost:52773/fhir/r4/metadata

---

### Method 2: Manual Installation

#### Step 1: Clone Repository
```bash
git clone https://github.com/kcedd34/smart-discharge-navigator.git
cd smart-discharge-navigator
```

#### Step 2: Configure AI (Optional)
Create `.env` file in project root:
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

This starts 3 services:
- **IRIS for Health** (port 52773)
- **Backend API** (port 8000)
- **Frontend** (port 3000)

#### Step 4: Wait for IRIS Initialization
```bash
# Wait until health check passes (2-5 minutes)
docker inspect --format='{{.State.Health.Status}}' smart-discharge-iris
# Should output: healthy
```

#### Step 5: Install FHIR R4 Endpoint

**Critical first-run step**. The FHIR endpoint is not pre-configured.

**Open interactive IRIS terminal:**
```bash
docker exec -it smart-discharge-iris iris session IRIS
```

**Inside IRIS terminal, copy and paste ALL commands below:**
```objectscript
// Unexpire passwords (development only)
set $NAMESPACE = "%SYS"
do ##class(Security.Users).UnExpireUserPasswords("*")

// Create FHIRSERVER namespace
set $NAMESPACE = "HSLIB"
do ##class(HS.Util.Installer.Foundation).Install("FHIRSERVER")

// Install FHIR R4 endpoint
set $NAMESPACE = "FHIRSERVER"
do ##class(HS.FHIRServer.Installer).InstallNamespace()
do ##class(HS.FHIRServer.Installer).InstallInstance("/fhir/r4", "HS.FHIRServer.Storage.Json.InteractionsStrategy", "hl7.fhir.r4.core@4.0.1")

// Configure search limits
set strategy = ##class(HS.FHIRServer.API.InteractionsStrategy).GetStrategyForEndpoint("/fhir/r4")
set configData = strategy.GetServiceConfigData()
set configData.DefaultSearchPageSize = 1000
set configData.MaxSearchPageSize = 10000
set configData.MaxSearchResults = 10000
do strategy.SaveServiceConfigData(configData)

write "FHIR installed at /fhir/r4",!

halt
```

**Wait 3-8 minutes** for FHIR package download and class compilation. You'll see progress messages.

#### Step 6: Configure CSP Gateway & Authentication

**Required** to enable HTTP access to `/fhir/r4/*` endpoints.

**Copy and run setup script:**
```bash
docker cp config/iris/setup_fhir_post_install.sh smart-discharge-iris:/tmp/setup_fhir_post_install.sh
docker exec smart-discharge-iris bash /tmp/setup_fhir_post_install.sh
```

This script:
1. Adds `/fhir` to CSP gateway routing table
2. Configures SuperUser for HTTP Basic auth
3. Restarts embedded httpd server

**Verify FHIR endpoint**:
```bash
curl http://localhost:52773/fhir/r4/metadata
# Should return JSON CapabilityStatement
```

#### Step 7: Load Sample Data

The script must run from inside the backend container to access the Docker network:

```bash
# Copy script to backend container
docker cp data/load_sample_data.py smart-discharge-backend:/app/

# Install requests library (if not already installed)
docker exec smart-discharge-backend pip install requests

# Execute script with correct FHIR URL
docker exec -e FHIR_BASE_URL=http://iris:52773/fhir/r4 smart-discharge-backend python /app/load_sample_data.py
```

Creates 8 synthetic patients:
- 3 HIGH risk (elderly, multiple comorbidities, multiple allergies)
- 3 MODERATE risk (2 chronic conditions)
- 2 LOW risk (single condition, younger)

---

### Restarting After Stop

If containers **stopped** (not destroyed):

```bash
docker-compose start

# Re-apply CSP gateway config (ephemeral, must re-run after restart)
docker cp config/iris/setup_fhir_post_install.sh smart-discharge-iris:/tmp/setup_fhir_post_install.sh
docker exec smart-discharge-iris bash /tmp/setup_fhir_post_install.sh
```

If containers **destroyed** (`docker-compose down`): repeat full installation (Steps 3-7).

---

## 📖 Usage

### 1. Dashboard (Rule-Based Baseline)

**Access**: http://localhost:3000

- View all patients sorted by risk score
- Click **"View Risk"** for detailed factor breakdown
- Click **"Generate Plan"** for template-based discharge plan

### 2. AI Clinical Chat

**Navigate**: Click **"🤖 AI Chat"** tab

1. Select patient from sidebar (optional - for patient-specific queries)
2. Type question or click suggested question
3. View AI response with FHIR sources cited

**Example Questions**:
- "What are the main readmission risk factors for this patient?"
- "Compare readmission risk across all ICU patients"
- "Should I be concerned about medication interactions?"

### 3. AI Patient Analysis

**From Dashboard**: Click **"🤖 AI Analysis"** on any patient

View:
- Side-by-side AI vs Rule-based scores
- Step-by-step AI reasoning
- Risks missed by rule-based engine
- AI recommendations

### 4. AI Discharge Planning

**From Dashboard**: Click **"🤖 AI Discharge Plan"** on any patient

Generates personalized plan including:
- Medication reconciliation with interaction awareness
- Follow-up scheduling based on clinical priorities
- Patient-friendly instructions
- Risk-specific interventions

### 5. Multi-Patient Comparison

1. Enable **"Compare Patients"** mode in dashboard
2. Select 2+ patients (checkboxes)
3. Click **"AI Compare"**
4. View AI triage ranking with rationale

---

## 📡 API Reference

**Base URL**: `http://localhost:8000/api/v1`

**Interactive Docs**: http://localhost:8000/docs

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

**InterSystems Programming Contest: AI Agents for FHIR 2026**  
**Contest Task**: #9 — Hospital Readmission Risk Workbench

### Requirements

| Requirement | Implementation |
|-------------|----------------|
| **AI Agent for FHIR** | ✅ GPT-4o LLM with clinical reasoning over FHIR R4 data |
| **FHIR Resources** | ✅ Patient, Encounter, Condition, Observation, MedicationRequest, AllergyIntolerance, CarePlan, Task |
| **Platform Features** | ✅ FHIR API, FHIR SQL Builder, AI Hub pattern (OpenAI-compatible) |
| **MVP Criteria** | ✅ Rule-based + AI scoring, FHIR Task generation, discharge plans |
| **Conversational AI** | ✅ Chat interface with patient context switching |
| **Explainable AI** | ✅ Step-by-step reasoning, confidence scores, risk attribution |

### Differentiators
- **Hybrid Intelligence**: AI Agent + rule engine working together
- **Graceful Degradation**: Full functionality without API key (rule-based fallback)
- **Risk Gap Detection**: AI identifies what rules miss
- **Multi-patient Triage**: AI-powered comparison for discharge prioritization
- **FHIR SQL Analytics**: Leverages IRIS SQL Builder for population insights

---

## 🛠️ Technology Stack

### Backend
- **Language**: Python 3.11
- **Framework**: FastAPI (async REST API)
- **AI**: OpenAI Python SDK (GPT-4o)
- **FHIR Client**: httpx + custom wrapper
- **Validation**: Pydantic v2

### Frontend
- **Framework**: React 18
- **HTTP Client**: Axios
- **UI**: Custom CSS with responsive design

### FHIR Server
- **Platform**: InterSystems IRIS for Health Community Edition
- **FHIR Version**: R4
- **Container**: `intersystemsdc/irishealth-community:latest`

### Infrastructure
- **Orchestration**: Docker Compose 3.8
- **Containers**: 3 services (IRIS, Backend, Frontend)

---

## 🚦 Troubleshooting

### FHIR Endpoint Issues

#### 404 - "CSP application path not in CSP gateway"

**Most common issue on fresh install**. The embedded httpd doesn't know about `/fhir` routes.

**Fix**:
```bash
docker cp config/iris/setup_fhir_post_install.sh smart-discharge-iris:/tmp/setup_fhir_post_install.sh
docker exec smart-discharge-iris bash /tmp/setup_fhir_post_install.sh
```

**Verify**:
```bash
curl http://localhost:52773/fhir/r4/metadata
# Should return 200 with CapabilityStatement
```

#### 404 - FHIR Endpoint Not Installed

Endpoint was never installed (first run or after `docker-compose down`).

**Fix** - Open interactive IRIS terminal:
```bash
docker exec -it smart-discharge-iris iris session IRIS
```

**Paste these commands inside IRIS:**
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
write "FHIR installed",!
halt
```

**Wait 3-8 minutes, then configure gateway:**
```bash
docker cp config/iris/setup_fhir_post_install.sh smart-discharge-iris:/tmp/setup_fhir_post_install.sh
docker exec smart-discharge-iris bash /tmp/setup_fhir_post_install.sh
```

#### 500 - "PROPERTY DOES NOT EXIST"

FHIR search index classes not fully generated during installation.

**Fix** - reinstall FHIR endpoint (use interactive method above).

#### 401 Unauthorized on POST Requests

Write operations require authentication. Backend handles this automatically. For manual testing:
```bash
curl -u SuperUser:SYS -X POST http://localhost:52773/fhir/r4/Patient \
  -H "Content-Type: application/fhir+json" \
  -d '{"resourceType":"Patient","name":[{"family":"Test"}]}'
```

---

### Backend Issues

#### "error parsing value for field CORS_ORIGINS"

`CORS_ORIGINS` must be JSON array. In `docker-compose.yml`:
```yaml
- CORS_ORIGINS=["http://localhost:3000","http://localhost:3001"]  # Correct
- CORS_ORIGINS=http://localhost:3000  # Wrong - causes pydantic error
```

#### Backend Can't Connect to IRIS

```bash
docker-compose ps         # Check all containers running
docker-compose logs iris  # Check IRIS startup
docker-compose logs backend --tail=30
```

Backend uses internal Docker hostname `iris` (not `localhost`):
```yaml
FHIR_BASE_URL=http://iris:52773/fhir/r4  # Correct for container-to-container
```

---

### AI Agent Issues

#### AI Features Not Working

**Check AI status**:
```bash
curl http://localhost:8000/api/v1/ai/status
```

**Common causes**:
- `OPENAI_API_KEY` not set → create `.env` file in project root
- `AI_MODEL=gpt-4` (base) → change to `gpt-4o` or `gpt-4-turbo` (JSON mode required)
- `AI_ENABLED=false` → set to `true` in `docker-compose.yml`

**Check logs**:
```bash
docker-compose logs backend --tail=50
```

---

### Sample Data Loading Issues

#### "Expecting value: line 1 column 1 (char 0)"

IRIS returns HTTP 201 with **empty body** on successful resource creation. Update to latest `data/load_sample_data.py` which extracts resource ID from `Location` header.

#### Patients Created But No Conditions/Encounters

Resource creation failed. Verify FHIR endpoint accepts writes:
```bash
curl -s -o /dev/null -w "%{http_code}" -u SuperUser:SYS \
  -X POST http://localhost:52773/fhir/r4/Patient \
  -H "Content-Type: application/fhir+json" \
  -d '{"resourceType":"Patient","name":[{"family":"Test"}]}'
# Expected: 201
```

---

## 📚 Appendix

### Manual FHIR Server Setup (Advanced)

**Note**: The automated scripts handle this. Use manual setup only for customization/debugging.

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
# Linux / macOS / WSL
export OPENAI_API_KEY=sk-your-key-here

# Windows CMD
set OPENAI_API_KEY=sk-your-key-here
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

**Open interactive IRIS terminal:**
```bash
docker exec -it smart-discharge-iris iris session IRIS
```

**Paste all commands below inside IRIS terminal:**
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

**Wait 3-8 minutes** for package download and class compilation.

**Expected output** (success indicators):
```
Saving hl7.fhir.r4.core@4.0.1 ← package data loading (takes 2-5 minutes)
INFO: New strategy created...
FHIR installed at /fhir/r4    ← installation successful
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

---

### Detailed FHIR Server Setup (Alternative Manual Configuration)

The following is the detailed manual setup procedure that was adapted for this application. This approach creates a FHIR server from scratch using IRIS terminal commands. This is useful if you need to customize the FHIR server configuration or troubleshoot installation issues.

> **Note**: The interactive installation method (Step 5 above) uses this approach. Use this section to understand what each command does or to customize the configuration.

#### Step 1: Start an IRIS Terminal Session

```bash
docker exec -it smart-discharge-iris iris session IRIS
```

#### Step 2: Unexpire User Passwords

By default, Community editions of IRIS Health have the password `SYS` for every account, but these passwords have expired. This step prevents authentication issues.

> **Warning**: This is only suitable for development environments. Production environments should use robust authentication.

```objectscript
set $NAMESPACE = "%SYS"
do ##class(Security.Users).UnExpireUserPasswords("*")
```

#### Step 3: Create a New Namespace for Your FHIR Server

```objectscript
set $NAMESPACE = "HSLIB"
do:'##class(%SYS.Namespace).Exists("fhirdemo") ##class(HS.Util.Installer.Foundation).Install("fhirdemo")
set $NAMESPACE = "fhirdemo"
```

> **Note**: For this application, we use the namespace `HSSYS` (configured in IRIS container). The namespace `fhirdemo` is shown here as an example if you need to create a custom namespace.

#### Step 4: Install the FHIR Server

Configure and install the FHIR R4 server endpoint:

```objectscript
// Make the path prefix for the FHIR server
set fhirServerPath = "/fhir/r4"

// Create Strategy 
set strategyClass = "HS.FHIRServer.Storage.Json.InteractionsStrategy"

// Create metadata info for FHIR version r4
set metadataPackage = "hl7.fhir.r4.core@4.0.1"

// You can allow metadata packages for multiple FHIR versions with the following: 
// set metadataPackage = $LISTBUILD("hl7.fhir.r4.core@4.0.1","hl7.fhir.us.core@3.1.0")

// Ensure namespace is FHIR enabled
do ##class(HS.FHIRServer.Installer).InstallNamespace()
do ##class(HS.FHIRServer.Installer).InstallInstance(fhirServerPath, strategyClass, metadataPackage)
```

> **Note**: This application uses `/fhir/r4` as the FHIR server path (not `/demo/fhir` as shown in some InterSystems examples).

#### Step 5: Configure Search Result Limits

Set limits on search results to avoid transferring huge amounts of data:

```objectscript
set strategy = ##class(HS.FHIRServer.API.InteractionsStrategy).GetStrategyForEndpoint(fhirServerPath)
set configData = strategy.GetServiceConfigData()
set configData.DefaultSearchPageSize = 1000
set configData.MaxSearchPageSize = 10000
set configData.MaxSearchResults = 10000
do strategy.SaveServiceConfigData(configData)
```

#### Step 6: Load FHIR Resources to the FHIR Server

Load FHIR resource files from a directory into the FHIR server:

```objectscript
// Location of our FHIR data
set fhirdata = "/usr/irissys/output/fhir"

// Load FHIR resource files
do ##class(HS.FHIRServer.Tools.DataLoader).SubmitResourceFiles(fhirdata, "FHIRServer", fhirServerPath, 1, "^fhirlogs")
```

**Arguments explanation:**
1. **Location of the FHIR data** — Directory path containing FHIR JSON files
2. **Type of service** — `FHIRServer` or `HTTP`
3. **FHIR server location path** — The endpoint path (e.g., `/demo/fhir`)
4. **Display progress** — `1` (yes) or `0` (no)
5. **Log process to a global** — `^fhirlogs` (optional)

> **Note**: For this application, sample data is loaded via the Python script `data/load_sample_data.py` which uses HTTP POST requests to the FHIR endpoint.

#### Step 7: Verify the Endpoint

Check that the endpoint is running by visiting the metadata endpoint:

```bash
curl http://localhost:52773/demo/fhir/metadata
```

It should return a `CapabilityStatement` resource (XML or JSON depending on Accept header).

#### Step 8: Query the FHIR Endpoint

Now that data is loaded, you can query the endpoint with HTTP requests.

**Example GET request:**

```http
GET http://localhost:52773/demo/fhir/Patient/1
Authorization: Basic SuperUser SYS
Accept: application/fhir+json
```

**Using curl:**

```bash
curl -u "SuperUser:SYS" \
    -H "Accept: application/fhir+json" \
    http://localhost:52773/fhir/r4/Patient \
    -o response.json
```

**Using Python Requests library:**

```python
import requests
from requests.auth import HTTPBasicAuth

headers = {"Content-Type": "application/fhir+json"}
uri = "http://localhost:52773/demo/fhir/Patient/1"

username = "SuperUser"
password = "SYS"
res = requests.get(uri, headers=headers, auth=HTTPBasicAuth(username, password))
print(res)
print(res.json())
```

---

#### 4. Load Sample Data

Execute from within the backend container to access the Docker network:

```bash
# Copy script to backend container
docker cp data/load_sample_data.py smart-discharge-backend:/app/

# Install requests library
docker exec smart-discharge-backend pip install requests

# Execute with FHIR URL pointing to 'iris' container
docker exec -e FHIR_BASE_URL=http://iris:52773/fhir/r4 smart-discharge-backend python /app/load_sample_data.py
```

This creates 8 synthetic patients categorised by risk level:
- **3 HIGH risk** — elderly patients with multiple chronic comorbidities (heart failure, COPD, CKD, diabetes) and critical allergies (Penicillin, NSAIDs)
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
| `IRIS_PASSWORD` | Yes | `SYS` | IRIS password |
| `CORS_ORIGINS` | Yes | `["http://localhost:3000","http://localhost:3001"]` | Allowed CORS origins (JSON array) |
| `OPENAI_API_KEY` | No | _(empty)_ | OpenAI key. Without it, system runs in rule-based fallback mode |
| `AI_MODEL` | No | `gpt-4o` | LLM model. Use `gpt-4o` or `gpt-4-turbo` |
| `AI_TEMPERATURE` | No | `0.3` | Sampling temperature |
| `AI_MAX_TOKENS` | No | `2000` | Maximum tokens in AI response |
| `AI_ENABLED` | No | `true` | Master toggle for AI |
| `HIGH_RISK_THRESHOLD` | No | `0.7` | Risk score above which is high risk |
| `MODERATE_RISK_THRESHOLD` | No | `0.4` | Risk score above which is moderate risk |

---

## 📄 License

MIT License - see [LICENSE](LICENSE)

---

## 🙏 Acknowledgments

- **InterSystems** - IRIS for Health Community Edition
- **OpenAI** - GPT-4o clinical reasoning engine
- **HL7 FHIR** - Healthcare interoperability standard
- **Contest Organizers** - InterSystems Programming Contest: AI Agents for FHIR 2026

---

**Built with ❤️ for healthcare innovation** | Carlos Eduardo Dias Duarte | [kcedd34@gmail.com](mailto:kcedd34@gmail.com)
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
- **LLM**: OpenAI GPT-4o (clinical reasoning engine)
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
# Open interactive IRIS terminal
docker exec -it smart-discharge-iris iris session IRIS

# Paste the installation commands from Step 5 (Installation section)
# Wait 3-8 minutes for completion, then configure CSP Gateway
docker cp config/iris/setup_fhir_post_install.sh smart-discharge-iris:/tmp/setup_fhir_post_install.sh
docker exec smart-discharge-iris bash /tmp/setup_fhir_post_install.sh
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

// Step 2: Re-run the installation commands from Step 5
// Exit and reopen interactive terminal, then paste all commands
```

Or use the interactive installation method from Step 5:
```bash
docker exec -it smart-discharge-iris iris session IRIS
# Paste all installation commands from Step 5
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
# Ensure IRIS has fully started (wait 60 seconds after docker-compose up)
sleep 60

# Copy script to backend container and execute
docker cp data/load_sample_data.py smart-discharge-backend:/app/
docker exec smart-discharge-backend pip install requests
docker exec -e FHIR_BASE_URL=http://iris:52773/fhir/r4 smart-discharge-backend python /app/load_sample_data.py
```

**Note**: The script uses `FHIR_BASE_URL` environment variable. When running from the host (outside Docker network), use `http://localhost:52773/fhir/r4`. When running inside containers, use `http://iris:52773/fhir/r4`.

---

**Built with ❤️ and 🤖 by [Carlos Eduardo Dias Duarte](mailto:kcedd34@gmail.com) for InterSystems Programming Contest: AI Agents for FHIR 2026**
