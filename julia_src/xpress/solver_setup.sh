#!/bin/bash

# Instructions for setting up the solver
# The $LICENSESERVER and $TRANSCRYPT_PASSWORD environment variables must be assigned or replaced
git clone $LICENSESERVER_URL
cd licenseserver
# Only need transcrypt for local testing
transcrypt/transcrypt --flush-credentials -y || true
transcrypt/transcrypt -c aes-256-cbc -p "$TRANSCRYPT_PASSWORD" -y
# Needed for deploys to NREL servers
cp Dockerfile.xpress ../..
# Only need for local testing
cp docker-compose.xpress.yml ../../..
