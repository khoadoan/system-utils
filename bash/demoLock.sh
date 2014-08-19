#!/bin/bash
. ./BashLib.sh || exit 1

LOCKFILE=LOCK.demoLock
LOCKTHRESHOLD=5

lock
if [ $? -ne 0 ]
then
	logMsg "could not obtain lock"
	exit 0
fi
logMsg "locked and running"
sleep 10
