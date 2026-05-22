#!/bin/bash
# End-to-end test of all 17 API endpoints
BASE=http://localhost:8000/api/v1
PATIENT_ID=22  # Linda Smith (high risk patient)
PATIENT_ID2=63 # William Jones (moderate risk)

echo "============================================================"
echo "Smart Discharge Navigator - E2E Endpoint Tests"
echo "============================================================"
echo ""

test_endpoint() {
    local name="$1"
    local method="$2"
    local url="$3"
    local data="$4"
    local expected_key="$5"

    if [ "$method" = "POST" ]; then
        response=$(curl -s -X POST "$url" -H "Content-Type: application/json" -d "$data" 2>&1)
    else
        response=$(curl -s "$url" 2>&1)
    fi

    if echo "$response" | python3 -c "import json,sys; d=json.load(sys.stdin); sys.exit(0 if '$expected_key' in str(d) else 1)" 2>/dev/null; then
        echo "✅ $name"
    else
        echo "❌ $name"
        echo "   Response: ${response:0:200}"
    fi
}

# 1. Health check
test_endpoint "GET /health" GET "$BASE/health" "" "healthy"

# 2. AI Status
test_endpoint "GET /ai/status" GET "$BASE/ai/status" "" "ai_available"

# 3. List patients
test_endpoint "GET /patients" GET "$BASE/patients" "" "risk_level"

# 4. Patient detail
test_endpoint "GET /patients/{id}" GET "$BASE/patients/$PATIENT_ID" "" "Linda Smith"

# 5. Risk assessment
test_endpoint "GET /patients/{id}/risk-assessment" GET "$BASE/patients/$PATIENT_ID/risk-assessment" "" "risk_score"

# 6. Statistics
test_endpoint "GET /statistics" GET "$BASE/statistics" "" "total_patients"

# 7. AI Chat
test_endpoint "POST /ai/chat" POST "$BASE/ai/chat" '{"message": "What is the risk for patient 22?"}' "response"

# 8. AI Patient Analysis
test_endpoint "GET /patients/{id}/ai-analysis" GET "$BASE/patients/$PATIENT_ID/ai-analysis" "" "ai_risk_level"

# 9. AI Discharge Plan
test_endpoint "POST /patients/{id}/ai-discharge-plan" POST "$BASE/patients/$PATIENT_ID/ai-discharge-plan" '{}' "discharge_plan"

# 10. Non-AI Discharge Plan
test_endpoint "POST /patients/{id}/discharge-plan" POST "$BASE/patients/$PATIENT_ID/discharge-plan" '{}' "plan"

# 11. Compare Patients
test_endpoint "POST /ai/compare-patients" POST "$BASE/ai/compare-patients" "{\"patient_ids\": [\"$PATIENT_ID\", \"$PATIENT_ID2\"]}" "comparison_summary"

# 12. Analytics SQL Stats
test_endpoint "GET /analytics/sql-stats" GET "$BASE/analytics/sql-stats" "" "IRIS"

# 13. Analytics Readmission SQL
test_endpoint "GET /analytics/readmission-sql" GET "$BASE/analytics/readmission-sql" "" "queries"

# 14. Analytics SQL Builder Info
test_endpoint "GET /analytics/sql-builder-info" GET "$BASE/analytics/sql-builder-info" "" "FHIR SQL Builder"

# 15. Patient Summary (role-based)
test_endpoint "GET /patients/{id}/summary" GET "$BASE/patients/$PATIENT_ID/summary" "" "patient_id"

# 16. Patient Summary with role=nurse
test_endpoint "GET /patients/{id}/summary?role=nurse" GET "$BASE/patients/$PATIENT_ID/summary?role=nurse" "" "patient_id"

# 17. NL to SQL
test_endpoint "POST /ai/nl-to-sql" POST "$BASE/ai/nl-to-sql" '{"query": "How many patients have high risk?"}' "generated_sql"

echo ""
echo "============================================================"
echo "Tests complete!"
echo "============================================================"

# Show actual response of key endpoints for README verification
echo ""
echo "=== Actual response shapes for README verification ==="
echo ""
echo "--- GET /ai/status ---"
curl -s "$BASE/ai/status" | python3 -c "import json,sys; d=json.load(sys.stdin); print(json.dumps(d, indent=2))"

echo ""
echo "--- GET /patients (first patient keys) ---"
curl -s "$BASE/patients" | python3 -c "import json,sys; d=json.load(sys.stdin); print('List of', len(d), 'patients'); print('Keys:', list(d[0].keys()))"

echo ""
echo "--- POST /ai/chat response keys ---"
curl -s -X POST "$BASE/ai/chat" -H "Content-Type: application/json" -d '{"message": "Hello"}' | python3 -c "import json,sys; d=json.load(sys.stdin); print('Keys:', list(d.keys())); print('sources sample:', d.get('sources', d.get('fhir_sources', 'N/A'))[:1] if isinstance(d.get('sources', d.get('fhir_sources', [])), list) else 'no sources')"

echo ""
echo "--- POST /patients/{id}/ai-discharge-plan response keys ---"
curl -s -X POST "$BASE/patients/$PATIENT_ID/ai-discharge-plan" -H "Content-Type: application/json" -d '{}' | python3 -c "import json,sys; d=json.load(sys.stdin); print('Keys:', list(d.keys()))"

echo ""
echo "--- POST /ai/compare-patients response keys ---"
curl -s -X POST "$BASE/ai/compare-patients" -H "Content-Type: application/json" -d "{\"patient_ids\": [\"$PATIENT_ID\", \"$PATIENT_ID2\"]}" | python3 -c "import json,sys; d=json.load(sys.stdin); print('Keys:', list(d.keys()))"
