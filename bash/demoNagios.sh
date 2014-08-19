#!/bin/bash
. BashLib.sh || exit 1
NAGIOS_SVC="check-test"

case "${1}" in
	ok)
		echo "$(hostname);${NAGIOS_SVC};0;all clear" | ${SEND_NSCA} -H localhost -d ";"
	;;
	err)
		logErr "an error has occured"
	;;
	crit)
		logCrit "shit has hit the fan"
	;;
	*)
	;;
esac
