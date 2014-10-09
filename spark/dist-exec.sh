#!/bin/bash
. BashLib.sh || exit 1
. HadoopLib.sh || exit 1

[ ! -z "${1}" ] || exit 0

ipList=
while [ -z "$(which ${1})" ]
do
	ipList="${ipList} ${1}"
	shift
done
[ ! -z ${ipList} ] || ipList=$(getSlaves)

keyFile=${HOME}/.ssh/verve-shared.pem
logMsg "executing: $*"
for ip in ${ipList}
do
	logMsg "executing on ${ip}"
	ssh -o StrictHostKeyChecking=false -i ${keyFile} ${ip} "$@" &
done
