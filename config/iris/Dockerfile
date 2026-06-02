# Custom InterSystems IRIS for Health image
# Bakes FHIR R4 installation into the image at BUILD TIME.
#
# Why: The previous approach installed FHIR at container startup via start.sh,
# which caused a race condition — HS.Util.Installer.Foundation creates the
# FHIRSERVER namespace via background jobs, and the FHIR installer was called
# before those jobs completed, leading to "namespace not ready" failures.
#
# This Dockerfile runs the full FHIR setup during `docker build`, so the
# resulting image already has the FHIR endpoint configured. The iris-data
# volume is initialised from this pre-configured image on first run.

ARG IRIS_IMAGE=intersystemsdc/irishealth-community:latest
FROM $IRIS_IMAGE

LABEL maintainer="Carlos Eduardo Dias Duarte <kcedd34@gmail.com>"
LABEL description="Smart Discharge Navigator — IRIS for Health with FHIR R4 pre-installed"

USER irisowner

# Copy setup scripts (build context = project root)
COPY --chown=irisowner:irisowner config/iris/install_fhir.txt /tmp/install_fhir.txt
COPY --chown=irisowner:irisowner config/iris/setup_fhir_post_install.sh /tmp/setup_fhir_post_install.sh

# Run FHIR installation during the Docker build.
# Steps:
#   1. Start IRIS
#   2. Install FHIRSERVER namespace + FHIR R4 endpoint (install_fhir.txt)
#   3. Configure CSP gateway routing for /fhir (setup_fhir_post_install.sh)
#   4. Stop IRIS cleanly — database state is saved into the image layer
#
# The iris-data volume (defined in docker-compose.yml) is populated from this
# layer on first `docker-compose up`, so FHIR is available immediately with
# no extra setup steps.
RUN iris start IRIS && \
    iris session IRIS -U %SYS < /tmp/install_fhir.txt && \
    bash /tmp/setup_fhir_post_install.sh && \
    iris stop IRIS quietly

EXPOSE 52773 1972
