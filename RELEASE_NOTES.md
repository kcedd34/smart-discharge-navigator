# Release Notes

## v1.1.0 — Bug Fix Release (2026-06-01)

**Commit**: `9899826`
**Branch**: `main`

This release addresses all issues reported during the InterSystems Programming Contest reviewer evaluation.

---

### Bug Fixes

#### 1. IRIS Healthcheck — `template: map does not contain key "Health"`

**Problem**: `docker-compose.yml` had `healthcheck: disable: true`, so `.State.Health` never existed at runtime. The `start.sh` wait loop used `docker inspect --format='{{.State.Health.Status}}'`, which crashed with a template parse error on every iteration — causing 60 failed attempts before timeout.

**Fix**:
- `docker-compose.yml`: Added a real healthcheck (`iris status IRIS 2>&1 | grep -qi running`, `interval: 10s`, `retries: 30`, `start_period: 90s`).
- `start.sh`: Replaced the broken template with a conditional Go template `{{if .State.Health}}{{.State.Health.Status}}{{else}}no-healthcheck{{end}}` that never crashes, plus an HTTP fallback probe against port 52773 — so the loop exits as soon as IRIS is reachable regardless of healthcheck state.

---

#### 2. FHIR Database Not Installed Automatically

**Problem**: `start.sh` ran `iris session IRIS -U HSSYS` — the `HSSYS` namespace does not exist in IRIS for Health Community Edition. The FHIR installation command silently failed and was never executed.

Additionally, the success check used `grep "EndpointExists:1"` — a string that never appears in the installation output — so even if the install ran, the script would always report failure.

**Fix**:
- `start.sh`: Changed namespace flag to `-U %SYS` (the correct system namespace where FHIR installer classes reside).
- `start.sh`: Changed success detection to `grep "FHIR Server Installation Complete"` (the actual string printed by `install_fhir.txt`), with an HTTP double-check (`curl /fhir/r4/metadata`) as a secondary verification.
- `install_fhir.txt`: Replaced ObjectScript block-style `if { } else { }` with single-line syntax (`if condition do ...`) — block style causes `<SYNTAX>` errors when the script is fed via stdin pipe.
- `start.sh`: Added idempotency check — if `/fhir/r4/metadata` already returns HTTP 200, the entire installation is skipped without re-running.

---

#### 3. AI Agent Returns "No Data" — Sample Patients Never Loaded

**Problem**: `start.sh` contained an interactive `read -r LOAD_DATA` prompt asking whether to load sample data. In non-interactive environments (CI, Docker exec, automated runs) this prompt received no input and execution was blocked or skipped, resulting in an empty FHIR database. The AI agent had no patient records to reason about.

**Fix**:
- `start.sh`: Removed the interactive prompt entirely. Sample data loading is now fully automatic — 8 synthetic patients (3 HIGH, 3 MODERATE, 2 LOW risk) are always created on first start.
- The script runs the loader inside the `smart-discharge-backend` container with `FHIR_BASE_URL=http://iris:52773/fhir/r4`, ensuring correct Docker network resolution.

---

#### 4. ObjectScript Compatibility in Piped Mode (`setup_fhir_post_install.sh`)

**Problem**: `Security.Users.Open("SuperUser")` is not a valid method — the correct API is `Security.Users.%OpenId("SuperUser")`. Block-style `if $IsObject(user) { ... }` and `try { ... } catch { ... }` statements cause `<SYNTAX>` errors when ObjectScript is executed line-by-line via stdin pipe.

The `RestartHTTPd()` call referenced `%SYS.HSDFHIR.Utils`, a class absent in IRIS for Health Community Edition, causing a `<CLASS DOES NOT EXIST>` error.

**Fix**:
- Changed `Security.Users.Open()` → `Security.Users.%OpenId()`.
- Converted all block-style conditionals to single-line ObjectScript compatible with piped execution.
- Removed the `RestartHTTPd()` call — confirmed unnecessary, the FHIR endpoint is accessible without it.

---

#### 5. Clarified That `docker-compose up -d` Alone Is Insufficient

**Problem**: Reviewers and users running `docker-compose up -d` directly (instead of `./start.sh`) would get containers running but no FHIR endpoint and no sample data, resulting in a broken application with no patients shown.

**Fix**:
- `README.md`: Added prominent `⚠️` warning blocks at the top of both the **Method 1** and **Method 2** installation sections, making clear that `docker-compose up -d` only starts the containers and that Steps 5–7 (or `./start.sh`) are required for a fully functional setup.

---

### Documentation Updates (`README.md`)

- **Step 4**: Replaced broken `docker inspect --format='{{.State.Health.Status}}'` with `curl -s -o /dev/null -w "%{http_code}" http://localhost:52773/csp/sys/UtilHome.csp`.
- **Step 5**: Clarified that `-U %SYS` is required and explained why.
- **Step 6**: Corrected description of what the CSP script actually does; noted that `/fhir/r4/metadata` is accessible before this step.
- **Step 7**: Updated `docker cp` path from `/app/` to `/tmp/`; removed the unnecessary `pip install requests` line.
- **Troubleshooting**: All `iris session IRIS` commands updated to include `-U %SYS`.
- **Troubleshooting — IRIS memory**: Replaced broken `docker inspect` command with the safe conditional template + HTTP probe.
- **Demo Video**: Added YouTube link.

---

### Files Changed

| File | Change |
|------|--------|
| `docker-compose.yml` | Real healthcheck replacing `disable: true` |
| `start.sh` | Fixed wait loop, FHIR install namespace, success detection, automatic data loading; removed ~80 lines of orphaned code |
| `config/iris/install_fhir.txt` | Single-line ObjectScript for piped-mode compatibility |
| `config/iris/setup_fhir_post_install.sh` | Correct `%OpenId()`, single-line syntax, removed unavailable class call |
| `README.md` | All commands corrected to match fixed code; troubleshooting updated; warning notes added for `docker-compose up -d` |

---

## v1.0.0 — Initial Release

Initial submission to InterSystems Programming Contest: AI Agents for FHIR 2026 (Task #9 — Hospital Readmission Risk Workbench).

**Features**:
- Hybrid AI Agent (GPT-4o) + rule-based risk scoring engine
- FHIR R4 read/write via InterSystems IRIS for Health
- FHIR SQL Builder analytics (population queries, polypharmacy detection)
- Conversational AI chat with FHIR patient context
- AI-powered discharge plan generation (CarePlan + Task resources)
- Multi-patient triage with AI prioritization rationale
- Graceful degradation to rule-based mode without API key
- React dashboard with tabbed navigation (Dashboard, AI Chat, Analytics)
- 8 synthetic sample patients across 3 risk categories
