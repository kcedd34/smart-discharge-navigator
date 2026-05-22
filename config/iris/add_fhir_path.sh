#!/bin/bash
# Append /fhir path to CSP.ini
CSP_INI="/usr/irissys/csp/bin/CSP.ini"

# Add /fhir to APP_PATH_INDEX
sed -i 's|/csp=Enabled|/csp=Enabled\n/fhir=Enabled|' "$CSP_INI"

# Add the APP_PATH:/fhir section
cat >> "$CSP_INI" << 'EOF'

[APP_PATH:/fhir]
Default_Server=LOCAL
Alternative_Server_0=1~~~~~~LOCAL
EOF

echo "Updated CSP.ini:"
cat "$CSP_INI"
