#!/bin/bash
. BashLib.sh || exit 1
. HadoopLib.sh || exit 1

[ ! -z "${1}" ] || exit 0

ipList=
while [ ! -f ${1} -a ! -d ${1} ]
do
	ipList="${ipList} ${1}"
	shift
done
[ ! -z "${ipList}" ] || ipList=$(getSlaves)

# set the target directory if it's not specified 
keyFile=${HOME}/.ssh/verve-shared.pem
while [ -f "${1}" -o -d "${1}" ]
do
	srcFile=${1}
	tgtDir=$(dirname ${srcFile})
	[[ ${tgtDir} =~ ^/ ]] || tgtDir="${PWD}/${tgtDir}"

	logMsg "copying: ${srcFile} to ${tgtDir}"
	for ip in ${ipList}
	do
		logMsg "transfering to ${ip}"
		if [ -d ${srcFile} ]
		then
			scp -r -o StrictHostKeyChecking=false -i ${keyFile} ${srcFile} ${ip}:${tgtDir}
		else
			# make sure that the target directory exists
			ssh -o StrictHostKeyChecking=false -i ${keyFile} ${ip} "mkdir -p ${tgtDir}"
			scp -o StrictHostKeyChecking=false -i ${keyFile} ${srcFile} ${ip}:${tgtDir}
		fi
	[ $? -eq 0 ] || exit 1
	done
	shift
done
