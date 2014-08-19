#!/bin/bash
#
# pulls emr job logs 
#

bucket="vrv-data-log-debug"
jobId=${1:?bad or missing emr job id}
logType=${2:?bad or missing log type}
case ${logType} in
	controller|stderr)
		for s in $(s3cmd ls s3://${bucket}/${jobId}/steps/* | awk '{print $NF;}'); 
		do 
			echo "pulling logs from ${s}"
			for f in $(s3cmd ls ${s}* | awk -v logType="${logType}$" '$NF ~ logType {print $NF;}'); 
			do 
				lfn="${jobId}."$(echo $f | perl -ne 'print "$2.$1\n" if m/steps\/(\d+)\/(\w+)$/;'); 
				s3cmd get $f ${lfn}; 
			done; 
		done
	;;
	job)
		for f in $(s3cmd ls s3://${bucket}/${jobId}/jobs/* | awk '$NF ~ /job_/ && $NF !~ /.xml$/ {print $NF;}'); 
		do
			lfn="${jobId}.$(basename $f)"
			s3cmd get $f ${lfn};
		done
	;;
	*)
		echo "bad or missing log type" >&2
	;;
esac
