write "=== GetEndpointList source ===",!
set m = ##class(%Dictionary.CompiledMethod).%OpenId("HS.FHIRServer.ServiceAdmin||GetEndpointList")
set impl = m.Implementation
write impl.Read(503),!
write "=== EndpointExists source ===",!
set m2 = ##class(%Dictionary.CompiledMethod).%OpenId("HS.FHIRServer.ServiceAdmin||EndpointExists")
set impl2 = m2.Implementation
write impl2.Read(1000),!
halt
