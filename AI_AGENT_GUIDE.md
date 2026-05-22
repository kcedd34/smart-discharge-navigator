# AI Agent Guide 🤖

**Comprehensive Guide to the Smart Discharge Navigator AI Clinical Reasoning Agent**

---

## Table of Contents

- [Overview](#overview)
- [How the AI Agent Works](#how-the-ai-agent-works)
- [Getting Started](#getting-started)
- [AI Chat Interface](#ai-chat-interface)
- [AI Patient Analysis](#ai-patient-analysis)
- [AI Discharge Planning](#ai-discharge-planning)
- [Multi-Patient Comparison](#multi-patient-comparison)
- [Example Conversations](#example-conversations)
- [Prompt Engineering Details](#prompt-engineering-details)
- [Configuration](#configuration)
- [Best Practices for Clinical Queries](#best-practices-for-clinical-queries)
- [Limitations and Ethical Considerations](#limitations-and-ethical-considerations)
- [Troubleshooting](#troubleshooting)

---

## Overview

The Smart Discharge Navigator AI Agent is a **GPT-4-powered clinical reasoning system** that analyzes FHIR patient data and provides:

- **Conversational clinical Q&A** — ask questions about patients in natural language
- **Deep risk analysis** — AI-powered insights beyond what rule-based scoring captures
- **Personalized discharge plans** — contextual, patient-specific care narratives
- **Multi-patient triage** — AI comparison and prioritization across patients

The AI Agent works **alongside** the existing rule-based risk engine, providing a hybrid intelligence approach that is both powerful and reliable.

---

## How the AI Agent Works

### Data Flow

```
1. FHIR Data Collection
   └── Patient demographics, encounters, conditions,
       medications, vital signs from InterSystems IRIS

2. Clinical Context Building
   └── Structured summary of patient data formatted
       for LLM consumption

3. LLM Reasoning (GPT-4)
   └── Clinical reasoning with system-level medical
       persona and safety guardrails

4. Result Integration
   └── AI insights merged with rule-based baseline
       for comprehensive assessment
```

### What Data Does the AI See?

For each patient analysis, the AI Agent gathers:

| FHIR Resource | Data Extracted | Clinical Purpose |
|---------------|----------------|------------------|
| **Patient** | Name, age, gender, birth date | Demographics context |
| **Encounter** | Recent admissions, dates, types | Admission pattern analysis |
| **Condition** | Active diagnoses, ICD codes | Comorbidity assessment |
| **MedicationRequest** | Active medications, dosages | Polypharmacy & interaction risk |
| **Observation** | Vital signs, lab values | Physiological status assessment |

---

## Getting Started

> **Prerequisite**: The full application must be running before using the AI Agent. If you haven't done so yet, follow the installation guide in [README.md](README.md) — specifically the **FHIR endpoint installation step** (Step 3c) which is mandatory and not handled automatically by `docker-compose up`.

### 1. Start All Services

```bash
# Recommended: automated start script handles FHIR installation
./start.sh
```

The `start.sh` script:
- Starts all Docker containers
- Waits for IRIS to become healthy (up to 10 minutes)
- Installs the FHIR R4 endpoint if not already present (3–8 minutes)
- Loads sample data (optional, prompt at end)
- Verifies AI status

### 2. Obtain an OpenAI API Key (Optional — for AI features)

The system runs fully in **rule-based fallback mode** without a key.

1. Go to [platform.openai.com](https://platform.openai.com/)
2. Create an account or sign in
3. Navigate to **API Keys** → **Create new secret key**
4. Copy the key (starts with `sk-`)

### 3. Configure the API Key

Create a `.env` file in the project root (recommended — kept out of Git by `.gitignore`):

```bash
# .env
OPENAI_API_KEY=sk-your-key-here
AI_MODEL=gpt-4o
AI_ENABLED=true
```

> **Model requirement**: Use `gpt-4o` or `gpt-4-turbo`. The base `gpt-4` model does **not** support JSON mode (`response_format=json_object`), which the AI Agent requires for structured clinical analysis. Using base `gpt-4` will cause the system to silently fall back to rule-based mode.

Alternatively, export the key in the shell before starting:

```bash
# Linux / macOS
export OPENAI_API_KEY=sk-your-key-here
./start.sh

# Windows PowerShell
$env:OPENAI_API_KEY = "sk-your-key-here"
docker-compose up -d
```

Or set it permanently in `docker-compose.yml`:
```yaml
environment:
  - OPENAI_API_KEY=sk-your-key-here
```

### 4. Verify AI Status

```bash
curl http://localhost:8000/api/v1/ai/status
```

Expected response (AI active):
```json
{
  "ai_available": true,
  "model": "gpt-4o",
  "ai_enabled": true,
  "has_api_key": true
}
```

Expected response (rule-based fallback mode):
```json
{
  "ai_available": false,
  "model": "rule-based-fallback",
  "ai_enabled": true,
  "has_api_key": false
}
```

### 5. Check the UI

Look for the **AI Status badge** in the application header:
- 🟢 **"AI Active"** — Full AI Agent operational
- 🟡 **"AI Fallback"** — Rule-based mode (no API key)

---

## AI Chat Interface

### Accessing the Chat

1. Open the application at http://localhost:3000
2. Click the **"🤖 AI Chat"** tab in the navigation bar
3. The chat interface opens with:
   - **Left sidebar**: Patient context selector + suggested questions
   - **Main area**: Chat conversation with the AI Agent

### Patient Context

- **With patient selected**: AI responses are grounded in that patient's FHIR data
- **Without patient selected**: AI provides general clinical guidance

### Suggested Questions

The interface provides clinically relevant starter questions:
- "What are the main readmission risk factors for this patient?"
- "Are there any concerning medication interactions?"
- "What follow-up care would you recommend?"
- "Summarize this patient's clinical history"

### Conversation Memory

The chat maintains conversation history within a session, allowing:
- Follow-up questions that reference previous context
- Iterative exploration of clinical concerns
- Natural dialogue flow

---

## AI Patient Analysis

### How to Use

1. In the Dashboard, find a patient
2. Click **"🤖 AI Analysis"**
3. The analysis modal shows:

#### Score Comparison
Two side-by-side cards:
- **AI Score**: LLM-determined risk level with confidence percentage
- **Rule-Based Score**: Deterministic weighted score

#### Key AI Insights
Bullet-point list of AI-identified risk factors and clinical observations that go beyond what the rule engine captures.

#### Reasoning Steps
Step-by-step display of the AI's clinical reasoning process:
1. What the AI examined
2. What it found
3. Why it's clinically relevant

#### Risks Missed by Rules
Highlighted risks that the AI identified but the rule-based engine alone would not catch. This is a key differentiator of the AI Agent approach.

#### Recommendations
AI-generated, context-specific action items for the care team.

---

## AI Discharge Planning

### How to Use

1. Click **"🤖 AI Discharge Plan"** for any patient
2. The AI generates a comprehensive, personalized discharge plan including:
   - **Medication instructions** with interaction awareness
   - **Follow-up schedule** prioritized by clinical urgency
   - **Warning signs** — when to seek emergency care
   - **Lifestyle recommendations** tailored to conditions
   - **Care coordination** — referrals and specialist follow-ups

### AI vs Template Plans

| Aspect | Template Plan (Rule-based) | AI Discharge Plan |
|--------|---------------------------|-------------------|
| **Personalization** | Risk-level based templates | Patient-specific narratives |
| **Medications** | List of current meds | Interaction-aware guidance |
| **Follow-up** | Fixed intervals by risk level | Prioritized by clinical need |
| **Language** | Standard medical language | Patient-friendly, contextual |
| **Comprehensiveness** | Predefined checklist | Dynamic, condition-aware |

---

## Multi-Patient Comparison

### How to Use

1. Click **"Compare Patients"** in the dashboard toolbar
2. Select 2 or more patients by clicking their rows
3. Click **"AI Compare"**
4. View results:
   - **Risk Ranking**: AI-ordered list by clinical urgency
   - **Common Risk Factors**: Shared patterns across selected patients
   - **Unique Concerns**: Patient-specific flags
   - **Triage Recommendation**: AI-generated prioritization rationale

### Use Cases

- **Shift handoff**: Quickly prioritize patients for incoming team
- **Discharge planning**: Determine which patients need most attention
- **Resource allocation**: Focus intensive services on highest-need patients

---

## Example Conversations

### Example 1: General Risk Assessment

```
👤 User: What are the main readmission risk factors for this patient?

🤖 AI Agent: Based on the FHIR data for patient John Smith (72 years old),
I've identified several key readmission risk factors:

1. **Frequent Hospitalizations**: 3 admissions in the past 6 months,
   suggesting a pattern of clinical instability.

2. **Cardiac Comorbidities**: Active heart failure (I50.9) and chronic
   ischemic heart disease (I25.10) create significant interaction risk.

3. **Polypharmacy Concerns**: Currently on 8 active medications including
   metformin and lisinopril. The combination requires careful monitoring
   for renal function.

4. **Age-Related Risk**: At 72 years, recovery capacity is reduced and
   medication metabolism may be altered.

5. **Vital Sign Trends**: Recent blood pressure readings show borderline
   hypertension (145/92), which may indicate medication adjustment needed.

I recommend prioritizing this patient for intensive discharge planning
with cardiology follow-up within 7 days.

FHIR Sources: Patient, Encounter (3), Condition (4), MedicationRequest (8),
Observation (5)
```

### Example 2: Medication Query

```
👤 User: Should I be concerned about medication interactions?

🤖 AI Agent: Yes, there are potential interaction concerns worth reviewing:

1. **Metformin + Heart Failure**: Metformin should be used cautiously in
   patients with heart failure due to lactic acidosis risk, especially
   if renal function is compromised.

2. **Lisinopril + Spironolactone**: Both medications affect potassium
   levels. Combined use increases hyperkalemia risk. Recommend monitoring
   serum potassium levels.

3. **Polypharmacy Risk**: With 8 active medications, the cumulative
   side effect burden increases. Consider a comprehensive medication
   reconciliation before discharge.

I recommend a pharmacist consultation as part of the discharge process.
```

### Example 3: Discharge Planning

```
👤 User: What should the discharge plan focus on?

🤖 AI Agent: Given this patient's profile, the discharge plan should
prioritize:

1. **Cardiac Monitoring**
   - Daily weight monitoring for fluid retention
   - Blood pressure log twice daily
   - Report any chest pain or shortness of breath immediately

2. **Medication Management**
   - Pill organizer setup before discharge
   - Written medication schedule with times
   - Pharmacist phone number for questions

3. **Follow-up Appointments**
   - Cardiology: Within 7 days (HIGH priority)
   - Primary Care: Within 14 days
   - Endocrinology: Within 30 days (diabetes management)

4. **Home Environment**
   - Assess need for home health nursing (2-3x/week)
   - Consider telemonitoring for heart failure management
   - Fall risk assessment (age + multiple medications)
```

### Example 4: Comparative Analysis

```
👤 User: Compare readmission risk across my ICU patients

🤖 AI Agent: I've analyzed and ranked 3 ICU patients by readmission risk:

**Triage Priority:**

1. 🔴 **John Smith** (Risk: HIGH, Confidence: 87%)
   - Multiple cardiac comorbidities + frequent readmissions
   - Unique concern: Potential medication interactions

2. 🟠 **Maria Garcia** (Risk: MODERATE, Confidence: 78%)
   - COPD with recent exacerbation
   - Unique concern: Smoking cessation compliance

3. 🟢 **Robert Johnson** (Risk: LOW, Confidence: 82%)
   - Post-surgical recovery, no chronic conditions
   - Unique concern: Adequate pain management plan

**Common Risk Factors**: Age > 65, polypharmacy (5+ medications)

**Recommendation**: Focus intensive discharge planning on Mr. Smith,
with standard protocol for Ms. Garcia and basic discharge for Mr. Johnson.
```

---

## Prompt Engineering Details

### System Prompt Structure

The AI Agent uses carefully crafted prompts:

```
System Role:
"You are a clinical AI assistant specialized in hospital readmission
risk assessment. You analyze FHIR patient data and provide evidence-based
clinical reasoning."

Clinical Guidelines:
- Assess readmission risk based on established clinical factors
- Consider comorbidity interactions, not just individual conditions
- Provide specific, actionable recommendations
- Flag uncertainties and recommend human clinical review
- Use evidence-based medicine principles

Safety Guardrails:
- Always recommend physician review for high-risk findings
- Never provide definitive diagnoses
- Acknowledge limitations of AI-based assessment
- Reference FHIR data sources for transparency
```

### Prompt Design Principles

1. **Grounded in FHIR Data**: Every AI response is anchored to actual patient data from the FHIR server
2. **Structured Output**: JSON format ensures parseable, consistent responses
3. **Calibrated with Rules**: Rule-based score is provided for AI reference and comparison
4. **Safety First**: Guardrails prevent overconfident clinical claims
5. **Low Temperature (0.3)**: Prioritizes consistency over creativity in clinical context

---

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | *(required)* | Your OpenAI API key. Set via `.env` file (recommended) |
| `AI_MODEL` | `gpt-4o` | Model. Use `gpt-4o` or `gpt-4-turbo` — base `gpt-4` lacks JSON mode support |
| `AI_TEMPERATURE` | `0.3` | Randomness control (0.0–1.0, lower = more deterministic) |
| `AI_MAX_TOKENS` | `2000` | Maximum tokens in AI response |
| `AI_ENABLED` | `true` | Master toggle for AI features |

### Model Selection

| Model | Speed | Quality | Cost | Recommendation |
|-------|-------|---------|------|----------------|
| `gpt-4o` | Fast | Highest | Medium | **Default — required for JSON mode** |
| `gpt-4-turbo` | Fast | High | Medium | Compatible alternative |
| `gpt-4` | Slower | High | Higher | ⚠️ Does NOT support JSON mode — causes fallback |
| `gpt-3.5-turbo` | Fastest | Good | Lowest | Development/testing only |

### Cost Considerations

- Each AI analysis call uses ~1,000–3,000 tokens
- Chat messages use ~500–2,000 tokens per turn
- Estimated cost: $0.03–0.12 per AI interaction with GPT-4
- Use `AI_ENABLED=false` to disable AI and avoid costs

---

## Best Practices for Clinical Queries

### DO ✅

- **Be specific**: "What cardiac risk factors does this patient have?" is better than "Is this patient at risk?"
- **Ask about patterns**: "Are there any concerning trends in vital signs?"
- **Request comparisons**: "How does this patient compare to others with similar conditions?"
- **Ask for reasoning**: "Why is this patient considered high risk?"
- **Use patient context**: Always select a patient before asking patient-specific questions

### DON'T ❌

- **Don't use for diagnosis**: The AI provides risk assessment support, not diagnostic conclusions
- **Don't skip clinical review**: Always have a clinician review AI recommendations
- **Don't rely solely on AI**: Use alongside clinical judgment and rule-based scores
- **Don't share PHI externally**: Be aware that patient data is sent to OpenAI's API

---

## Limitations and Ethical Considerations

### Technical Limitations

1. **API Dependency**: AI features require internet access and OpenAI API availability
2. **Latency**: AI responses take 2-5 seconds vs milliseconds for rule-based scoring
3. **Token Limits**: Very complex patients with extensive history may exceed context windows
4. **Model Knowledge Cutoff**: GPT-4 has a training data cutoff and may not reflect latest clinical guidelines
5. **Non-Deterministic**: Responses may vary slightly between identical requests

### Clinical Limitations

1. **Not a Diagnostic Tool**: The AI Agent provides decision support, not clinical diagnoses
2. **No Real-Time Data**: Analysis is based on FHIR data snapshot, not live monitoring
3. **Limited to Available Data**: AI can only reason about data present in FHIR resources
4. **Cultural/Social Factors**: May not fully capture social determinants of health
5. **Generalization**: LLM clinical knowledge is general, not institution-specific

### Ethical Considerations

1. **Human Oversight Required**: AI recommendations must always be reviewed by qualified clinicians
2. **Data Privacy**: Patient data is transmitted to OpenAI's servers for processing
   - Consider `AI_ENABLED=false` for environments with strict data sovereignty requirements
   - Future enhancement: on-premise LLM deployment option
3. **Bias Awareness**: LLM outputs may reflect biases present in training data
4. **Transparency**: Side-by-side AI vs rule-based comparison enables clinical scrutiny
5. **Accountability**: Clinical decisions remain the responsibility of the treating physician

### Regulatory Notes

- This system is intended for **clinical decision support** only
- It does not replace clinical judgment or established clinical workflows
- Institutions should review AI usage against local regulatory requirements (HIPAA, GDPR, etc.)
- Consider establishing an AI governance framework before clinical deployment

---

## Troubleshooting

### Application Not Starting

**FHIR endpoint not installed (most common issue)**

After running `docker-compose up -d`, the FHIR `/fhir/r4` endpoint must be installed manually. This is the most common reason for a "Backend working but no patient data" situation.

```bash
# Check if endpoint exists
curl -o /dev/null -w "%{http_code}" http://localhost:52773/fhir/r4/metadata
# Expected: 200 (OK)
# If 404: install the FHIR endpoint

# Install FHIR endpoint
docker cp config/iris/install_fhir.txt smart-discharge-iris:/tmp/install_fhir.txt
docker exec -i smart-discharge-iris bash -c 'iris session IRIS -U HSSYS < /tmp/install_fhir.txt'
# Wait 3–8 minutes for class compilation to complete
```

**Backend crashes on startup with "error parsing value for field CORS_ORIGINS"**

```yaml
# WRONG — plain string not accepted by pydantic-settings v2
- CORS_ORIGINS=http://localhost:3000

# CORRECT — must be a JSON array
- CORS_ORIGINS=["http://localhost:3000","http://localhost:3001"]
```

**IRIS container exits or is unhealthy**

Docker needs at least 4 GB RAM allocated for the IRIS container. Check Docker resource settings and verify `config/iris/merge.cpf` contains `globals=256,0,0,0,0,0`.

### AI Not Available

```bash
# Check API key is set
echo $OPENAI_API_KEY

# Check AI status
curl http://localhost:8000/api/v1/ai/status

# Check backend logs
docker-compose logs backend | grep -i "ai\|openai"
```

### AI Returning Fallback Responses

1. Verify `OPENAI_API_KEY` is valid and not expired
2. **Check `AI_MODEL=gpt-4o`** — base `gpt-4` does **not** support `response_format=json_object` (JSON mode). The API returns HTTP 400 and the agent silently falls back to rule-based mode. Use `gpt-4o` or `gpt-4-turbo`
3. Check `AI_ENABLED=true` in `docker-compose.yml`
4. Ensure internet connectivity from backend container
5. Check OpenAI API status: [status.openai.com](https://status.openai.com/)

### Discharge Plan Fails — "Failed to generate discharge plan"

**Symptom**: Clicking "Generate Plan" shows an error dialog; backend logs show `JSONDecodeError: Expecting value: line 1 column 1 (char 0)` and `Error creating CarePlan`.

**Root cause**: IRIS returns HTTP 201 with an **empty response body** when creating FHIR resources (`CarePlan`, `Task`). The original `create_resource()` called `response.json()` on the empty body.

**Fix** (already applied in current codebase): `create_resource()` in `fhir_client.py` now checks `response.content` before calling `.json()` and extracts the resource ID from the `Location` response header instead. If you’ve just cloned the repo, everything should work. If running an older container, recreate it:
```bash
docker-compose up -d --no-deps --force-recreate backend
```

### No Patients Showing in Dashboard

1. Check that sample data was loaded: `python3 data/load_sample_data.py`
2. Verify FHIR endpoint is working: `curl http://localhost:52773/fhir/r4/Patient -u SuperUser:SYS`
3. Check backend can reach IRIS: `docker-compose logs backend | grep -i "fhir\|iris\|error"`

### FHIR Writes Failing (HTTP 500)

If `POST /fhir/r4/Patient` returns 500 with "PROPERTY DOES NOT EXIST":
- The FHIR search classes were not fully generated. Reinstall the endpoint:

```bash
docker cp config/iris/install_fhir.txt smart-discharge-iris:/tmp/install_fhir.txt
docker exec -i smart-discharge-iris bash -c 'iris session IRIS -U HSSYS < /tmp/install_fhir.txt'
```

### Slow AI Responses

- Consider switching to `gpt-4-turbo` or `gpt-3.5-turbo` for faster responses
- Reduce `AI_MAX_TOKENS` if shorter responses are acceptable
- Check network latency to OpenAI API

### Rate Limiting

If you see 429 errors in logs:
- The AI Agent automatically falls back to rule-based mode
- Consider reducing request frequency
- Upgrade OpenAI API plan for higher rate limits

---

**Built with ❤️ and 🤖 for InterSystems Programming Contest: AI Agents for FHIR 2026**
