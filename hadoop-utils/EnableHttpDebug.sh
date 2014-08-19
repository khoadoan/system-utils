#!/bin/bash
#
# initial script provided by aws...added some additional failsafes
#
. BashLib.sh || exit 1

confFile=${1:-${HOME}/conf/log4j.properties}
backupFile=$(dirname ${confFile})/$(basename ${confFile}).$(date +%Y%m%d-%H%M%S)

# make sure we should proceed
proceed || exit 0

# backup the existing file
logMsg "backing up ${confFile} to ${backupFile}"
cp ${confFile} ${backupFile}

# code provided by AWS
set -e -x
logMsg "Enabling log4j for more http and aws debug logging"
perl -p -i -e 's/^(log4j\.logger\.com\.amazonaws.*)$/#Bootstrap action to add additional http and aws debugging\n#$1\nlog4j.logger.com.amazonaws=DEBUG\nlog4j.logger.org.apache.http=DEBUG\nlog4j.logger.org.apache.http.wire=ERROR\n/g' ${confFile}
