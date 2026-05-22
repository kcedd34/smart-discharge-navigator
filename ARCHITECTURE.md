# Architecture Documentation 🏗️

## System Overview

Smart Discharge Navigator implements a **hybrid intelligence architecture** combining an **AI Agent (OpenAI GPT-4)** with a **deterministic rule-based engine**, all built on top of a clean, layered architecture following SOLID principles.

The AI Agent is the **primary analytical layer**, providing LLM-powered clinical reasoning over FHIR data. The rule-based engine serves as a **baseline and safety net**, ensuring reliable operation even without AI availability.

---

## Architectural Layers

### Layer Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│  PRESENTATION LAYER                                                 │
│  React 18 — Dashboard + AI Chat + AI Analysis Modals               │
└───────────────────────────────┬─────────────────────────────────────┘
                                │ REST API (HTTP)
┌───────────────────────────────┴─────────────────────────────────────┐
│  API LAYER                                                          │
│  FastAPI — Core routes + AI Agent routes                           │
├─────────────────────────────────────────────────────────────────────┤
│  SERVICE LAYER                                                      │
│  ┌────────────────────────┐   ┌──────────────────────────────────┐ │
│  │  🤖 AI Agent Service    │   │  📊 Rule-Based Services          │ │
│  │  • LLM Clinical Reason │   │  • Risk Calculator               │ │
│  │  • Chat Management     │   │  • Care Plan Generator           │ │
│  │  • FHIR Data Gathering │   │  • FHIR Service (orchestration)  │ │
│  │  • Prompt Engineering  │   │                                   │ │
│  └────────────┬───────────┘   └───────────────┬──────────────────┘ │
├───────────────┴───────────────────────────────┴─────────────────────┤
│  CORE LAYER                                                         │
│  FHIR Client (httpx) · OpenAI Client (async) · Configuration       │
├─────────────────────────────────────────────────────────────────────┤
│  EXTERNAL SYSTEMS                                                   │
│  InterSystems IRIS (FHIR R4)    ·    OpenAI API (GPT-4)           │
└─────────────────────────────────────────────────────────────────────┘
```

---

## AI Agent Service Architecture

### Overview

The `AIAgentService` (`ai_agent_service.py`) is the **central AI component** that implements:

1. **Clinical reasoning** via OpenAI GPT-4
2. **FHIR data gathering** across multiple resource types
3. **Prompt engineering** with structured clinical context
4. **Graceful degradation** to rule-based fallback
5. **Conversation management** for multi-turn clinical dialogue

### Class Design

```python
class AIAgentService:
    # Initialization
    _initialize_client()          # Set up AsyncOpenAI with API key
    is_ai_available (property)    # Check AI readiness

    # Core AI Methods
    analyze_patient_with_ai()     # Hybrid analysis (AI + rules)
    chat_with_agent()             # Conversational clinical Q&A
    generate_ai_discharge_plan()  # AI-powered discharge narrative
    compare_patients()            # Multi-patient triage

    # Internal Methods
    _gather_patient_fhir_data()   # Collect FHIR resources
    _call_llm()                   # OpenAI API wrapper with retries
    _calculate_age()              # Age from birth date

    # Fallback Methods
    _generate_fallback_analysis()        # Rule-based analysis fallback
    _generate_fallback_discharge_plan()  # Template plan fallback
    _generate_fallback_comparison()      # Score-based comparison fallback
```

### Prompt Engineering Strategy

The AI Agent uses **structured clinical prompts** designed for accuracy and safety:

```
┌─────────────────────────────────────────────┐
│  SYSTEM PROMPT                              │
│  • Clinical reasoning persona               │
│  • FHIR data interpretation guidelines      │
│  • Risk assessment framework                │
│  • Safety guardrails                        │
│  • Output format specification              │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────┴──────────────────────────┐
│  USER PROMPT (dynamic per request)          │
│  • Patient FHIR data summary               │
│  │  - Demographics                          │
│  │  - Recent encounters                     │
│  │  - Active conditions (with codes)        │
│  │  - Current medications                   │
│  │  - Latest vital signs                    │
│  • Rule-based score (for reference)         │
│  • Specific question/task                   │
└─────────────────────────────────────────────┘
```

**Key prompt design decisions:**

1. **Low temperature (0.3)**: Prioritizes consistency and clinical accuracy
2. **Structured FHIR context**: Patient data is formatted into a readable clinical summary
3. **JSON output format**: Ensures parseable, structured AI responses
4. **Rule-based baseline**: Provided to AI for calibration and comparison
5. **Safety instructions**: AI is instructed to flag uncertainty and recommend human review

### Sequence Diagrams

#### AI Patient Analysis

```
Frontend          API Layer         AI Agent Service      OpenAI        FHIR Server
   │                  │                    │                 │               │
   │ GET /ai-analysis │                    │                 │               │
   │─────────────────►│                    │                 │               │
   │                  │ analyze_patient()  │                 │               │
   │                  │───────────────────►│                 │               │
   │                  │                    │ get FHIR data   │               │
   │                  │                    │────────────────────────────────►│
   │                  │                    │◄────────────────────────────────│
   │                  │                    │                 │               │
   │                  │                    │ rule-based score│               │
   │                  │                    │ (risk_calculator)               │
   │                  │                    │                 │               │
   │                  │                    │ build prompt    │               │
   │                  │                    │ + call LLM      │               │
   │                  │                    │────────────────►│               │
   │                  │                    │◄────────────────│               │
   │                  │                    │                 │               │
   │                  │                    │ parse + combine │               │
   │                  │ AIAnalysis result  │                 │               │
   │                  │◄───────────────────│                 │               │
   │  JSON response   │                    │                 │               │
   │◄─────────────────│                    │                 │               │
```

#### AI Chat Conversation

```
Frontend          API Layer         AI Agent Service      OpenAI        FHIR Server
   │                  │                    │                 │               │
   │ POST /ai/chat    │                    │                 │               │
   │ {message,        │                    │                 │               │
   │  patient_id,     │                    │                 │               │
   │  history}        │                    │                 │               │
   │─────────────────►│                    │                 │               │
   │                  │ chat_with_agent()  │                 │               │
   │                  │───────────────────►│                 │               │
   │                  │                    │                 │               │
   │                  │                    │ [if patient_id] │               │
   │                  │                    │ gather FHIR data│               │
   │                  │                    │────────────────────────────────►│
   │                  │                    │◄────────────────────────────────│
   │                  │                    │                 │               │
   │                  │                    │ build system    │               │
   │                  │                    │ prompt + history│               │
   │                  │                    │ + user message  │               │
   │                  │                    │────────────────►│               │
   │                  │                    │◄────────────────│               │
   │                  │                    │                 │               │
   │                  │ ChatResponse       │                 │               │
   │                  │◄───────────────────│                 │               │
   │ {response,       │                    │                 │               │
   │  fhir_sources,   │                    │                 │               │
   │  confidence,     │                    │                 │               │
   │  ai_used}        │                    │                 │               │
   │◄─────────────────│                    │                 │               │
```

#### Graceful Degradation

```
Frontend          API Layer         AI Agent Service      Fallback
   │                  │                    │                  │
   │ GET /ai-analysis │                    │                  │
   │─────────────────►│                    │                  │
   │                  │ analyze_patient()  │                  │
   │                  │───────────────────►│                  │
   │                  │                    │                  │
   │                  │                    │ check            │
   │                  │                    │ is_ai_available  │
   │                  │                    │                  │
   │                  │               [AI NOT available]      │
   │                  │                    │                  │
   │                  │                    │ fallback_analysis│
   │                  │                    │─────────────────►│
   │                  │                    │◄─────────────────│
   │                  │                    │                  │
   │                  │ AIAnalysis         │                  │
   │                  │ (rule-based only,  │                  │
   │                  │  ai_used=false)    │                  │
   │                  │◄───────────────────│                  │
   │ JSON response    │                    │                  │
   │◄─────────────────│                    │                  │
```

---

## Hybrid Approach: AI + Rule-Based

### Why Hybrid?

| Concern | AI Agent | Rule Engine | Hybrid Benefit |
|---------|----------|-------------|----------------|
| **Accuracy** | Nuanced, context-aware | Consistent, deterministic | Best of both worlds |
| **Explainability** | Natural language reasoning | Factor-by-factor breakdown | Multiple explanation formats |
| **Reliability** | Depends on API availability | Always available | Graceful degradation |
| **Novel risks** | Can identify non-obvious patterns | Limited to predefined factors | Broader risk coverage |
| **Speed** | ~2-5 seconds (API call) | < 100ms | Fast baseline + rich AI layer |
| **Cost** | API usage costs | Free | AI only when needed |

### Integration Pattern

```
Patient Request ──► Rule-Based Score (always runs, ~100ms)
                          │
                    ┌─────┴─────┐
                    │ AI Enabled │
                    └─────┬─────┘
                     Yes  │  No
                ┌─────────┴──────────┐
                ▼                    ▼
         AI Analysis          Return rule-based
         (~2-5 seconds)       result only
                │
                ▼
         Merge Results
         (AI score + rule score + insights + reasoning)
                │
                ▼
         Return Hybrid Response
```

---

## AI vs Rule-Based Comparison

| Dimension | Rule-Based Engine | AI Agent |
|-----------|-------------------|----------|
| **Input** | Structured FHIR fields | Full patient context |
| **Algorithm** | Weighted factor sum | LLM clinical reasoning |
| **Output** | Numeric score + level | Score + insights + reasoning |
| **Risk factors** | 6 predefined | Unlimited (context-dependent) |
| **Discharge plan** | Template-based | Personalized narrative |
| **Interaction** | None (API only) | Conversational chat |
| **Availability** | Always | Requires API key |
| **Latency** | < 100ms | 2-5 seconds |
| **Determinism** | Fully deterministic | Mostly consistent (temp=0.3) |

---

## Presentation Layer (Frontend)

### Technology: React 18

**Components & Views**:

| Component | Description |
|-----------|-------------|
| **Dashboard** | Patient list with risk scores, AI analysis buttons |
| **AI Chat** | Conversational interface with patient context |
| **AI Analysis Modal** | Side-by-side AI vs rule comparison |
| **AI Discharge Modal** | AI-generated personalized plan |
| **Comparison View** | Multi-patient AI triage |
| **Risk Modal** | Rule-based factor breakdown |

**State Management**: React hooks (useState, useEffect, useRef)

**New AI-Specific State**:
- `aiStatus` — AI availability indicator
- `chatMessages` — Conversation history
- `aiAnalysis` — Current AI analysis result
- `comparisonResult` — Multi-patient comparison

---

## API Layer

### Technology: FastAPI

### AI Agent Endpoints (NEW)

```
GET    /api/v1/ai/status                        # AI availability check
POST   /api/v1/ai/chat                          # Conversational AI
GET    /api/v1/patients/{id}/ai-analysis         # AI risk analysis
POST   /api/v1/ai/compare-patients               # Multi-patient comparison
POST   /api/v1/patients/{id}/ai-discharge-plan   # AI discharge plan
```

### Core Endpoints

```
GET    /api/v1/health
GET    /api/v1/patients
GET    /api/v1/patients/{id}
GET    /api/v1/patients/{id}/risk-assessment
POST   /api/v1/patients/{id}/discharge-plan
GET    /api/v1/statistics
```

---

## Service Layer

### AI Agent Service (`ai_agent_service.py`) — NEW 🤖

- **Pattern**: Agent + Facade
- **Purpose**: LLM-powered clinical reasoning orchestration
- **Dependencies**: OpenAI API, FHIR Client, Risk Calculator
- **Key Methods**:
  - `analyze_patient_with_ai()`: Hybrid risk assessment
  - `chat_with_agent()`: Conversational clinical Q&A
  - `generate_ai_discharge_plan()`: Personalized discharge narrative
  - `compare_patients()`: Multi-patient triage ranking

### FHIRService (`fhir_service.py`)

- **Pattern**: Facade
- **Purpose**: FHIR data orchestration
- **Methods**: `get_all_patients_summary()`, `get_patient_risk_assessment()`, etc.

### RiskCalculator (`risk_calculator.py`)

- **Pattern**: Strategy
- **Purpose**: Deterministic risk scoring algorithm
- **Methods**: `calculate_risk()`, individual factor calculators

### CarePlanGenerator (`care_plan_generator.py`)

- **Pattern**: Factory
- **Purpose**: FHIR CarePlan + Task resource creation

---

## Core Layer

### FHIR Client (`fhir_client.py`)
- **Pattern**: Adapter
- HTTP wrapper for InterSystems IRIS FHIR R4 API
- **IRIS quirk**: `POST /fhir/r4/{Resource}` returns HTTP 201 with an **empty body** (Content-Length: 0). The `create_resource()` method handles this by checking `response.content` before calling `.json()` and falling back to the `Location` header to extract the assigned resource ID. The same applies to `MedicationRequest` searches — the `_sort=-authored-on` parameter is not supported by IRIS and returns 400; it is omitted.

### OpenAI Client (within `ai_agent_service.py`)
- **Pattern**: Adapter
- AsyncOpenAI client for GPT-4o API calls
- Requires `gpt-4o` or `gpt-4-turbo` — base `gpt-4` lacks `response_format=json_object` (JSON mode) and causes fallback to rule-based mode
- Retry logic for rate limits and transient errors

### Configuration (`config.py`)
- **Pattern**: Singleton (Pydantic BaseSettings)
- **New fields**: `OPENAI_API_KEY`, `AI_MODEL`, `AI_TEMPERATURE`, `AI_MAX_TOKENS`, `AI_ENABLED`

---

## Design Patterns

### AI-Specific Patterns

#### 1. AI Orchestration (Agent Pattern)

The `AIAgentService` acts as an autonomous agent:
- **Perceives**: Gathers FHIR data across resource types
- **Reasons**: Constructs prompts and invokes LLM
- **Acts**: Returns structured clinical insights
- **Adapts**: Handles errors with fallback strategies

#### 2. Graceful Degradation

```python
if self.is_ai_available:
    return await self._ai_analysis(patient_id)
else:
    return self._generate_fallback_analysis(patient_id)
```

Ensures 100% uptime regardless of AI availability.

#### 3. Prompt Template Pattern

Structured prompt construction with:
- System-level clinical persona
- Dynamic FHIR data injection
- Output format specification
- Safety guardrails

### Existing Patterns

1. **Dependency Injection**: Services receive dependencies via module-level singletons
2. **Facade Pattern**: FHIRService simplifies complex subsystem interactions
3. **Strategy Pattern**: Risk calculator with pluggable factor calculators
4. **Factory Pattern**: FHIR resource creation (CarePlan, Task)

---

## SOLID Principles

### Single Responsibility (SRP)
- `ai_agent_service.py` — AI reasoning only
- `risk_calculator.py` — Deterministic scoring only
- `care_plan_generator.py` — FHIR resource creation only
- `fhir_client.py` — FHIR communication only

### Open/Closed (OCP)
- AI prompts can be extended without modifying core service
- Risk factors configurable via environment
- New AI capabilities added as new methods

### Dependency Inversion (DIP)
- AI Agent depends on abstract FHIR client interface
- Configuration injected via Settings
- OpenAI client abstracted behind `_call_llm()` method

---

## Data Flow

### AI Analysis Flow

```
1. User clicks "🤖 AI Analysis" in UI
2. Frontend sends GET /api/v1/patients/{id}/ai-analysis
3. API Layer calls AIAgentService.analyze_patient_with_ai()
4. AIAgentService:
   a. Gathers FHIR data (Patient, Encounters, Conditions, Meds, Observations)
   b. Runs rule-based risk_calculator for baseline score
   c. Builds clinical context prompt with FHIR data
   d. Calls GPT-4 via _call_llm()
   e. Parses AI response (risk level, insights, reasoning, recommendations)
   f. Merges AI analysis with rule-based baseline
5. Returns AIAnalysis with both AI and rule-based results
6. Frontend renders side-by-side comparison modal
```

### Chat Flow

```
1. User types message in AI Chat interface
2. Frontend sends POST /api/v1/ai/chat with message, patient_id, history
3. AIAgentService.chat_with_agent():
   a. If patient_id: gathers FHIR data for context
   b. Builds system prompt with clinical persona + FHIR data
   c. Appends conversation history
   d. Calls GPT-4
   e. Returns ChatResponse with FHIR sources cited
4. Frontend appends response to conversation, auto-scrolls
```

---

## Error Handling

### AI-Specific Error Handling

| Error Type | Handling Strategy |
|------------|-------------------|
| No API Key | Fallback to rule-based mode |
| Rate Limit (429) | Retry with backoff, then fallback |
| Connection Error | Fallback to rule-based mode |
| Invalid Response | Log error, return fallback analysis |
| Timeout | Fallback to rule-based mode |
| AI Disabled (config) | Skip AI, use rules only |

### Layered Error Strategy

- **API Layer**: Catches exceptions → HTTP 500 with message
- **AI Service**: Catches OpenAI errors → graceful fallback
- **Service Layer**: Validates business logic → descriptive exceptions
- **Core Layer**: Handles HTTP errors → propagates up

---

## Security Considerations

### AI Security

- **API Key**: Stored in environment variables, never exposed to frontend
- **Data Privacy**: Patient data sent to OpenAI for processing — configurable via `AI_ENABLED` toggle
- **Prompt Injection**: System prompts define strict clinical persona boundaries
- **Output Validation**: AI responses parsed and validated before returning to client

### FHIR Security

- Basic Auth for IRIS (credentials in env vars)
- CORS restricted to frontend origin
- Pydantic validation on all inputs

---

## Performance

| Operation | Latency | Notes |
|-----------|---------|-------|
| Rule-based risk score | < 100ms | Deterministic calculation |
| AI patient analysis | 2-5s | Includes FHIR data gathering + LLM call |
| AI chat response | 1-3s | Depends on context size |
| AI discharge plan | 3-5s | Comprehensive narrative generation |
| AI patient comparison | 3-7s | Multiple patients processed |

### Optimization Strategies

- **Async I/O**: All operations use async/await
- **Parallel FHIR queries**: Multiple resources fetched concurrently
- **Low temperature**: Reduces LLM processing time
- **Token limits**: `AI_MAX_TOKENS` controls response size and cost

---

## Deployment Architecture

### Development (Docker Compose)

```
Docker Compose:
├── IRIS Container (port 52773) — FHIR Server
│   ├── config/iris/merge.cpf → /tmp/merge.cpf  (memory tuning)
│   └── FHIR endpoint installed via install_fhir.txt after first boot
├── Backend Container (port 8000) — FastAPI + AI Agent
│   └── env: OPENAI_API_KEY, AI_MODEL, FHIR_BASE_URL, CORS_ORIGINS (JSON array)
└── Frontend Container (port 3000) — React + AI Chat
```

### IRIS Memory Configuration

The file `config/iris/merge.cpf` is mounted into the IRIS container and applied at startup via `ISC_CPF_MERGE_FILE`. The critical setting is:

```ini
[config]
globals=256,0,0,0,0,0   # 256 MB global buffer — required for FHIR schema installation
```

Without sufficient memory, `InstallInstance` will fail mid-compilation with out-of-memory errors.

### FHIR Endpoint Installation (Post-Boot Step)

The IRIS for Health image does not come with a FHIR endpoint pre-configured. The endpoint must be installed once via InterSystems ObjectScript after the container is healthy:

**Script (`config/iris/install_fhir.txt`):**
```objectscript
// Step 1: Add HealthShare package mapping (required by FHIR installer)
set sc = ##class(%IPM.Utils.Module).AddPackageMapping("%ALL", "%SYSTEM.Context.HealthShare", "HSLIB")

// Step 2: Install FHIR R4 endpoint
set sc = ##class(HS.FHIRServer.Installer).InstallInstance(
    "/fhir/r4",
    "HS.FHIRServer.Storage.Json.InteractionsStrategy",
    "hl7.fhir.r4.core@4.0.1"
)
```

**What this creates:**
- FHIR endpoint at `/fhir/r4` in the HSSYS namespace
- A generated search schema `HSFHIR.X000x.*` (e.g., `HSFHIR.X0008.*`) containing:
  - `HSFHIR.X0008.R.*` — FHIR resource storage classes (~145 classes)
  - `HSFHIR.X0008.S.*` — FHIR search index classes (~145 classes, with 20-40 search parameter properties each)
  - `HSFHIR.X0008.V.*` — FHIR value set classes
- SQL Tables accessible as `HSFHIR_X0008_S.Patient`, `HSFHIR_X0008_S.Encounter`, etc.

> **Important**: If the `InstallInstance` call is interrupted (container OOM, Ctrl+C, timeout), the search classes may be generated with only 3 stub properties instead of the full 20-40 search parameters. This causes `<PROPERTY DOES NOT EXIST>` errors on FHIR write operations. The fix is to run `UninstallInstance` followed by a fresh `InstallInstance`.

### FHIR SQL Schema Naming

The generated SQL schema name follows the pattern `HSFHIR_X000x_S` where `x` increments with each installation:

| Installation | Schema | Table example |
|---|---|---|
| 1st | `HSFHIR_X0001_S` | `HSFHIR_X0001_S.Patient` |
| 2nd (after uninstall) | `HSFHIR_X0002_S` | `HSFHIR_X0002_S.Patient` |
| nth | `HSFHIR_X000n_S` | `HSFHIR_X000n_S.Patient` |

The `fhir_sql_analytics.py` service queries via the IRIS REST SQL endpoint and uses the current schema version. The schema version can be discovered with:
```sql
SELECT * FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME LIKE 'HSFHIR%'
```

### IRIS Authentication

- **Default credentials**: `SuperUser` / `SYS`
- **FHIR GET requests** (e.g., `/fhir/r4/metadata`): No authentication required
- **FHIR write requests** (POST/PUT/DELETE): HTTP Basic Auth required
- The backend passes `IRIS_USERNAME` / `IRIS_PASSWORD` from environment variables

> After first boot, the IRIS community image may set `ChangePassword=1` on the SuperUser account. If login via the Management Portal fails, fix it by running:
> ```bash
> echo 'set props("ChangePassword")=0' | docker exec -i smart-discharge-iris bash -c 'iris session IRIS -U %SYS'
> ```

### Environment Variables

```
# Required
FHIR_BASE_URL      → http://iris:52773/fhir/r4   (internal Docker hostname)
IRIS_USERNAME      → SuperUser
IRIS_PASSWORD      → SYS
CORS_ORIGINS       → ["http://localhost:3000","http://localhost:3001"]  ← JSON array!

# Optional (AI features) — recommended: set in .env file at project root
OPENAI_API_KEY     → sk-...
AI_MODEL           → gpt-4o   # gpt-4o or gpt-4-turbo required (JSON mode support)
AI_ENABLED         → true
```

**Critical**: `CORS_ORIGINS` must be a valid JSON array string. pydantic-settings v2 does not coerce a plain URL string to a list — it will raise a `SettingsError` and prevent the backend from starting.

---

## Future Enhancements

### Short Term
1. **Streaming AI responses** — Real-time token streaming in chat
2. **Prompt caching** — Cache system prompts for faster responses
3. **AI audit log** — Track all AI interactions for compliance

### Medium Term
1. **Fine-tuned model** — Custom clinical model for better accuracy
2. **RAG integration** — Retrieval-augmented generation with clinical guidelines
3. **Multi-modal AI** — Process clinical images and documents
4. **FHIR SQL Builder** — Native IRIS queries for complex analytics

### Long Term
1. **On-premise LLM** — Self-hosted model for data sovereignty
2. **Clinical validation** — Prospective studies comparing AI vs rule accuracy
3. **Multi-tenant** — Support multiple hospitals with isolated AI contexts

---

## InterSystems Platform Features

### FHIR SQL Builder Integration

FHIR SQL Builder is a core InterSystems IRIS for Health feature that creates SQL projections of FHIR resources. Our application uses it for population-level analytics.

**Architecture:**

```
┌────────────────────────────────────────────────────────────────────┐
│  InterSystems IRIS for Health                                      │
│                                                                    │
│  ┌──────────────────┐         ┌────────────────────────────────┐  │
│  │  FHIR Repository │         │  FHIR SQL Builder              │  │
│  │  (REST API)      │────────►│  (Auto-generated SQL Tables)   │  │
│  │                  │         │                                │  │
│  │  POST /fhir/r4/  │         │  Schema: HSFHIR_X0001_S       │  │
│  │  Patient         │         │  ┌──────────────────────────┐ │  │
│  │  Encounter       │         │  │ Patient (SQL table)      │ │  │
│  │  Condition       │         │  │ Encounter (SQL table)    │ │  │
│  │  Observation     │         │  │ Condition (SQL table)    │ │  │
│  │  MedicationReq   │         │  │ Observation (SQL table)  │ │  │
│  │  CarePlan, Task  │         │  │ MedicationRequest        │ │  │
│  └──────────────────┘         │  │ CarePlan, Task           │ │  │
│                               │  └──────────────────────────┘ │  │
│                               └──────────────┬─────────────────┘  │
│                                              │                    │
│                               ┌──────────────┴─────────────────┐  │
│                               │  SQL Execution Engine          │  │
│                               │  REST: /api/atelier/v1/…/sql   │  │
│                               │  JDBC/ODBC also available      │  │
│                               └────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────┘
```

**Implementation:** `backend/app/services/fhir_sql_analytics.py`

**SQL Queries Demonstrated:**

| # | Query | FHIR Resources | SQL Feature |
|---|-------|----------------|-------------|
| 1 | Patient demographics | Patient | COUNT, AVG, MIN, MAX |
| 2 | Gender distribution | Patient | GROUP BY |
| 3 | Encounter frequency | Patient ⟷ Encounter | Cross-resource JOIN |
| 4 | Condition prevalence | Condition | Nested element aggregation |
| 5 | High-risk population | Patient ⟷ Encounter ⟷ Condition | 3-table JOIN + HAVING |
| 6 | Medication utilization | MedicationRequest | CodeableConcept query |
| 7 | Readmission candidates | Patient ⟷ Encounter | CASE-based stratification |
| 8 | Polypharmacy analysis | MedicationRequest | Aggregation with CASE |

**Example SQL (Patient-Encounter JOIN):**

```sql
SELECT 
    p.Key as patient_id,
    COUNT(e.Key) as encounter_count,
    MIN(e.Period_start) as first_encounter,
    MAX(e.Period_start) as last_encounter
FROM HSFHIR_X0001_S.Patient p
LEFT JOIN HSFHIR_X0001_S.Encounter e 
    ON e.Subject = CONCAT('Patient/', p.Key)
GROUP BY p.Key
HAVING COUNT(e.Key) > 0
ORDER BY encounter_count DESC
```

**Example SQL (3-Table High-Risk Population):**

```sql
SELECT 
    p.Key as patient_id,
    DATEDIFF('yy', p.BirthDate, CURRENT_DATE) as age,
    COUNT(DISTINCT e.Key) as total_encounters,
    COUNT(DISTINCT c.Key) as active_conditions
FROM HSFHIR_X0001_S.Patient p
LEFT JOIN HSFHIR_X0001_S.Encounter e 
    ON e.Subject = CONCAT('Patient/', p.Key)
LEFT JOIN HSFHIR_X0001_S.Condition c 
    ON c.Subject = CONCAT('Patient/', p.Key)
GROUP BY p.Key, p.BirthDate, p.gender
HAVING COUNT(DISTINCT e.Key) >= 2 OR COUNT(DISTINCT c.Key) >= 2
ORDER BY total_encounters DESC
```

**API Endpoints:**

| Endpoint | Description |
|----------|-------------|
| `GET /api/v1/analytics/sql-stats` | Population analytics via SQL Builder |
| `GET /api/v1/analytics/readmission-sql` | Readmission-specific SQL analytics |
| `GET /api/v1/analytics/sql-builder-info` | SQL Builder configuration info |

**Why SQL Builder vs REST API?**

| Operation | FHIR REST API | FHIR SQL Builder |
|-----------|---------------|------------------|
| Patient count | Multiple API calls + client counting | `SELECT COUNT(*) FROM Patient` |
| Age statistics | Fetch all → calculate client-side | `SELECT AVG(DATEDIFF(...))` |
| Cross-resource analysis | N+1 API calls | Single JOIN query |
| Population filtering | Client-side filtering | `WHERE` / `HAVING` clauses |
| Risk stratification | Application logic | `CASE` expressions in SQL |

---

### AI Hub Integration

The AI Hub pattern from InterSystems provides a framework for integrating AI/ML capabilities with healthcare data in IRIS. Our implementation follows this pattern using OpenAI GPT-4 as the external LLM provider.

**Architecture:**

```
┌─────────────────────────────────────────────────────────────────────┐
│                    AI Hub Integration Pattern                       │
│                                                                     │
│  ┌──────────────┐    ┌──────────────────┐    ┌──────────────────┐  │
│  │ IRIS FHIR    │    │  AI Agent Svc    │    │  OpenAI GPT-4    │  │
│  │ Data Store   │───►│  (Orchestrator)  │───►│  (External LLM)  │  │
│  │              │    │                  │    │                  │  │
│  │ Patient      │    │  • Gather FHIR   │    │  • Reasoning     │  │
│  │ Encounter    │    │  • Build context │    │  • Analysis      │  │
│  │ Condition    │    │  • Call LLM      │    │  • Generation    │  │
│  │ Observation  │    │  • Parse result  │    │                  │  │
│  │ MedRequest   │    │  • Merge w/rules │    │                  │  │
│  └──────────────┘    └──────────────────┘    └──────────────────┘  │
│                             │                                       │
│                      ┌──────┴──────┐                                │
│                      │ Rule Engine │  (deterministic baseline)      │
│                      └─────────────┘                                │
│                                                                     │
│  Production Path: Replace OpenAI with IntegratedML                 │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  IRIS IntegratedML (future):                                 │  │
│  │    CREATE MODEL ReadmissionRisk PREDICTING (risk_level)     │  │
│  │    TRAIN MODEL ReadmissionRisk FROM PatientFeatures          │  │
│  │    SELECT PREDICT(ReadmissionRisk) FROM PatientFeatures     │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

**Implementation:** `backend/app/services/ai_agent_service.py`

**Key Design Decisions:**

1. **External LLM via AI Hub Pattern** — OpenAI GPT-4 as the reasoning engine, following AI Hub's model-agnostic integration approach
2. **FHIR-Grounded Reasoning** — All AI inputs are sourced from IRIS FHIR resources
3. **Orchestrator Pattern** — The AI Agent Service coordinates data retrieval, LLM calls, and result merging
4. **IntegratedML Compatibility** — The architecture supports replacing the external LLM with IRIS IntegratedML models trained on local data
5. **Graceful Degradation** — Mirrors AI Hub resilience: falls back to rules when AI is unavailable

---

## Conclusion

The architecture delivers a **true AI Agent for FHIR** through:

- **Hybrid Intelligence**: LLM reasoning + rule-based safety net
- **Clinical Focus**: Purpose-built prompts for healthcare decision support
- **Graceful Degradation**: 100% uptime with or without AI
- **FHIR Compliance**: Full R4 integration with InterSystems IRIS
- **Extensibility**: Clean separation enables easy enhancement
- **Transparency**: Side-by-side AI vs rule comparison for clinical trust
