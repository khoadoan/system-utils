#!/bin/bash
. BashLib.sh || exit 1
. HadoopLib.sh || exit 1

ipList=$(getSlaves)

for ip in ${ipList}
do
	echo "${ipList}"
done
