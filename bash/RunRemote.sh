#!/bin/bash
#
# generic bash script for remote execution
#
. BashLib.sh || exit 1

OPTS="c:o:"
while getopts ${OPTS} opt
do
	case ${opt} in
		c)
			. ${OPTARG} || exit 1
		;;
		o)
			for tuple in ${OPTARG//,/ }
			do
				logMsg "setting ${tuple}"
				eval "${tuple}"
			done
		;;
	esac
done
shift $((OPTIND - 1))

# locking is optional, as it may be handled on the other end
[ -z "${LOCKFILE}" ] || lock || exit 1

# assume we're managing host configs via ssh-config
sshHost=${sshHost:?bad or missing host}
remCmd=${remCmd:?bad or missing remote command}

# see if there's something we need to do prior to processing
if [ "$(typeset -F preProc)" = "preProc" ]
then
	preProc
elif [ ! -z "${preProc}" ]
then
	eval "${preProc}"
fi
if [ $? -ne 0 ]
then
	logErr "preproc failed"
	exit 1
fi

# execute...use eval to resolve any last minute variables
eval "ssh ${sshHost} \"${remCmd}\""
if [ $? -ne 0 ]
then
	logErr "failed to execute: ${remCmd}"
	exit 1
fi

# see if there's something we need to do afterwards
if [ "$(typeset -F postProc)" = "postProc" ]
then
	postProc
elif [ ! -z "${postProc}" ]
then
	eval "${postProc}"
fi
if [ $? -ne 0 ]
then
	logErr "postproc failed"
	exit 1
fi
