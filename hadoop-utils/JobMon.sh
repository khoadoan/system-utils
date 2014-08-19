#!/bin/bash

function ExitFunc
{
	rm -f ${curFile} ${newFile}
	exit 0
}

function getJobId
{
	hadoop job -list | awk '$1 ~ /^job/ {print $1;}'
}

trap ExitFunc 0 2 15

OPTS="v"
while getopts ${OPTS} opt
do
	case ${opt} in
		v)
			verbose=1
		;;
	esac
done
shift $((OPTIND - 1))

jobId=${1:-$(getJobId)}
wrkDir=${wrkDir:-/var/tmp}

curFile=${wrkDir}/js.$$.cur
newFile=${wrkDir}/js.$$.new
while [ 1 ]
do
	echo "----- $(date)"
	if [ -z "${jobId}" ]
	then
		jobId=$(getJobId)
	else
		echo "JOB: ${jobId}"
		if [ ! -z "${verbose}" ]
		then
			hadoop job -status ${jobId} >${newFile}
			[ -f ${curFile} ] && diff ${curFile} ${newFile} | perl -ne 'next if !m/^>/; s/^>\s+//; print $_;'
			mv ${newFile} ${curFile}
		else
			hadoop job -status ${jobId} | perl -ne 'if(m/completion:|records=/) { s/^\s+//g; print $_; } elsif(m/^\tverve/) { $main::verveStats = 1; } elsif($main::verveStats && m/^\t{2}/) { s/^\s+//g; print "verve-metrics.$_"; } else { $main::verveStats = 0; }'
		fi
	fi
	sleep 10
done
