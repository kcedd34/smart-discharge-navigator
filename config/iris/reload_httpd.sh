#!/bin/bash
PID=$(cat /usr/irissys/httpd/logs/httpd.pid 2>/dev/null)
if [ -z "$PID" ]; then
  PID=$(pgrep -f 'httpd' | head -1)
fi
echo "httpd PID: $PID"
if [ -n "$PID" ]; then
  kill -HUP $PID && echo "Reload signal sent"
else
  echo "No httpd PID found, trying restart"
  /usr/irissys/httpd/bin/apachectl restart || echo "restart failed"
fi
sleep 2
echo "Testing /fhir/r4/metadata..."
curl -s -o /dev/null -w "metadata=%{http_code}" http://localhost:52773/fhir/r4/metadata
