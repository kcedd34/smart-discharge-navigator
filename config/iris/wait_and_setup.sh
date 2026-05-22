#!/bin/bash
set -e

echo "=== Waiting for IRIS to become healthy ==="
for i in $(seq 1 30); do
  STATUS=$(docker inspect --format='{{.State.Health.Status}}' smart-discharge-iris 2>/dev/null || echo "unknown")
  echo "  [$i/30] IRIS Status: $STATUS"
  if [ "$STATUS" = "healthy" ]; then
    echo "IRIS is healthy! Proceeding with FHIR setup..."
    break
  fi
  if [ $i -eq 30 ]; then
    echo "ERROR: IRIS did not become healthy in time"
    exit 1
  fi
  sleep 10
done

echo ""
echo "=== Checking if FHIR package is already loaded ==="
LOADED=$(docker exec smart-discharge-iris iris session IRIS -U HSSYS < /tmp/check_pkg.txt 2>&1 | grep -E '^[01]$' | head -1 || echo "0")
echo "Package loaded: $LOADED"

if [ "$LOADED" != "1" ]; then
  echo "=== Loading FHIR R4 package ==="
  docker exec smart-discharge-iris iris session IRIS -U HSSYS < /tmp/import_pkg.txt 2>&1
  echo "Package import complete"
fi

echo ""
echo "=== Installing FHIR endpoint ==="
docker exec smart-discharge-iris iris session IRIS -U HSSYS < /tmp/install_fhir.txt 2>&1
echo "FHIR install complete"

echo ""
echo "=== Verifying FHIR endpoint ==="
sleep 5
curl -s -u SuperUser:SYS http://localhost:52773/fhir/r4/metadata 2>&1 | head -5 || echo "curl test failed"
