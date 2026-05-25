#!/bin/bash

# CSP Gateway & Authentication Configuration Script
# Required for HTTP access to /fhir/r4/* endpoints

echo "========================================="
echo "Configuring CSP Gateway for FHIR"
echo "========================================="

# Execute ObjectScript commands
iris session IRIS << 'EOF'

set $NAMESPACE = "%SYS"

write !,"1. Adding /fhir to CSP Gateway routing...",!
// Add CSP application mapping for /fhir path
set props("AuthenticationMethods") = 64  // Password authentication
set props("MatchRoles") = ":%All"
set props("NameSpace") = "FHIRSERVER"
set props("Enabled") = 1
set props("IsNameSpaceDefault") = 0
set props("Description") = "FHIR R4 Server Endpoint"
set props("ServeFiles") = 0
set props("ServeFilesTimeout") = 0
set props("UseSessionCookie") = 2
set props("RecurseTimeout") = 60
do ##class(Security.Applications).Create("/fhir", .props)
write "CSP application /fhir configured",!

write "2. Configuring SuperUser for HTTP auth...",!
// Ensure SuperUser has HTTP login enabled
set user = ##class(Security.Users).Open("SuperUser")
if $IsObject(user) {
    set user.AutheMethods = $ZBOOLEAN(user.AutheMethods, 64, 1)  // Enable Password
    do user.%Save()
    write "SuperUser HTTP authentication enabled",!
}

write "3. Restarting embedded HTTP server...",!
// Restart httpd to apply changes
do ##class(%SYS.HSDFHIR.Utils).RestartHTTPd()
write "HTTP server restarted",!

write !,"========================================",!
write "CSP Gateway Configuration Complete!",!
write "========================================",!
write "Test endpoint:",!
write "  curl http://localhost:52773/fhir/r4/metadata",!
write !

halt
EOF

echo ""
echo "✅ CSP Gateway configured successfully!"
echo ""
echo "🔗 Test FHIR endpoint:"
echo "   http://localhost:52773/fhir/r4/metadata"
echo ""
echo "🔐 Credentials:"
echo "   Username: SuperUser"
echo "   Password: SYS"
echo ""
