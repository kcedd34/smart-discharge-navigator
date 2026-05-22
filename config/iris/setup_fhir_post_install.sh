#!/bin/bash
# =============================================================================
# setup_fhir_post_install.sh
#
# Run INSIDE the smart-discharge-iris container after the FHIR endpoint is
# installed.  This script handles the two post-install steps that are required
# on every fresh container start:
#
#   1. Add /fhir to the CSP gateway routing table (CSP.ini)
#   2. Restart the embedded httpd so it picks up the new routing
#   3. Fix SuperUser authentication (must have AutheEnabled=64 + password set)
#   4. Fix the /fhir/r4 CSP application authentication (AutheEnabled=96)
#
# Usage (called from start.sh / CI):
#   docker exec smart-discharge-iris bash /tmp/setup_fhir_post_install.sh
# =============================================================================

set -e

CSP_INI="/usr/irissys/csp/bin/CSP.ini"

# ── 1. CSP Gateway: add /fhir path ──────────────────────────────────────────
echo ">>> Step 1: Updating CSP gateway routing..."

if grep -q "^/fhir=Enabled" "$CSP_INI"; then
    echo "    /fhir already present in CSP.ini — skipping."
else
    # Insert /fhir=Enabled after the /csp=Enabled line in APP_PATH_INDEX
    sed -i 's|/csp=Enabled|/csp=Enabled\n/fhir=Enabled|' "$CSP_INI"

    # Append the APP_PATH:/fhir section at the end of the file
    cat >> "$CSP_INI" << 'INIEOF'

[APP_PATH:/fhir]
Default_Server=LOCAL
Alternative_Server_0=1~~~~~~LOCAL
INIEOF

    echo "    /fhir path added to CSP.ini."
fi

# ── 2. Restart httpd ─────────────────────────────────────────────────────────
echo ">>> Step 2: Reloading/restarting httpd..."

HTTPD_PID_FILE="/usr/irissys/httpd/logs/httpd.pid"
HTTPD_BIN="/usr/irissys/httpd/bin/httpd"
HTTPD_CONF="/usr/irissys/httpd/conf/httpd.conf"
HTTPD_DIR="/usr/irissys/httpd"

if [ -f "$HTTPD_PID_FILE" ]; then
    HTTPD_PID=$(cat "$HTTPD_PID_FILE")
    if kill -0 "$HTTPD_PID" 2>/dev/null; then
        echo "    Sending HUP to httpd PID $HTTPD_PID for graceful reload..."
        kill -HUP "$HTTPD_PID"
        sleep 2
        echo "    httpd reloaded."
    else
        echo "    httpd PID $HTTPD_PID not running — doing full start..."
        "$HTTPD_BIN" -f "$HTTPD_CONF" -d "$HTTPD_DIR" -c "Listen 52773"
        sleep 2
        echo "    httpd started."
    fi
else
    echo "    No PID file found — starting httpd..."
    "$HTTPD_BIN" -f "$HTTPD_CONF" -d "$HTTPD_DIR" -c "Listen 52773"
    sleep 2
    echo "    httpd started."
fi

# ── 3. Fix SuperUser authentication ──────────────────────────────────────────
echo ">>> Step 3: Configuring SuperUser authentication..."

printf 'set sc=##class(Security.Users).Get("SuperUser",.p)\nset p2("AutheEnabled")=64\nset p2("Password")="SYS"\nset sc2=##class(Security.Users).Modify("SuperUser",.p2)\nwrite "SuperUser AutheEnabled=64 sc=",sc2,!\nhalt\n' \
    | iris session IRIS -U %SYS 2>/dev/null | grep -v "^$" | grep -v "^%SYS"

# ── 4. Fix FHIR app authentication ───────────────────────────────────────────
echo ">>> Step 4: Configuring /fhir/r4 CSP application authentication..."

printf 'set mods("AutheEnabled")=96\nset sc=##class(Security.Applications).Modify("/fhir/r4",.mods)\nwrite "FHIR app AutheEnabled=96 sc=",sc,!\nhalt\n' \
    | iris session IRIS -U %SYS 2>/dev/null | grep -v "^$" | grep -v "^%SYS"

echo ""
echo ">>> Post-install setup complete."
echo "    Test: curl http://localhost:52773/fhir/r4/metadata"
