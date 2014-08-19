#!/bin/bash
. BashLib.sh || exit 1
. HadoopLib.sh || exit 1

jobId=${1:?bad or missing job id}
if [[ $jobId =~ ^task ]]
then
	taskId=${jobId}
	jobId=${taskId/task/job}
	jobId=${jobId/_[mr]_[0-9]*/}	
	logMsg "jobId: ${jobId}"
	logMsg "taskId: ${taskId}"
fi
srcDir=/mnt/var/log/hadoop/userlogs
tgtDir=/var/tmp/${jobId}

if [ -d ${tgtDir} ]
then
	rm -fr ${tgtDir}/*
else
	mkdir ${tgtDir}
fi

# set the target directory if it's not specified 
keyFile=${HOME}/.ssh/verve-shared.pem

for ip in $(getSlaves)
do
	mkdir -p ${tgtDir}/${ip}
	if [ -z "${taskId}" ]
	then
		# get all attempts
		scp -o StrictHostKeyChecking=false -i ${keyFile} -r ${ip}:${srcDir}/${jobId} ${tgtDir}/${ip} 2>/dev/null
	else
		# get only attempts for specified task
		scp -o StrictHostKeyChecking=false -i ${keyFile} -r ${ip}:${srcDir}/${jobId}/${taskId/task/attempt}* ${tgtDir}/${ip} 2>/dev/null
	fi
done
read -p "view logs [y - all, 1 - syslog, 2 - stderr]: " ans
case ${ans} in
	y)
		find ${tgtDir} -type f -exec cat {} \; | less -X
	;;
	1)
		for f in $(find ${tgtDir} -name "syslog")
		do
			echo ${f}
			cat ${f}
		done | less -X
	;;
	2)
		for f in $(find ${tgtDir} -name "stderr")
		do
			echo ${f}
			cat ${f}
		done | less -X
	;;
	*)
		logMsg "log collected to ${tgtDir}"
	;;
esac
