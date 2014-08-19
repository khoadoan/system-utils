#!/bin/bash
#
# backup script for Hadoop Namenode
#

. BashLib.sh || exit 1

function LocalExitFunc
{
	if [ -z "${DEBUG}" ]
	then
		rm -f ${imgFile}
		rm -f ${editsFile}
		rm -f ${tarFile}
	else
		logMsg "DEBUG set...no cleanup"
	fi
}

OPTS="c:d"
while getopts ${OPTS} opt
do
	case ${opt} in
		c)
			. ${OPTARG} || exit 1
		;;
		d)
			DEBUG=1
		;;
	esac
done
shift $((OPTIND - 1))

id=${id:-$(hostname)}
id=${id%%.*}
imgUrl=${imgUrl:-http://localhost:9101/getimage?getimage=1}
editsUrl=${imgUrl:-http://localhost:9101/getimage?getedit=1}
curDate=$(date +%Y%m%d)
wrkDir=${wrkDir:-/var/tmp}
tgtDir=${tgtDir:?bad or missing tgtDir}

# snapshot the image
imgFile="${wrkDir}/image.${id}.${curDate}.gz"
logMsg "backup image from ${imgUrl} to ${imgFile}"
curl -o - "${imgUrl}" | gzip -c >${imgFile}
if [ $? -ne 0 -o ! -s ${imgFile} ]
then
	logErr "image backup failed"
	exit 1
fi
# snapshot the edits
editsFile="${wrkDir}/edits.${id}.${curDate}.gz"
logMsg "backup edits from ${editsUrl} to ${editsFile}"
curl -o - "${editsUrl}" | gzip -c >${editsFile}
if [ $? -ne 0 -o ! -s ${editsFile} ]
then
	logErr "edits backup failed"
	exit 1
fi
# tarball 
tarFile="${wrkDir}/${id}.namenode-backup.${curDate}.tar"
tar cf ${tarFile} ${imgFile} ${editsFile}
# transfer to s3
logMsg "transferring ${tarFile} to ${tgtDir}"
if [ "${tgtDir#s3://}" = "${tgtDir}" ]
then
	# assume linux fs
	mv ${tarFile} ${tgtDir}
	rc=$?
else
	# use s3cmd
	s3cmd put ${tarFile} ${tgtDir}/$(basename ${tarFile})
	rc=$?
fi
if [ $rc -ne 0 ]
then
	logErr "transfer failed"
	exit 1
fi
