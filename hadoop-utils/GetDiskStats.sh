#!/bin/bash
BASEDIR=$(dirname $0)
[[ ${BASEDIR} =~ ^/ ]] || BASEDIR=${PWD}/${BASEDIR}
date +"START: %Y%m%d-%H:%M:%S %s"
hadoop dfsadmin -report | awk '{print $0;} $0 ~ /^-/ {exit;}'
[[ ${PATH} =~ ${BASEDIR} ]] || export PATH=${BASEDIR}:${PATH}
dist-exec.sh "df | awk '{print \$1, \$3, \$5}'"
