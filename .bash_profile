#!/bin/bash
#==============================================================================
#    File: ~/.bash_profile
#  Author: Nick Laws
#
# Description: Loads for all login shells. Sets path variable and others
#    Set up for REopt API development on Mac OS. After defining XPRESSDIR
#    and SRC_DIR, copy this file to your $HOME (~) directory:
#        cp bash_profile ~/.bash_profile
#    Note: the environment variables are not set until a new terminal session
#    is opened. And if you already have a ~/.bash_profile defined, add the
#    path definitions and exports below to your file.
#==============================================================================

# Source global definitions
if [ -f ~/.bashrc ]; then
  source ~/.bashrc
fi

#------------------------------------------------------------------------------
#  Define the following based on your file structure
#------------------------------------------------------------------------------
#  xpress path
XPRESSDIR="/usr/local/opt/xpress"

#  path to reopt_api/reo/src for SAM SDK C libraries
SRC_DIR="/Users/tkwasnik/github/reopt_api/reo/src"
APP_ENV=local
. /opt/xpressmp/bin/xpvars.sh
#==============================================================================

#------------------------------------------------------------------------------
#  Leave the following unchanged
#------------------------------------------------------------------------------
DYLD_LIBRARY_PATH="${XPRESSDIR}/lib:${SRC_DIR}:${DYLD_LIBRARY_PATH}"
PATH="${XPRESSDIR}/bin:${PATH}"
CLASSPATH="${XPRESSDIR}/lib/xprs.jar:${XPRESSDIR}/lib/xprb.jar:${XPRESSDIR}/lib/xprm.jar:${CLASSPATH}"

export XPRESS="$XPRESSDIR/bin"
export PATH
export DYLD_LIBRARY_PATH
export CLASSPATH
export APP_ENV="local"

#==============================================================================
