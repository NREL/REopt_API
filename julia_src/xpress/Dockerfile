FROM ubuntu:latest
# For creating base image of Julia API. Requires an untracked tar.gz file for FICO Xpress
# Used in both production and local development

WORKDIR /opt/reopt/solver
COPY xp8.12.3_linux_x86_64.tar.gz .
COPY install.sh .
