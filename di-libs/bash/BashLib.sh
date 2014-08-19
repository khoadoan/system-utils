#!/bin/bash
#
# library of 'common' functionality for scirpts
#

BASEDIR=${BASEDIR:-$(dirname $0)}
# make sure BASEDIR is absolute
[[ $BASEDIR =~ ^/ ]] || BASEDIR="${PWD}/${BASEDIR}"
SEND_NSCA=/usr/sbin/send_nsca
NOTIFY=
SUBJECT="$(basename $0) - $(hostname)"
ERRFILE="${EXTERRFILE:-/var/tmp/$$.err}"
# set the default lock threshold to 4 hours
LOCKTHRESHOLD=$((3600 * 4))
# defines whether a stale lock file is cleared or kept in place
AUTORESTART=0
LOCKFILE=
# remove any residual files...providing they belong to us
[ "${EXTERRFILE}" = "${ERRFILE}" ] || rm -f ${ERRFILE}

trap ExitFunc 0 2 15

function logMsg
{
	ts=$(date +"%Y%m%d-%H%M%S")
	echo "${ts}:$*" >&2
}

function logWarn
{
	logMsg "WARNING:$*"
}

function logErr
{
	logMsg "ERROR:$*" 2>&1 | tee -a ${ERRFILE} >&2
	if [ ! -z "${NAGIOS_SVC}" ]
	then
		echo "$(hostname);${NAGIOS_SVC};1;$*" | ${SEND_NSCA} -H localhost -d ";" >/dev/null 2>&1
	fi
}

function logCrit
{
	logMsg "CRIT:$*" 2>&1 | tee -a ${ERRFILE} >&2
	if [ ! -z "${NAGIOS_SVC}" ]
	then
		echo "$(hostname);${NAGIOS_SVC};2;$*" | ${SEND_NSCA} -H localhost -d ";" >/dev/null 2>&1
	fi
}

function ExitFunc
{
	rc=$?
	[ -z "${DEBUG}" ] || logMsg "exiting..."
	typeset -F LocalExitFunc >/dev/null && LocalExitFunc ${rc}
	if [ -s "${ERRFILE}" ]
	then
		if [ ! -z "${NOTIFY}" ]
		then
			logWarn "issues detected, sending notification to ${NOTIFY}"
			# note...need to make sure \r is removed...ssh bug
			sed 's/\r//g;' ${ERRFILE} | mail -s "${SUBJECT}" ${NOTIFY}
		fi
	elif [ $rc -eq 0 -a ! -z "${NAGIOS_SVC}" ]
	then
		echo "$(hostname);${NAGIOS_SVC};0;ALL CLEAR" | ${SEND_NSCA} -H localhost -d ";" >/dev/null 2>&1
	fi
	# cleanup
	[ -z "${DEBUG}" -a "${EXTERRFILE}" != "${ERRFILE}" ] && rm -f ${ERRFILE}
	# exit...seems to be required in some cases...but don't re-execute this function
	trap "" 0
	[[ rc -eq 0 ]] && unlock
	logMsg "END(${rc}): $(basename $0)"
	exit ${rc}
}

function proceed
{
	# make sure we want to do this
	if [ ! -z "${SSH_TTY}" ]
	then
		read -p "Are you sure you want to proceed: " ans
		[ "${ans}" = "y" ] || return 1
	fi
}

function lock
{
	# make sure lockfile is set
	if [ -z "${LOCKFILE}" -o ! -f "${LOCKFILE}" -a ! -f "${LOCKFILE}.locked" ]
	then
		logMsg "LOCKFILE not defined or initialized"
		return 1
	fi
	# get the current pid just in case we have a stranded lock file
	filePid=$(cat ${LOCKFILE}.locked 2>/dev/null || echo "0")
	if [ -d /proc/${filePid} ]
	then
		# get the modify time
		lockTime=$(($(date +%s) - $(stat -c %Y ${LOCKFILE}.locked)))
		if [ ${lockTime} -gt ${LOCKTHRESHOLD} ]
		then
			logErr "lock held by ${filePid} for more than ${LOCKTHRESHOLD} secs"
		else
			logMsg "lock held by ${filePid}"
		fi
		return 1
	elif [[ ${filePid} -gt 0 ]]
	then
		if [[ ${AUTORESTART} == 1 ]]
		then
			# should be clear...move it back, but consider the race condition
			logMsg "stale lock file found...releasing"
			mv ${LOCKFILE}.locked ${LOCKFILE} 2>/dev/null || return 1
		else
			# get the modify time
			lockTime=$(($(date +%s) - $(stat -c %Y ${LOCKFILE}.locked)))
			if [ ${lockTime} -gt ${LOCKTHRESHOLD} ]
			then
				logErr "lock held by ${filePid} for more than ${LOCKTHRESHOLD} secs"
			else
				logMsg "lock held by ${filePid}"
			fi
			return 1
		fi
	fi
	# the move is atomic and only one process should ever succeed
	mv ${LOCKFILE} ${LOCKFILE}.locked 2>/dev/null
	if [ $? -ne 0 ]
	then
		logMsg "lock still enabled OR doesn't exist"
		return 1
	fi
	# its ours...save our pid
	echo $$ >${LOCKFILE}.locked
	logMsg "lock obtained"
}

function unlock
{
	filePid=$(cat ${LOCKFILE}.locked 2>/dev/null || echo "0")
	[ ${filePid} -eq $$ ] || return
	mv ${LOCKFILE}.locked ${LOCKFILE} 2>/dev/null
	logMsg "lock released"
}

logMsg "START: $(basename $0)"
