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
echo "⏳ Waiting for IRIS for Health to become healthy..."
echo "   (First start can take 3–5 minutes while IRIS initialises)"
echo ""

# Wait for IRIS healthcheck to pass
attempt=0
max_attempts=60   # 60 × 10s = 10 minutes
while [ $attempt -lt $max_attempts ]; do
    STATUS=$(docker inspect --format='{{.State.Health.Status}}' smart-discharge-iris 2>/dev/null)
    if [ "$STATUS" = "healthy" ]; then
        echo "✅ IRIS is healthy!"
        break
    fi
    attempt=$((attempt + 1))
    echo "   IRIS status: ${STATUS:-starting} ... ($attempt/$max_attempts)"
    sleep 10
done

if [ $attempt -eq $max_attempts ]; then
    echo "❌ Timeout waiting for IRIS. Check logs with: docker-compose logs iris"
    exit 1
fi

# ─── Install FHIR R4 endpoint (idempotent) ───────────────────────────────────
echo ""
echo "🔬 Checking FHIR R4 endpoint..."

# Quick check: does the endpoint already exist?
ENDPOINT_CHECK=$(docker exec smart-discharge-iris bash -c \
    "printf 'write ##class(HS.FHIRServer.ServiceAdmin).EndpointExists(\"/fhir/r4\"),!\nhalt\n' | iris session IRIS -U HSSYS 2>/dev/null" \
    2>/dev/null | grep -E '^[01]$' | tail -1)

if [ "$ENDPOINT_CHECK" = "1" ]; then
    echo "✅ FHIR R4 endpoint already installed — skipping installation."
else
    echo "📦 Installing FHIR R4 endpoint (this takes 3–8 minutes, please wait)..."
    echo "   Installing hl7.fhir.r4.core@4.0.1 into InterSystems IRIS..."

    SCRIPT_SRC="config/iris/install_fhir.txt"
    if [ ! -f "$SCRIPT_SRC" ]; then
        echo "❌ Installation script not found: $SCRIPT_SRC"
        echo "   Make sure you are running this script from the repository root."
        exit 1
    fi

    docker cp "$SCRIPT_SRC" smart-discharge-iris:/tmp/install_fhir.txt
    INSTALL_OUTPUT=$(docker exec -i smart-discharge-iris bash -c \
        'iris session IRIS -U HSSYS < /tmp/install_fhir.txt 2>&1')

    # Check for success
    if echo "$INSTALL_OUTPUT" | grep -q "EndpointExists:1"; then
        echo "✅ FHIR R4 endpoint installed successfully!"
    else
        echo "❌ FHIR endpoint installation may have failed. Last output:"
        echo "$INSTALL_OUTPUT" | tail -20
        echo ""
        echo "   Try running manually:"
        echo "   docker cp config/iris/install_fhir.txt smart-discharge-iris:/tmp/install_fhir.txt"
        echo "   docker exec -i smart-discharge-iris bash -c 'iris session IRIS -U HSSYS < /tmp/install_fhir.txt'"
        exit 1
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

# ─── Load sample data (optional) ─────────────────────────────────────────────
echo ""
echo "📊 Do you want to load sample patient data? (8 synthetic patients) [y/N]"
read -r LOAD_DATA
if [ "$LOAD_DATA" = "y" ] || [ "$LOAD_DATA" = "Y" ]; then
    if command -v python3 &> /dev/null; then
        echo "   Loading sample data..."
        python3 data/load_sample_data.py
    else
        echo "⚠️  python3 not found. Load data manually:"
        echo "   pip install requests && python3 data/load_sample_data.py"
    fi
fi

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
    echo "❌ Error: docker-compose is not installed. Please install it and try again."
    exit 1
fi

echo "✅ docker-compose is installed"
echo ""

# Check for .env file
if [ ! -f .env ]; then
    echo "⚠️  No .env file found. Creating from .env.example..."
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "   Created .env from .env.example"
        echo "   Edit .env to add your OPENAI_API_KEY for AI features."
    else
        echo "   No .env.example found either. Proceeding with defaults."
    fi
    echo ""
fi

# Check for OpenAI API Key
if [ -z "$OPENAI_API_KEY" ]; then
    # Try loading from .env file
    if [ -f .env ]; then
        source .env 2>/dev/null
    fi
fi

if [ -z "$OPENAI_API_KEY" ] || [ "$OPENAI_API_KEY" = "sk-your-openai-api-key-here" ]; then
    echo "⚠️  OPENAI_API_KEY is not set or is a placeholder."
    echo "   The system will run in RULE-BASED FALLBACK MODE."
    echo "   To enable AI Agent features:"
    echo "     1. Get an API key at https://platform.openai.com/api-keys"
    echo "     2. Set it in your .env file: OPENAI_API_KEY=sk-your-key-here"
    echo "     3. Or export it: export OPENAI_API_KEY=sk-your-key-here"
    echo ""
    echo "   All core features work without AI — you'll just miss:"
    echo "   • AI Clinical Chat"
    echo "   • AI-powered risk analysis"
    echo "   • AI discharge plan generation"
    echo "   • Multi-patient AI comparison"
    echo ""
else
    echo "✅ OPENAI_API_KEY is configured — AI Agent features enabled!"
    echo ""
fi

# Start services
echo "🚀 Starting services..."
docker-compose up -d

echo ""
echo "⏳ Waiting for services to be ready..."
echo "   (This may take 60-90 seconds for IRIS to fully initialize)"
echo ""

# Wait for backend to be healthy
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

# Check AI status
echo ""
echo "🤖 Checking AI Agent status..."
AI_STATUS=$(curl -s http://localhost:8000/api/v1/ai/status 2>/dev/null)
if echo "$AI_STATUS" | grep -q '"ai_available":true'; then
    echo "✅ AI Agent is ACTIVE (GPT-4o ready)"
else
    echo "⚠️  AI Agent is in FALLBACK MODE (rule-based only)"
    echo "   Set OPENAI_API_KEY to enable AI features."
fi

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
echo "   IRIS Portal:      http://localhost:52773/csp/sys/UtilHome.csp"
echo "                     (Username: SuperUser, Password: SYS)"
echo ""
echo "📁 Next steps:"
echo "   1. Load sample data:"
echo "      python3 data/load_sample_data.py"
echo ""
echo "   2. Open the application:"
echo "      http://localhost:3000"
echo ""
echo "   3. Try the AI Chat:"
echo "      Click '🤖 AI Chat' tab and ask about a patient"
echo ""
echo "   4. View logs:"
echo "      docker-compose logs -f"
echo ""
echo "   5. Stop services:"
echo "      docker-compose down"
echo ""
echo "======================================"
