#!/bin/bash
BASEDIR=$(dirname $0)
[ ${BASEDIR} != "." ] || BASEDIR=${PWD}

OPTS="c:o:s:"
while getopts ${OPTS} opt
do
	case ${opt} in
		c)
			. ${OPTARG} || exit 1
		;;
		o)
			for tuple in ${OPTARG//,/ }
			do
				echo "setting ${tuple}"
				eval "${tuple}"
			done
		;;
		s)
			subTuples=${OPTARG}
		;;
	esac
done
shift $((OPTIND - 1))

srcDir=${srcDir:?bad or missing srcDir}
# cover cases where there are multiple source directories
srcDir=${srcDir// /\" -input \"}
tgtDir=${tgtDir:?bad or missing tgtDir}
genOpts="${genOpts} -conf ${BASEDIR}/../cfg/jobconf.xml"
numReducers=${numReducers:-0}
logFile=${logFile:-RunStream.$(date +%Y%m%d).log}

# runtime substitutions
# NOTE:  procDate is assumed to be of form yyyy-mm-dd or defaults to today
procDate=${procDate:-$(date +%Y-%m-%d)}
srcDir=${srcDir//<PROCDATE>/${procDate//-/}}
tgtDir=${tgtDir//<PROCDATE>/${procDate//-/}}
srcDir=${srcDir//<PROC-DATE>/${procDate}}
tgtDir=${tgtDir//<PROC-DATE>/${procDate}}
logFile=${logFile//<PROCDATE>/${procDate//-/}}
for tuple in ${subTuples//,/ }
do
	# upper case the lhs
	typeset -u lhs=${tuple%=*}
	rhs=${tuple#*=}
	if [ ! -z "${lhs}" -a ! -z "${rhs}" ]
	then
		srcDir=${srcDir//<${lhs}>/${rhs}}
		tgtDir=${tgtDir//<${lhs}>/${rhs}}
		mapper=${mapper//<${lhs}>/${rhs}}
		reducer=${reducer//<${lhs}>/${rhs}}
		logFile=${logFile//<${lhs}>/${rhs}}
	fi
done

# redirect stdout/err to ${logFile}
echo "redirecting output to ${logFile}"
exec 1>>${logFile}
exec 2>>${logFile}

cmd="hadoop jar ${HOME}/.versions/1.0.3/share/hadoop/contrib/streaming/hadoop-streaming.jar ${genOpts} -output \"${tgtDir}\" -input \"${srcDir}\" ${jobOpts}"

if [ ! -z "${mapper}" ]
then
	if [ "${mapper%%.*}" = "org" -o "${mapper%%.*}" = "com" ]
	then
		#cmd="${cmd} -mapper \"${mapper%% *}\" ${mapper#* }"
		cmd="${cmd} -mapper ${mapper}"
	elif [ -x "${mapper%% *}" ]
	then
		exec=${mapper%% *}
		[ $(dirname $exec) = "/usr/bin" ] || [ $(dirname $exec) = "/bin" ] || distFiles="${distFiles} ${exec}"
		cmd="${cmd} -mapper \"${mapper}\""
	else
		echo "bad or missing mapper, ${mapper%% *}"
		exit 1
	fi
fi
if [ ! -z "${reducer}" ]
then
	if [ "${reducer%%.*}" = "org" ]
	then
		cmd="${cmd} -reducer \"${reducer}\" -numReduceTasks ${numReducers}"
	elif [ -x "${reducer%% *}" ]
	then
		exec=${reducer%% *}
		[ $(dirname $exec) = "/usr/bin" ] || [ $(dirname $exec) = "/bin" ] || distFiles="${distFiles} ${exec}"
		cmd="${cmd} -reducer \"${reducer}\" -numReduceTasks ${numReducers}"
	else
		echo "bad or missing reducer"
		exit 1
	fi
else
	cmd="${cmd} -numReduceTasks 0"
fi

# distribute any additionally specified files
if [ ! -z "${distFiles}" ]
then
	${BASEDIR}/dist-cp.sh ${distFiles//${BASEDIR}/${PWD}} || exit 1
fi

# see if pre-processing is configured
if typeset -F preproc 
then
	echo "executing preproc"
	preproc || exit 1
fi

hadoop dfs -rmr ${tgtDir}
echo "running: ${cmd}"
eval "${cmd}" || exit 1

# grab the job id from the logs and output the final status
jobId=$(perl -ne '$main::jobId = $1 if m/jobid=(job_\d+_\d+)/; END {print $main::jobId;}' ${logFile})
if [ ! -z "${jobId}" ]
then
	hadoop job -status ${jobId}
fi

# see if post-processing is configured
if typeset -F postproc
then
	echo "executing postproc"
	postproc || exit 1
fi
