#!/bin/bash
#
# runs the avro tool
#
OPTS="d"
debug=
while getopts ${OPTS} opt
do
	case ${opt} in
		d)
			debug=1
		;;
	esac
done
shift $((OPTIND - 1))

CLASSPATH=${HOME}
HADOOP_HOME=${HADOOP_HOME:-/opt/hadoop}
libDir=${HOME}/lib
for j in $(find ${libDir} -follow -name "avro*.jar") $(find ${HADOOP_HOME} -follow -name "*.jar")
do
	[[ ${CLASSPATH} =~ $(basename ${j}) ]] && continue
	[[ $j =~ avro-tools.*jar$ ]] && jarFile=${j}
	CLASSPATH="${CLASSPATH}:${j}"
done
export CLASSPATH
# make each file spec a URI, if not already
args=$1
shift
while [ ! -z "$1" ]
do
	fn=$1
	if [[ ! $fn =~ ^[[:alnum:]]+: ]]
	then
		[[ $fn =~ ^\/ ]] || fn="${PWD}/${fn}"
		fn="file://${fn}"
	fi
	args="$args ${fn}"
	shift
done
[ -z "${debug}" ] || echo ${CLASSPATH} >&2
java org.apache.avro.tool.Main $args
