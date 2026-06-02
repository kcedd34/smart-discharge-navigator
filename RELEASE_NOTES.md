# Release Notes

## v1.2.2 — ObjectScript Pipe Syntax Fix (2026-06-02)

**Branch**: `main`

Fixed `<SYNTAX>` errors in `setup_fhir_post_install.sh` caused by multi-line
`if { } else { }` block syntax, which is invalid when ObjectScript is executed
via stdin pipe (`iris session IRIS << 'EOF'`).

### Change

`config/iris/setup_fhir_post_install.sh`: Replaced block-style conditional:
```objectscript
if '##class(Security.Applications).Exists("/fhir") {
    do ##class(Security.Applications).Create(...)
} else {
    do ##class(Security.Applications).Modify(...)
}
```
With equivalent single-line syntax:
```objectscript
set fhirAppExists = ##class(Security.Applications).Exists("/fhir")
if 'fhirAppExists do ##class(Security.Applications).Create("/fhir", .props)
if 'fhirAppExists write "CSP application /fhir created",!
if fhirAppExists do ##class(Security.Applications).Modify("/fhir", .props)
if fhirAppExists write "CSP application /fhir already exists — updated.",!
```

> **Rule**: In piped/stdin ObjectScript execution, every statement must be
> on a single line. Multi-line `{ }` blocks are only valid in interactive
> terminal sessions or compiled `.mac` routines.

### Verified end-to-end on clean environment

```
docker-compose down -v && ./start.sh
```
- ✅ IRIS starts and reaches healthy state
- ✅ FHIR R4 endpoint installs (`Foundation.Install` + 45s wait + `InstallInstance`)
- ✅ CSP gateway configured (no `<SYNTAX>` errors)
- ✅ 8 sample patients loaded
- ✅ `curl http://localhost:52773/fhir/r4/metadata` → HTTP 200
- ✅ Frontend at http://localhost:3000 shows patient dashboard

---

## v1.2.1 — Revert to Runtime FHIR Install (2026-06-02)

**Branch**: `main`

Reverts the build-time FHIR installation introduced in v1.2.0 after discovering
that IRIS detects a hostname change (`buildkitsandbox` → runtime container) and
the `/fhir/r4` REST web application registration becomes inaccessible (HTTP 404),
even though the FHIRSERVER database mounts correctly.

### Root Cause of v1.2.0 Regression

When IRIS runs inside `docker build`, it registers the FHIR endpoint under the
build node hostname `buildkitsandbox`. When the resulting image starts as a
container, IRIS logs `System appears to have failed over from node buildkitsandbox`
and the CSP/web-application registration for `/fhir/r4` is not served correctly.

### Changes

- `docker-compose.yml`: Reverted to `image: intersystemsdc/irishealth-community:latest`
- `start.sh`: Restored runtime FHIR installation block; `docker-compose up -d` (no `--build`)
- `README.md`: Restored installation instructions to runtime approach
- `config/iris/Dockerfile`: Kept in repo as reference / for CI pre-build use cases, but no longer used by default

### What Still Fixes the Original Race Condition

`config/iris/install_fhir.txt` retains the **poll loop** added in v1.2.0:

```objectscript
for {
    quit:##class(%SYS.Namespace).Exists("FHIRSERVER")
    hang 2
}
```

This waits for `Foundation.Install("FHIRSERVER")` background jobs to complete
before calling `InstallInstance` — which was the root cause of the reviewer's
issue ("package attempted to install FHIR BEFORE the FHIRSERVER namespace was
installed").

---

## v1.2.0 — FHIR Setup Race Condition Fix (2026-06-02)

**Branch**: `main`

This release fixes the root cause of the FHIR installation failure reported by the InterSystems Open Exchange reviewer: *"the package attempted to install the FHIR application BEFORE the FHIRSERVER namespace and database were installed."*

---

### Root Cause

`HS.Util.Installer.Foundation.Install("FHIRSERVER")` spawns background jobs to create the FHIRSERVER namespace and database. The previous `start.sh` called the FHIR installer (`HS.FHIRServer.Installer.InstallInstance`) immediately on the next line — before those background jobs finished — resulting in a **"namespace not ready"** error on a clean first run.

### Fix

**FHIR installation is now performed at Docker image build time**, not at container startup.

A new `config/iris/Dockerfile` extends `intersystemsdc/irishealth-community:latest`, runs IRIS, executes `install_fhir.txt` (which now includes an explicit wait loop after `Foundation.Install`), configures the CSP gateway, and stops IRIS. The resulting image layer already contains the fully configured FHIR R4 endpoint.

On `docker-compose up`, the `iris-data` named volume is initialised from this pre-built image layer — so **FHIR is available immediately, with no runtime installation step**.

---

### Changes

#### `config/iris/Dockerfile` *(new)*

New Dockerfile for the IRIS service. Inherits `intersystemsdc/irishealth-community:latest`, runs `install_fhir.txt` + `setup_fhir_post_install.sh` at build time, and saves the configured IRIS state into the image.

#### `config/iris/install_fhir.txt`

- Added an explicit **poll loop** after `Foundation.Install("FHIRSERVER")` that waits (up to 120 s) until `%SYS.Namespace.Exists("FHIRSERVER")` returns true — guaranteeing the namespace is ready before `InstallInstance` is called.
- Improved step-by-step console output for easier debugging.

#### `config/iris/setup_fhir_post_install.sh`

- Added existence check before `Security.Applications.Create("/fhir")` — if the CSP app already exists, it calls `Modify` instead of `Create`. This makes the script fully idempotent (safe to run on an image that already configured it during build).

#### `docker-compose.yml`

- Replaced `image: intersystemsdc/irishealth-community:latest` with a `build:` directive pointing to `config/iris/Dockerfile` (context = project root).
- Users now run `docker-compose up --build` on the first run; subsequent runs use the cached image.

#### `start.sh`

- Changed `docker-compose up -d` → `docker-compose up --build -d` so the first run always triggers the image build automatically.
- Replaced the FHIR installation block with a simple readiness check: if `/fhir/r4/metadata` returns 200, the app is ready; otherwise a clear error message tells the user to run `docker-compose up --build`.

#### `README.md`

- Updated Quick Start to clarify that `--build` is needed on the first run.
- Rewrote Installation sections (both Method 1 and Method 2): removed the manual IRIS terminal session for FHIR install (Step 5 is now just a verification `curl`), updated restart and reset instructions.

---

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
