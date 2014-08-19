#!/bin/bash
#
# pulls stderr logs for job dag
#

jobId=${1:?bad or missing emr job id}
for s in $(s3cmd ls s3://vrv-data-log-debug/${jobId}/steps/* | awk '{print $NF;}'); 
do 
	for f in $(s3cmd ls ${s}* | awk '$NF ~ /stderr/ {print $NF;}'); 
	do 
		lfn=$(echo $f | perl -ne 'print "${jobId}.$2.$1\n" if m/steps\/(\d+)\/(\w+)$/;'); 
		s3cmd get $f $lfn; 
	done; 
done
