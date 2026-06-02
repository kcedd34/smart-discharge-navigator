#!/bin/bash

echo "======================================"
echo "Smart Discharge Navigator"
echo "AI-Powered Clinical Reasoning Agent"
echo "Quick Start Script"
echo "======================================"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running. Please start Docker and try again."
    exit 1
fi

echo "✅ Docker is running"
echo ""

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Error: docker-compose is not installed. Please install it and try again."
    exit 1
fi

echo "✅ docker-compose is installed"
echo ""

# Check for OpenAI API Key
if [ -z "$OPENAI_API_KEY" ] || [ "$OPENAI_API_KEY" = "sk-your-openai-api-key-here" ]; then
    echo "⚠️  OPENAI_API_KEY is not set or is a placeholder."
    echo "   The system will run in RULE-BASED FALLBACK MODE."
    echo "   To enable AI Agent features:"
    echo "     1. Get an API key at https://platform.openai.com/api-keys"
    echo "     2. Export it: export OPENAI_API_KEY=sk-your-key-here"
    echo "     3. Then re-run this script."
    echo ""
    echo "   All core features work without AI. You'll miss:"
    echo "   • AI Clinical Chat"
    echo "   • AI-powered risk analysis"
    echo "   • AI discharge plan generation"
    echo "   • Multi-patient AI comparison"
    echo ""
else
    echo "✅ OPENAI_API_KEY is configured — AI Agent features enabled!"
    echo ""
fi

# ─── Start containers ────────────────────────────────────────────────────────
echo "🚀 Starting containers..."
docker-compose up -d

echo ""
echo "⏳ Waiting for IRIS for Health to become ready..."
echo "   (First start can take 3–5 minutes while IRIS initialises)"
echo ""

# Wait for IRIS to be ready.
# Primary: Docker healthcheck status (requires healthcheck to be enabled in docker-compose.yml).
# Fallback: HTTP probe against the management portal on port 52773.
attempt=0
max_attempts=40   # 40 × 15s = 10 minutes
while [ $attempt -lt $max_attempts ]; do
    # Use Go conditional template so this works whether healthcheck is enabled or not
    STATUS=$(docker inspect \
        --format='{{if .State.Health}}{{.State.Health.Status}}{{else}}no-healthcheck{{end}}' \
        smart-discharge-iris 2>/dev/null)

    if [ "$STATUS" = "healthy" ]; then
        echo "✅ IRIS is healthy!"
        break
    fi

    # Fallback: check if the IRIS web server is responding on port 52773
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 \
        http://localhost:52773/csp/sys/UtilHome.csp 2>/dev/null)
    if echo "$HTTP_CODE" | grep -qE "^(200|302|401)$"; then
        echo "✅ IRIS web server is responding (HTTP $HTTP_CODE) — allowing 20 s for full initialisation..."
        sleep 20
        break
    fi

    attempt=$((attempt + 1))
    echo "   IRIS not ready yet (docker status: ${STATUS:-unknown}, http: ${HTTP_CODE:-no response}) ... ($attempt/$max_attempts)"
    sleep 15
done

if [ $attempt -eq $max_attempts ]; then
    echo "❌ Timeout waiting for IRIS. Check logs with: docker-compose logs iris"
    exit 1
fi

# ─── Install FHIR R4 endpoint (idempotent) ───────────────────────────────────
echo ""
echo "🔬 Checking FHIR R4 endpoint..."

# Quick check via HTTP: if /fhir/r4/metadata returns 200, endpoint is installed.
METADATA_CODE=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 10 \
    http://localhost:52773/fhir/r4/metadata 2>/dev/null)

if [ "$METADATA_CODE" = "200" ]; then
    echo "✅ FHIR R4 endpoint already installed — skipping installation."
else
    echo "📦 Installing FHIR R4 endpoint (this takes 3–8 minutes on first run)..."
    echo "   The installer waits for Foundation.Install background jobs to complete"
    echo "   before calling InstallInstance — this avoids the namespace-not-ready race."

    SCRIPT_SRC="config/iris/install_fhir.txt"
    if [ ! -f "$SCRIPT_SRC" ]; then
        echo "❌ Installation script not found: $SCRIPT_SRC"
        echo "   Make sure you are running this script from the repository root."
        exit 1
    fi

    docker cp "$SCRIPT_SRC" smart-discharge-iris:/tmp/install_fhir.txt
    INSTALL_OUTPUT=$(docker exec -i smart-discharge-iris bash -c \
        'iris session IRIS -U %SYS < /tmp/install_fhir.txt 2>&1')

    if echo "$INSTALL_OUTPUT" | grep -q "FHIR Server Installation Complete"; then
        echo "✅ FHIR R4 endpoint installed successfully!"
    else
        # Secondary check via HTTP
        sleep 5
        VERIFY_CODE=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 10 \
            http://localhost:52773/fhir/r4/metadata 2>/dev/null)
        if [ "$VERIFY_CODE" = "200" ]; then
            echo "✅ FHIR R4 endpoint verified via HTTP — installation complete!"
        else
            echo "❌ FHIR endpoint installation may have failed. Last output:"
            echo "$INSTALL_OUTPUT" | tail -20
            echo ""
            echo "   Run manually:"
            echo "   docker cp config/iris/install_fhir.txt smart-discharge-iris:/tmp/install_fhir.txt"
            echo "   docker exec -i smart-discharge-iris bash -c 'iris session IRIS -U %SYS < /tmp/install_fhir.txt'"
            exit 1
        fi
    fi
fi

# ─── Post-install: CSP gateway routing + auth configuration ──────────────────
echo ""
echo "🔧 Configuring CSP gateway and IRIS authentication..."

SETUP_SCRIPT="config/iris/setup_fhir_post_install.sh"
if [ -f "$SETUP_SCRIPT" ]; then
    docker cp "$SETUP_SCRIPT" smart-discharge-iris:/tmp/setup_fhir_post_install.sh
    docker exec smart-discharge-iris bash /tmp/setup_fhir_post_install.sh
    echo "✅ CSP gateway and authentication configured."
else
    echo "⚠️  Post-install script not found: $SETUP_SCRIPT"
    echo "   FHIR requests may return 404 if CSP gateway is not configured."
fi

# ─── Wait for backend ────────────────────────────────────────────────────────
echo ""
echo "⏳ Waiting for Backend API to become ready..."

attempt=0
max_attempts=30
while [ $attempt -lt $max_attempts ]; do
    if curl -s http://localhost:8000/api/v1/health > /dev/null 2>&1; then
        echo "✅ Backend is ready!"
        break
    fi
    attempt=$((attempt + 1))
    echo "   Waiting... ($attempt/$max_attempts)"
    sleep 3
done

if [ $attempt -eq $max_attempts ]; then
    echo "❌ Timeout waiting for backend. Check logs with: docker-compose logs backend"
    exit 1
fi

# ─── Check AI status ─────────────────────────────────────────────────────────
echo ""
echo "🤖 Checking AI Agent status..."
AI_STATUS=$(curl -s http://localhost:8000/api/v1/ai/status 2>/dev/null)
if echo "$AI_STATUS" | grep -q '"ai_available":true'; then
    echo "✅ AI Agent is ACTIVE (GPT-4o ready)"
else
    echo "⚠️  AI Agent is in FALLBACK MODE (rule-based only)"
    echo "   Set OPENAI_API_KEY to enable AI features."
fi

# ─── Load sample data (automatic) ───────────────────────────────────────────
echo ""
echo "📊 Loading sample patient data (8 synthetic patients)..."
docker cp data/load_sample_data.py smart-discharge-backend:/tmp/load_sample_data.py
docker exec -e FHIR_BASE_URL=http://iris:52773/fhir/r4 \
    smart-discharge-backend python /tmp/load_sample_data.py \
    && echo "✅ Sample data loaded successfully!" \
    || echo "⚠️  Sample data load encountered issues — FHIR endpoint may need a moment. Re-run: docker exec smart-discharge-backend python /tmp/load_sample_data.py"

echo ""
echo "======================================"
echo "✅ All services are running!"
echo "======================================"
echo ""
echo "📊 Service URLs:"
echo "   Frontend:         http://localhost:3000"
echo "   AI Chat:          http://localhost:3000 (click 'AI Chat' tab)"
echo "   Backend API:      http://localhost:8000"
echo "   API Docs:         http://localhost:8000/docs"
echo "   AI Status:        http://localhost:8000/api/v1/ai/status"
echo "   FHIR Endpoint:    http://localhost:52773/fhir/r4/metadata"
echo "   IRIS Portal:      http://localhost:52773/csp/sys/UtilHome.csp"
echo "                     (Username: SuperUser, Password: SYS)"
echo ""
echo "📁 Useful commands:"
echo "   Load sample data: python3 data/load_sample_data.py"
echo "   View logs:        docker-compose logs -f"
echo "   Stop services:    docker-compose down"
echo ""
echo "======================================"

